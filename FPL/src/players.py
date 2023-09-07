import asyncio
from typing import List

import pandas as pd
import requests
from aiohttp import ClientSession

from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request, fetch_request_async


# TODO should I make async??
def basic_player_df() -> pd.DataFrame:
    """
    Function that returns the current summary of players

    Return
    ------
    `pd.DataFrame`: summary dataframe of player stats up to current gameweek

    """

    fpl_json = fetch_request(_get_api_url("bootstrap"))
    # fpl_json = response.loads(response.content)

    # -- Columns we're interested in  -- #
    columns = [
        "first_name",
        "second_name",
        "points_per_game",
        "total_points",
        "team",
        "now_cost",
        "id",
        "selected_by_percent",
        "form",
    ]

    players_df = pd.DataFrame(fpl_json["elements"])
    players_df = (
        players_df  # .sort_values(by=["form"], ignore_index=True, ascending=False)
    )

    return players_df[columns]


# TODO should I make async??
def get_player_id_dict():
    # async def get_player_id_dict():
    """TODO"""
    fpl_json = fetch_request(_get_api_url("bootstrap"))

    # async with ClientSession() as session:
    #     fpl_json = await fetch_request_async(_get_api_url("bootstrap"), session)

    players_df = pd.DataFrame(fpl_json["elements"])
    players_df["full_name"] = players_df["first_name"] + " " + players_df["second_name"]

    id_dict = pd.Series(
        players_df["full_name"].values, index=players_df["id"].values
    ).to_dict()
    return id_dict


async def _get_player_info(ids: List[int]):
    """
    TODO
    """

    urls = [_get_api_url("element", id) for id in ids]
    async with ClientSession() as session:
        tasks = [fetch_request_async(url, session) for url in urls]
        data = await asyncio.gather(*tasks)
    return data


def get_player_info(ids: List = None):
    if ids is None:
        ids = get_player_id_dict()

    data = asyncio.run(_get_player_info(ids))
    return data
