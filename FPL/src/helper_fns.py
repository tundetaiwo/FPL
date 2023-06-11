import asyncio
import datetime
import json
from functools import lru_cache

# from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import requests

# -- Define Types -- #
JSON = int | str | float | bool | None
JSONObject = dict[str, JSON]
from aiohttp import ClientSession


class Fantasy:
    """_summary_"""

    def __init__(self, gameweek: int = None, session=None):
        # --  Error Handling -- #

        # -- ping api for current gameweek -- #
        if gameweek == None:
            gameweek = self.get_gameweek()

        self.current_gw = gameweek
        # -- Overall Player Data -- #
        response = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/", timeout=30
        )
        fpl_json = json.loads(response.content)

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
        team_df = pd.DataFrame(fpl_json["teams"])
        # --  Data Cleaning -- #
        players_df = players_df.sort_values(
            by=["form"], ignore_index=True, ascending=False
        )[columns]

        players_df["full_name"] = (
            players_df["first_name"] + " " + players_df["second_name"]
        )
        players_df.drop(columns=["first_name", "second_name"], inplace=True)
        pos_dict = dict(
            pd.DataFrame(
                fpl_json["element_types"], columns=["id", "plural_name_short"]
            ).values
        )
        id_dict = pd.Series(
            players_df["full_name"].values, index=players_df["id"].values
        ).to_dict()

        team_dict = pd.Series(team_df["id"].values, index=team_df["name"].values)

        # -- create dictionary of players and respective IDs -- #
        player_dict_invalid = []
        for id, name in id_dict.items():
            try:
                if "a" in name:
                    pass
            except Exception as e:
                print(f"id: {id}, name value: {name}")
                print(f"Error: {e}")

                print("removing value from dictionary\n")
                player_dict_invalid.append(id)

        for id in player_dict_invalid:
            id_dict.pop(id)

        # dict of "name": id
        self.id_dict = id_dict
        # dict of id: "name"
        self.player_dict = {name: id for id, name in id_dict.items()}
        self.pos_dict = pos_dict

        # TODO: Create a new name for this
        self.players_df = players_df

        self.session = ClientSession()

        # Create Dictionary of player names and IDs

    def get_gameweek(self):
        """Method to get current gameweek from FPL API"""

        url = "https://fantasy.premierleague.com/api/bootstrap-static/"

        response = requests.get(url)
        data = response.json()

        current_time = datetime.datetime.now()

        for gameweek in data["events"]:
            deadline_time = datetime.datetime.strptime(
                gameweek["deadline_time"], "%Y-%m-%dT%H:%M:%SZ"
            )
            if deadline_time > current_time:
                current_gameweek = gameweek["id"] - 1
                break

        print(f"current gameweek is {current_gameweek}.")

        return current_gameweek

    def get_transfer_history(self, user_id: int) -> pd.DataFrame:
        response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{user_id}/transfers/"
        )
        json_hist = json.loads(response.content)

        return pd.DataFrame(
            json_hist, columns=["element_in", "element_out", "event", "entry"]
        )

    async def get_chips_played(self, user_id: int) -> Dict:
        """_summary_

        :param user_id: id of user
        :type user_id: int
        :return: _description_
        :rtype: Dict
        """
        chip_dict = {}
        for gw in range(1, self.current_gw):
            response = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw}/picks/",
                timeout=30,
            )
            user_json = json.loads(response.content)

            chip_type = user_json.get("active_chip")
            if chip_type is not None:
                # Rename chip types for readability
                chip_type = "3xcaptain" if chip_type == "3xc" else chip_type

                if chip_dict.get(chip_type) is None:
                    chip_dict[chip_type] = [gw]
                else:
                    chip_dict[chip_type].append(gw)

        return chip_dict

    # @lru_cache(maxsize=50)
    async def _get_page(self, i: int, session: ClientSession):
        response = await session.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_new_entries=1&page_standings={i}&phase=1",
            ssl=False,
        )
        return response.json()

    async def _get_top_users(self, n: int) -> pd.DataFrame():
        """Method to get information of top n users in the overall league table.

        Parameters
        ----------
        `n (int)`: Top n players to return, default is 50
        """

        top_n_teams = pd.DataFrame()
        top_n_transfer_history = pd.DataFrame()
        # Get maximum page nth user would be on
        page_range = np.arange(1, 1 + int(np.ceil(n / 50)))
        # fetch pages
        async with ClientSession() as session:
            page_list = await asyncio.gather(
                *(self._get_page(i, session) for i in page_range)
            )
            user_urls = []
            user_ids = []
            # page_list = await page_list
            for page in page_list:
                page = await page
                print(page.keys())
                for entry in page["standings"]["results"]:
                    user_ids.append(entry["id"])

            users_json_list = await asyncio.gather(
                *(self.get_user(id, session) for id in user_ids)
            )

        return users_json_list

    async def get_user(
        self, user_id: int, session: ClientSession, gameweek: int = None
    ) -> pd.DataFrame:
        """Method to retrieve user team information from FPL API

        :param user_id: user id
        :type user_id: int
        :param gameweek: gameweek to retrieve. If None then uses current gameweek as default
        :type gameweek: int, optional

        Returns
        -------
        `pd.DataFrame`: DataFrame containing team for specific gameweek

        """
        if gameweek is None:
            gameweek = self.current_gw
        # user_id = 2960212
        # send request to FPL API
        response = await session.get(
            f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{self.current_gw}/picks/",
            ssl=False,
        )
        user_json = await response.json()

        print(user_json.keys())
        # get active teamj
        if "picks" in user_json:
            active_team = pd.DataFrame(user_json.get("picks"))
            active_team["element"].replace(self.id_dict, inplace=True)
        else:
            active_team = pd.DataFrame()

        # Use position to get sub positions
        active_team["position"] = active_team["position"].apply(
            lambda x: max(0, x - 12)
        )
        active_team.rename({"position": "sub_position"}, axis=1, inplace=True)

        return active_team

    def get_top_users(self, n: int = 50):
        return asyncio.run(self._get_top_users(n))
        # for user in overall_league_json["standings"]["results"]:
        #     user_id = user["entry"]

        #     # get team for user
        #     user_team = self.get_user(user_id)
        #     user_team["user_id"] = user_id
        #     top_n_teams = pd.concat([top_n_teams, user_team], axis=0)

        #     # get transfer history for us er
        #     top_n_transfer_history = pd.concat(
        #         [top_n_transfer_history, self.get_transfer_history(user_id)], axis=0
        #     )
        # # stop when rank is greater than n
        # if user["rank"] == n:
        #     print("breaking")
        #     break

        # # Clean DataFrames
        # self.top_n_teams = top_n_teams.reset_index(drop=True)
        # self.top_n_transfer_history = top_n_transfer_history.reset_index(
        #     drop=True
        # ).replace({"element_in": self.id_dict, "element_out": self.id_dict})

        # # Calculate transfers out/in for top n in the last 3 weeks
        # self.top_n_transfers_out = self.top_n_transfer_history.query(
        #     f"event>={self.current_gw-2}"
        # )["element_out"].value_counts()
        # self.top_n_transfers_in = self.top_n_transfer_history.query(
        #     f"event>={self.current_gw-2}"
        # )["element_in"].value_counts()

        return users_json_list

    def top_users_chip_history(self, n: int = 50):
        """TODO: finish writing function

        :param n: _description_, defaults to 50
        :type n: int, optional
        """
        max_page = 1 + int(np.ceil(n / 50))
        for i in np.arange(1, max_page):
            # for i in range(1, 101):
            print(f"Completion: {i/max_page:.2%}", end="\r")
            response = requests.get(
                f"https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_new_entries=1&page_standings={i}&phase=1",
                timeout=30,
            )

    def get_request_sync(self, url: str) -> JSONObject:
        response = requests.get(url)
        return response.json()

    async def get_request_async(self, url: str) -> JSONObject:
        return await asyncio.to_thread(self.get_request_async, url)

    def get_player_info(self, player: str, window: int = 5) -> pd.DataFrame:
        """Methhod to extract information for player(s), such as recent form.

        Parameters
        ----------
        `player (str)`: Name of player to extract FPL information, defaults to None
        `window (int)`: window of game weeks to look back over. If current gameweek is 15 and `window=5` then function will return information from gameweek 10-15. Also is the value for future window, defaults to 5

        Return
        ------
        `pd.DataFrame`: Dataframe of player stats.

        """

        self.recent_form = {}
        self.recent_form_graph = {}

        player_id = self.player_dict[player]
        response = self.get_request_sync(
            f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        )
        player_df = (
            pd.DataFrame(response["history"])
            .reset_index()
            .rename(columns={"index": "event"})
        )

        fixtures_df = pd.DataFrame(response["fixtures"])
        recent_df = player_df.query(f"round > {self.current_gw - window}")
        upcoming_fixtures_df = fixtures_df.query(f"event < {self.current_gw + window}")[
            ["event", "difficulty", "id"]
        ]

        # TODO: Consider using GW instead of kickoff_time
        self.recent_form_graph.update(
            {player_id: px.line(player_df, y="total_points", x="round")}
            # {player: px.line(recent_form_df, y="total_points", x="kickoff_time")}
        )
        self.recent_form.update({player_id: recent_df.total_points.mean()})

        return player_df

    async def get_all_player_info(self, players: List[str]):
        if players is None:
            players = self.id_dict.keys()

        player_tuple = asyncio.gather(
            *[self.get_player_info(player) for player in players]
        )
        await player_tuple
        return player_tuple
