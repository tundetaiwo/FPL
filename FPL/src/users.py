import asyncio
from typing import Dict, List

from aiohttp import ClientSession

from FPL.src import get_team_id_dict
from FPL.utils._get_api_url import _get_api_url
from FPL.utils.caching import dir_cache
from FPL.utils.fetch import fetch_request, fetch_request_async


def get_users(ids: List[int], gameweek: int, max_attempts: int = 1_000):
    """
    Function to asynchronously retrieve user information

    Parameters
    ----------
    `ids (List[int])`:

    `gameweek (int)`: gameweek up to, to retrieve manager team information for

    `max_attempts (int)`: maximum number of attempts to try fetch request, default = 1000

    Return
    ------
    `user information json`:

    """

    def _get_users(ids: List[int], gameweek: int):
        async def _get_users_async(ids: List[int], gameweek: int):
            urls = [_get_api_url("picks", id, gameweek) for id in ids]
            async with ClientSession() as session:
                tasks = [
                    fetch_request_async(url, session, max_attempts=max_attempts)
                    for url in urls
                ]
                data = await asyncio.gather(*tasks)
            return data

        return asyncio.run(_get_users_async(ids, gameweek=gameweek))

    return _get_users(ids, gameweek)


def get_users_id(
    league_id: int, top_n: int = 50, refresh: int = 60, max_attempts: int = 1_000
) -> List[int]:
    """
    Function to asynchronously get the IDs of users within a league.

    Parameters
    ----------
    `league_id (int)`:

    `top_n` (int): top n users to retrieve

    `refresh (int)`: time (minutes) to check since last save, default=60

    `max_attempts (int)`: maximum number of attempts to try fetch request, default = 1000

    Return
    ------
    `list`: list of ids of top n users in ascending order

    Notes
    -----

    Be wary season to season! id of overall league might change in the API.
    2023: '314
    """

    @dir_cache(refresh=refresh)
    def _get_users_id(league_id: int, top_n: int = 50) -> List[int]:
        async def _get_top_users_id(n) -> List[int]:
            pages = range((n // 50) + 2)
            urls = [
                _get_api_url("standings", id=league_id, page=page) for page in pages
            ]
            async with ClientSession() as session:
                tasks = [
                    fetch_request_async(url, session, max_attempts=max_attempts)
                    for url in urls
                ]
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

    return _get_users_id(league_id, top_n)


def get_user_leagues_id(user_id: int, refresh: int = 0) -> List[int]:
    """
    Function to get custom league ids a FPL manager has joined.

    Parameters
    ----------
    `manager_id (int)`: id of user to get league ids

    `refresh (int)`: time (minutes) to check since last save, default=0

    Return
    ------
    `List[int]`: list of custom leauge ids for user

    """

    @dir_cache(refresh=refresh)
    def _get_users_id(user_id: int) -> List[int]:
        url = _get_api_url("entry", user_id)
        data = fetch_request(url)
        league_ids = []
        for league in data["leagues"]["classic"]:
            # All non-custom leagues have ids from 1 to around 320
            if league["id"] < 320:
                continue
            league_ids.append(league["id"])
        return league_ids

    return _get_users_id(user_id)


def get_league_data(
    ids: List[int], refresh: int = 60, max_attempts: int = 1_000
) -> None:
    """
    Function to extract league data

    Parameters
    ----------
    `ids (List[int])`: list of ids

    `refresh (int)`: time (minutes) to check since last save, default=60

    `max_attempts (int)`: maximum number of attempts to try fetch request, default = 1000

    Return
    ------
    `return`:

    """

    @dir_cache(refresh=refresh)
    def _get_league_data(ids: List[int]) -> None:
        urls = [_get_api_url("standings", id=id) for id in ids]

        async def _get_league_data(urls):
            async with ClientSession() as session:
                tasks = [
                    fetch_request_async(url, session, max_attempts=max_attempts)
                    for url in urls
                ]
                data = await asyncio.gather(*tasks)
            return data

        return asyncio.run(_get_league_data(urls))

    return _get_league_data(ids)
