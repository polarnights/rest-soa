import strawberry
from strawberry.scalars import ID, JSON


@strawberry.type
class Game:
    id: ID
    scores: JSON

    comments: list[str]


prev_games = [
    Game(
        id=0,
        scores={
            "Ch0p1k3": 1,
            "Yulya": 2,
            "Sanya": 3,
        },
        comments=[
            "GG",
            "WP",
            "GJ"
        ]
    ),
    Game(
        id=1,
        scores={
            "Ch0p1k3": 4,
            "Pepsi": 2,
            "Nescafe Gold": 3
        },
        comments=[
            "....",
            "b****",
            "GG WP EASY KATKA"
        ]
    ),
    Game(
        id=2,
        scores={
            "228": 1,
            "1337": 2,
            "1488": 3
        },
        comments=[]
    )
]


cur_games = [
    Game(
        id=3,
        scores={
            "Coca cola": 2,
            "The North Face": 1,
            "Ch0p1k3": 4
        },
        comments=[
            "Hello",
            "Good bye"
        ]
    ),
    Game(
        id=4,
        scores={
            "228": 1,
            "1337": 2,
            "1488": 3
        },
        comments=[]
    )
]


@strawberry.type
class Query:
    @strawberry.field
    def current_games(self) -> list[Game]:
        return cur_games

    @strawberry.field
    def previous_games(self) -> list[Game]:
        return prev_games

    @strawberry.field
    def game(self, id: int) -> Game:
        games = [e for e in prev_games + cur_games if e.id == id]
        if len(games) == 0:
            raise Exception("Can't find game")
        return games[0]


@strawberry.type
class Mutation:
    @strawberry.field
    def add_comment(self, id: int, comment: str) -> Game:
        games = [e for e in prev_games + cur_games if e.id == id]
        if len(games) == 0:
            raise Exception("Can't find game")
        games[0].comments.append(comment)
        return games[0]


schema = strawberry.Schema(query=Query, mutation=Mutation)
