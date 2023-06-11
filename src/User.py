from typing import Any

from FPL.utils.fetch import fetch_request_async


class User:
    def __init__(self, session: Any, id: int) -> None:
        self.session = session
        self.id = id

    async def get_user(self):
        await fetch_request_async(
            f"https://fantasy.premierleague.com/api/entry/{self.id}/"
        )
