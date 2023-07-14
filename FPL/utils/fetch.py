# %%
import asyncio
import json
import ssl

import certifi
import requests
from aiohttp import ClientSession

# %%
# -- Define Types -- #
JSON = int | str | float | bool | None
JSONObject = dict[str, JSON]

ssl_context = ssl.create_default_context(cafile=certifi.where())


def fetch_request(url: str) -> JSONObject:
    """
    Function to fetch and load JSON from url

    Parameters
    ----------
    `url (str)`: url to send request
    """
    repsonse = requests.get(url)
    return repsonse.json()


async def fetch_request_async(url: str, session: ClientSession) -> JSONObject:
    """
    Coroutine to fetch request from url

    Parameters
    ----------
    `url (str)`: url to send request
    `session (ClientSession)`: open aiohttp ClientSession
    """

    async with session.get(url, ssl=ssl_context) as response:
        return await response.json()
