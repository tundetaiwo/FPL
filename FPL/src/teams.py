"""
Functions pertaining to team data
"""

from typing import Dict

import pandas as pd
from aiohttp import ClientSession

from FPL.utils._get_api_url import _get_api_url
from FPL.utils.fetch import fetch_request, fetch_request_async


def get_team_id_dict() -> Dict[int, str]:
    """
    Function to extract FPL team names from corresponding ids in API

    Return
    ------
    `pd.Series`: Series where values are team names and index is corresponding I       D

    """
    fpl_json = fetch_request(_get_api_url("bootstrap"))

    # async with ClientSession() as session:
    #     fpl_json = await fetch_request_async(_get_api_url("bootstrap"), session)

    teams_df = pd.DataFrame(fpl_json["teams"])

    id_dict = pd.Series(teams_df["name"].values, index=teams_df["id"].values).to_dict()
    return id_dict
