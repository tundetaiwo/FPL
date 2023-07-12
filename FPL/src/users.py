# %%
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
    print(ids)
    urls = [_get_api_url("entry", id) for id in ids]
    print(urls)
    print("")
    async with ClientSession() as session:
        tasks = [fetch_request_async(id, session) for id in ids]
        data = await asyncio.gather(*tasks)
    return data


def get_users_async(ids: List[int]):
    asyncio.run(_get_users_async([1231, 13123]))
