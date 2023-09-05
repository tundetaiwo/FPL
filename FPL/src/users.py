import asyncio
from typing import List

from aiohttp import ClientSession

from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request_async


def get_users_async(ids: List[int], gameweek: int):
    """
    Wrapper function to asynchronously call _get_users_async
    """

    async def _get_users_async(ids: List[int], gameweek: int):
        """
        Function to asynchronously retrieve user information

        Parameters
        ----------
        `ids (List[int])`:

        `gameweek (int)`: gameweek up to retrieve manager team information for

        Return
        ------
        `user information json`:

        """
        urls = [_get_api_url("picks", id, gameweek) for id in ids]
        async with ClientSession() as session:
            tasks = [fetch_request_async(url, session) for url in urls]
            data = await asyncio.gather(*tasks)
        return data

    return asyncio.run(_get_users_async(ids, gameweek=gameweek))


def get_top_users_id(n: int = 50) -> List[int]:
    """
    Function to asynchronously get the IDs of the top n users.

    Parameters
    ----------
    `n` (int): top n users to retrieve

    Return
    ------
    `list`: list of ids of top n users in ascending order

    Notes
    -----

    Be wary season to season! id of overall league might change in the API.
    2023: '314
    """

    async def _get_top_users_id(n) -> List[int]:
        pages = range((n // 50) + 1)
        urls = [_get_api_url("standings", id=314, page=page) for page in pages]
        # urls = [_get_api_url("standings", page, league=314) for page in pages]
        async with ClientSession() as session:
            tasks = [fetch_request_async(url, session) for url in urls]
            data = await asyncio.gather(*tasks)

        return data

    list_of_pages = asyncio.run(_get_top_users_id(n))
    top_ids = []
    # start from 1 as first page is always empty
    for page in list_of_pages[1:]:
        # Happy to make the assumption there will always be 50 players on a page
        for player in range(50):
            top_ids.append(page.get("standings")["results"][player]["entry"])

    return top_ids[:n]
