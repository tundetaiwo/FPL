import asyncio
import json
from typing import Dict, List

import pandas as pd
from aiohttp import ClientSession

from FPL.src.teams import get_team_id_dict
from FPL.utils._get_api_url import _get_api_url
from FPL.utils.caching import dir_cache
from FPL.utils.fetch import fetch_request, fetch_request_async


def basic_player_df(refresh: int = 20) -> pd.DataFrame:
    """
    Function that returns the current summary of players

    Parameters
    ----------
    `refresh (int)`: time (minutes) to check since last save, default=20

    Return
    ------
    `pd.DataFrame`: summary dataframe of player stats up to current gameweek

    """

    @dir_cache(refresh=refresh)
    def _basic_player_df():
        fpl_json = fetch_request(_get_api_url("bootstrap"))
        # fpl_json = data.loads(data.content)

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
            "saves",
            "saves_per_90",
            "yellow_cards",
            "red_cards",
        ]

        players_df = pd.DataFrame(fpl_json["elements"])
        columns = players_df.columns
        players_df = players_df.sort_values(
            by=["form"], ignore_index=True, ascending=False
        )

        return players_df[columns]

    return _basic_player_df()


def get_player_id_dict(reverse: bool = False) -> Dict[str, int] | Dict[int, str]:
    """

    Parameters
    ----------
    `reverse (bool)`: reverse key, value pair i.e. <id, player> becomes <player, id> if True. Default is False

    Return
    ------
    `Dict`: dictionary of player and corresponding id key, value choice depends on `reverse` argument

    """
    fpl_json = fetch_request(_get_api_url("bootstrap"))

    # async with ClientSession() as session:
    #     fpl_json = await fetch_request_async(_get_api_url("bootstrap"), session)

    players_df = pd.DataFrame(fpl_json["elements"])
    players_df["full_name"] = players_df["first_name"] + " " + players_df["second_name"]

    if reverse:
        id_dict = pd.Series(
            players_df["id"].values, index=players_df["full_name"].values
        ).to_dict()
    else:
        id_dict = pd.Series(
            players_df["full_name"].values, index=players_df["id"].values
        ).to_dict()

    return id_dict


def get_player_info(
    ids: List[int] | List[str] = None, refresh: int = 60, max_attempts=1_000
) -> List[Dict]:
    """
    Method to extract information for player(s), such as recent form.

    Parameters
    ----------
    `player (str)`: Name of player to extract FPL information, defaults to None

    `refresh (int)`: time (minutes) to check since last save, default=60

    `max_attempts (int)`: maximum number of attempts to try fetch request, default = 1000

    Return
    ------
    `List[Dict]`: dictionary of player stats.

    """

    @dir_cache(refresh=refresh)
    def _get_player_info(ids: List[int | List[str]]) -> List[Dict]:
        async def _get_player_info_async(ids: List[int]):
            """
            Function to retrieve information given player id
            """

            urls = [_get_api_url("element", id) for id in ids]
            async with ClientSession() as session:
                tasks = [
                    fetch_request_async(url, session, max_attempts=1_000)
                    for url in urls
                ]
                data = await asyncio.gather(*tasks)
            return data

        data = asyncio.run(_get_player_info_async(ids))

        return data

    return _get_player_info(ids)
