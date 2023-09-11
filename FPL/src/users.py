import asyncio
from typing import Dict, List

from aiohttp import ClientSession

from FPL.src import get_team_id_dict
from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request, fetch_request_async


def get_users(ids: List[int], gameweek: int):
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


def get_users_id(league_id: int, top_n: int = 50) -> List[int]:
    """
    Function to asynchronously get the IDs of users within a league.

    Parameters
    ----------
    `league_id (int)`:

    `top_n` (int): top n users to retrieve

    Return
    ------
    `list`: list of ids of top n users in ascending order

    Notes
    -----

    Be wary season to season! id of overall league might change in the API.
    2023: '314
    """

    async def _get_top_users_id(n) -> List[int]:
        pages = range((n // 50) + 2)
        urls = [_get_api_url("standings", id=league_id, page=page) for page in pages]
        async with ClientSession() as session:
            tasks = [fetch_request_async(url, session) for url in urls]
            data = await asyncio.gather(*tasks)

        return data

    list_of_pages = asyncio.run(_get_top_users_id(top_n))
    top_ids = []
    # start from 1 as first page is always empty
    for page in list_of_pages[1:]:
        # Happy to make the assumption there will always be 50 players on a page
        for player in range(len(page["standings"]["results"])):
            top_ids.append(page.get("standings")["results"][player]["entry"])
    return top_ids[:top_n]


def get_user_leagues_id(user_id: int) -> List[int]:
    """
    Function to get custom league ids a FPL manager has joined.

    Parameters
    ----------
    `manager_id (int)`: id of user to get league ids

    Return
    ------
    `List[int]`: list of custom leauge ids for user

    """

    url = _get_api_url("entry", user_id)
    data = fetch_request(url)
    league_ids = []
    for league in data["leagues"]["classic"]:
        # All non-custom leagues have ids from 1 to around 320
        if league["id"] < 320:
            continue
        league_ids.append(league["id"])
    return league_ids


def get_league_data(ids: List[int]) -> None:
    """
    Function to extract league data

    Parameters
    ----------
    `ids (List[int])`: list of ids

    Return
    ------
    `return`:

    """
    urls = [_get_api_url("standings", id=id) for id in ids]

    async def _get_league_data(urls):
        async with ClientSession() as session:
            tasks = [fetch_request_async(url, session) for url in urls]
            data = await asyncio.gather(*tasks)
        return data

    return asyncio.run(_get_league_data(urls))
