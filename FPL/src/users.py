import asyncio
from typing import List

from aiohttp import ClientSession

from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request_async


async def _get_users_async(ids: List[int]):
    """
    Function to asynchronously retrieve user information

    Parameters
    ----------
    `ids (List[int])`:

    Return
    ------
    `user information json`:

    """
    urls = [_get_api_url("entry", id) for id in ids]
    async with ClientSession() as session:
        tasks = [fetch_request_async(url, session) for url in urls]
        data = await asyncio.gather(*tasks)
    return data


def get_users_async(ids: List[int]):
    """
    Wrapper function to asynchronously call _get_users_async
    """
    # TODO: return a dataframe somehow
    return asyncio.run(_get_users_async(ids))


async def _get_top_users_id(n) -> List[int]:
    """
    TODO
    """
    pages = (n // 50) + 1
    urls = [_get_api_url("standings", page) for page in pages]
    async with ClientSession() as session:
        tasks = [fetch_request_async(url, session) for url in urls]
        data = await asyncio.gather(*tasks)

    # TODO: turn data into a list of ids
    # TODO: return first n in list of ids


def get_top_users_id(n: int = 50) -> List[int]:
    """
    Wrapper function to asynchronously call _get_top_users_id

    Parameters
    ----------
    `n` (int): top n users to retrieve

    Return
    ------
    `list`: list of ids of top n users in ascending order

    """
    data = asyncio.run(_get_top_users_id(n))

    return data
