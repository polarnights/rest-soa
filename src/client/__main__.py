import asyncio

import click
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from simple_term_menu import TerminalMenu


async def client(url: str) -> None:
    transport = AIOHTTPTransport(url=url)
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True
    ) as session:
        while True:
            menu = TerminalMenu([
                "[c] current games",
                "[p] previous games",
                "[f] find the game",
                "[a] add comment to the game",
                "[e] exit"
            ])
            choiсe = menu.show()
            if choiсe == 4:
                return
            if choiсe == 0:
                print(await session.execute(gql(
                    """
                    query {
                        currentGames {
                            id,
                            scores,
                            comments
                        }
                    }
                    """
                )), flush=True)
            elif choiсe == 1:
                print(await session.execute(gql(
                    """
                    query {
                        previousGames {
                            id,
                            scores,
                            comments
                        }
                    }
                    """
                )), flush=True)
            elif choiсe == 2:
                game_id = input("Game id: ")
                try:
                    print(await session.execute(gql(
                        """
                        query {
                            game(id:%s) {
                                id,
                                scores,
                                comments
                            }
                        }
                        """ % game_id
                    )), flush=True)
                except Exception as e:
                    print(e.args[0])
            elif choiсe == 3:
                game_id = input("Game id: ")
                comment = input("Comment: ")
                try:
                    print(await session.execute(gql(
                        """
                        mutation {
                            addComment(id:%s, comment:"%s") {
                                id,
                                scores,
                                comments
                            }
                        }
                        """ % (game_id, comment)
                    )), flush=True)
                except Exception as e:
                    print(e.args[0])
            else:
                raise Exception("Unknown arg")


@click.command()
@click.option("--url", default="http://0.0.0.0:8000/graphql", type=str)
def main(url: str) -> None:
    asyncio.run(client(url))


if __name__ == "__main__":
    main()
