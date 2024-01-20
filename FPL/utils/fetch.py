# %%
import asyncio
import json
import ssl

import certifi
import requests
from aiohttp import ClientSession, client_exceptions

# %%
# -- Define Types -- #
JSON = int | str | float | bool | None
JSONObject = dict[str, JSON]

ssl_context = ssl.create_default_context(cafile=certifi.where())


class FetchError(Exception):
    """Exception Error from failing to fetch a request, in order to distinguish from regular exceptions"""

    def __init__(self, message: str):
        super().__init__(message)


def fetch_request(url: str) -> JSONObject:
    """
    Function to fetch and load JSON from url

    Parameters
    ----------
    `url (str)`: url to send request
    """
    response = requests.get(url)
    return response.json()


async def fetch_request_async(
    url: str,
    session: ClientSession,
    max_attempts: int = 1000,
) -> JSONObject:
    """
    Coroutine to fetch request from url

    Parameters
    ----------
    `url (str)`: url to send request

    `session (ClientSession)`: open aiohttp ClientSession

    `max_attempts (int)`: maximum number of attempts to try fetch request, default = 1000

    Return
    ------
    `JSONObject`: JSON file of request object
    """
    attempt_count = 0

    # make sure condition is eventually met
    while True:
        try:
            async with session.get(url, ssl=ssl_context) as response:
                return await response.json()

        except client_exceptions.ContentTypeError as e:
            attempt_count += 1

        if attempt_count > max_attempts:
            raise FetchError(
                f"Maximum number of attempts ({max_attempts}) to fetch request reached."
            )
