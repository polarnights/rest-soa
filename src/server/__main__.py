import json
import typing as tp
from hashlib import sha1
from pathlib import Path
from random import randint

import click
import pika
import uvicorn
from fastapi import FastAPI, File, HTTPException, Header, UploadFile
from fastapi.responses import Response, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from server.db_models.user import User, Sex, Base
from constants import default_avatar, avatar_folder, favicon, pdfs_folder


def setup(
    host: str, port: int,
    rabbitmq_host: str, rabbitmq_port: int, rabbitmq_queue: str
) -> None:
    app = FastAPI()

    engine = create_engine(
        f'sqlite+pysqlite:///'
        f'{str(Path(__file__).absolute().parent / "db/users.db")}',
        echo=True
    )
    Session = sessionmaker(
        bind=engine, expire_on_commit=False
    )
    Base.metadata.create_all(engine)

    class RegistrationInfo(BaseModel):
        username: str
        sex: tp.Literal["female", "male", "other"]

    @app.get("/")
    async def root() -> RedirectResponse:
        return RedirectResponse("/docs")

    @app.post("/users/register")
    async def add_user(info: RegistrationInfo) -> dict[str, str]:
        if info.username == "unknown_user":
            raise HTTPException(
                status_code=401,
                detail="It is forbidden username. Try another"
            )
        with Session() as session:
            q = select(User).where(User.username == info.username)
            content = session.execute(q).scalar()
            if content is not None:
                raise HTTPException(
                    status_code=401,
                    detail="User with this username already exists"
                )
            token = sha1(
                f'{info.username} {info.sex} {randint(0, 1000)}'
                .encode('utf-8')
            ).hexdigest()
            sex = Sex.female if info.sex == "female"\
                else Sex.male if info.sex == "male"\
                else Sex.other
            session.add(User(
                username=info.username,
                avatar_path=str(default_avatar),
                sex=sex,
                token=token
            ))
            session.commit()
        return {
            "token": token,
        }

    @app.get("/users/profiles/{username}")
    async def get_user(username: str) -> dict[str, str]:
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )
            sex = "male" if user.sex == Sex.male\
                else "female" if user.sex == Sex.female\
                else "other"
            return {
                "username": username,
                "sex": sex,
                "avatar": app.url_path_for(
                    "get_user_avatar", username=username
                )
            }

    @app.put("/users/profiles/{username}")
    async def edit_user(
        username: str,
        new_username: tp.Optional[str], new_sex: tp.Optional[str],
        token: tp.Optional[str] = Header(None)
    ) -> dict[str, str]:
        if token is None:
            raise HTTPException(status_code=401, detail="Missing token")
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )
            if token != user.token:
                raise HTTPException(status_code=401, detail="Incorrect token")
            q = select(User).where(User.username == new_username)
            new_user = session.execute(q).scalar()
            if new_user is not None:
                raise HTTPException(
                    status_code=401,
                    detail="User with new username exists"
                )

            sex = "male" if user.sex == Sex.male\
                else "female" if user.sex == Sex.female\
                else "other"
            username = new_username or user.username
            sex = new_sex or user.sex
            old_path = Path(user.avatar_path)
            if old_path.name.startswith("unknown_user"):
                path = str(old_path)
            else:
                path = str(avatar_folder / username)
            old_path.rename(path)
            session.delete(user)
            n_sex = Sex.female if new_sex == "female"\
                else Sex.male if new_sex == "male"\
                else Sex.other
            session.add(User(
                username=username,
                avatar_path=path,
                sex=n_sex,
                token=token
            ))
            session.commit()
            return {
                "username": username,
                "sex": sex,
                "avatar": app.url_path_for(
                    "get_user_avatar", username=username
                ),
                "token": token
            }

    @app.get(
        "/users/avatars/{username}",
        responses={
            200: {
                "content": {"image/png": {}}
            }
        },
        response_class=Response
    )
    async def get_user_avatar(username: str,) -> Response:
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )
            with open(user.avatar_path, "rb") as avatar:
                avatar_bytes = avatar.read()
        return Response(content=avatar_bytes, media_type="image/png")

    @app.put("/users/avatars/{username}")
    async def edit_user_avatar(
        username: str,
        file: UploadFile = File(...),
        token: tp.Optional[str] = Header(None)
    ) -> dict[str, str]:
        if token is None:
            raise HTTPException(status_code=401, detail="Missing token")
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )
            if token != user.token:
                raise HTTPException(status_code=401, detail="Incorrect token")
            path = str(avatar_folder / username)

            with open(path, "wb") as f:
                f.write(await file.read())

            session.delete(user)
            session.add(User(
                username=user.username,
                avatar_path=path,
                sex=user.sex,
                token=token
            ))
            session.commit()

        return {}

    @app.get(
        "/favicon.ico",
        responses={
            200: {
                "content": {"image/x-icon": {}}
            }
        },
        response_class=Response
    )
    async def get_favicon() -> Response:
        with open(favicon, "rb") as f:
            favicon_bytes = f.read()
        return Response(content=favicon_bytes, media_type="image/x-icon")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host, port=rabbitmq_port
        )
    )
    channel = connection.channel()
    channel.confirm_delivery()
    channel.queue_declare(queue=rabbitmq_queue, durable=True)

    @app.post("/users/characters/{username}")
    async def generate_characters(
        username: str,
        token: tp.Optional[str] = Header(None)
    ) -> dict[str, str]:
        if token is None:
            raise HTTPException(status_code=401, detail="Missing token")
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )
            if token != user.token:
                raise HTTPException(status_code=401, detail="Incorrect token")

            sex = "male" if user.sex == Sex.male\
                else "female" if user.sex == Sex.female\
                else "other"
            channel.basic_publish(
                exchange='',
                routing_key=rabbitmq_queue,
                body=json.dumps({
                    "username": user.username,
                    "sex": sex,
                    "session_count": user.session_count,
                    "win_count": user.win_count,
                    "lose_count": user.lose_count,
                    "time": user.time
                }),
                mandatory=True
            )

        return {}

    @app.get(
        "/users/characters/{username}",
        responses={
            200: {
                "content": {"application/pdf": {}}
            }
        },
        response_class=Response
    )
    async def get_characters(username: str) -> Response:
        with Session() as session:
            q = select(User).where(User.username == username)
            user = session.execute(q).scalar()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User with this username is not exist"
                )

        path = pdfs_folder / f"{username}.pdf"
        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail="Profile PDF is not exist. If you did "
                       "not use /users/characters/{username}"
                       " that use this else wait."
            )

        with open(path, "rb") as f:
            b = f.read()
        return Response(content=b, media_type="application/pdf")

    uvicorn.run(app, host=host, port=port)


@click.command()
@click.option("--host", default="0.0.0.0", type=str)
@click.option("--port", default=8000, type=int)
@click.option("--rabbitmq_host", default="localhost", type=str)
@click.option("--rabbitmq_port", default=5672, type=int)
@click.option("--rabbitmq_queue", default="rabbitmqqueue", type=str)
def main(
    host: str, port: int,
    rabbitmq_host: str, rabbitmq_port: int, rabbitmq_queue: str
) -> None:
    setup(host, port, rabbitmq_host, rabbitmq_port, rabbitmq_queue)


if __name__ == "__main__":
    main()
