import asyncio
import json
from typing import List

from aiohttp import ClientSession

from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request_async


async def _get_users_async(ids: List[int]):
    """
    Function to asynchronously retrieve user information

    Parameters
    ----------
    `id (int)`:

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
    return asyncio.run(_get_users_async(ids))
