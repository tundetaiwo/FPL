import datetime
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import requests


class Fantasy:
    """_summary_"""

    def __init__(self, gameweek: int):

        # --  Error Handling -- #

        # -- Overall Player Data -- #
        response = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/", timeout=30
        )
        fpl_json = json.loads(response.content)

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
        self.current_gw = gameweek

        # Create Dictionary of player names and IDs

    def get_user(self, user_id: int, gameweek: int = None) -> pd.DataFrame:
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
        response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{self.current_gw}/picks/",
            timeout=30,
        )
        user_json = json.loads(response.content)

        # get active team
        active_team = pd.DataFrame(user_json["picks"])
        active_team["element"].replace(self.id_dict, inplace=True)

        # Use position to get sub positions
        active_team["position"] = active_team["position"].apply(
            lambda x: max(0, x - 12)
        )
        active_team.rename({"position": "sub_position"}, axis=1, inplace=True)

        return active_team

    def get_transfer_history(self, user_id: int) -> pd.DataFrame:
        response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{user_id}/transfers/"
        )
        json_hist = json.loads(response.content)

        return pd.DataFrame(
            json_hist, columns=["element_in", "element_out", "event", "entry"]
        )

    def get_chips_played(self, user_id: int) -> Dict:
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

    def get_top_users(self, n: int = 50) -> pd.DataFrame():
        """Method to get information of top n users in the overall league table.

        Parameters
        ----------
        `n (int)`: Top n players to return, defaults is 50
        """

        top_n_teams = pd.DataFrame()
        top_n_transfer_history = pd.DataFrame()
        max_page = 1 + int(np.ceil(n / 50))
        for i in np.arange(1, max_page):
            # for i in range(1, 101):
            print(f"Completion: {i/max_page:.2%}", end="\r")
            response = requests.get(
                f"https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_new_entries=1&page_standings={i}&phase=1",
                timeout=30,
            )

            overall_league_json = json.loads(response.content)
            for user in overall_league_json["standings"]["results"]:
                user_id = user["entry"]

                # get team for user
                user_team = self.get_user(user_id)
                user_team["user_id"] = user_id
                top_n_teams = pd.concat([top_n_teams, user_team], axis=0)

                # get transfer history for user
                top_n_transfer_history = pd.concat(
                    [top_n_transfer_history, self.get_transfer_history(user_id)], axis=0
                )
            # stop when rank is greater than n
            if user["rank"] == n:
                print("breaking")
                break

        # Clean DataFrames
        self.top_n_teams = top_n_teams.reset_index(drop=True)
        self.top_n_transfer_history = top_n_transfer_history.reset_index(
            drop=True
        ).replace({"element_in": self.id_dict, "element_out": self.id_dict})

        # Calculate transfers out/in for top n in the last 3 weeks
        self.top_n_transfers_out = self.top_n_transfer_history.query(
            f"event>={self.current_gw-2}"
        )["element_out"].value_counts()
        self.top_n_transfers_in = self.top_n_transfer_history.query(
            f"event>={self.current_gw-2}"
        )["element_in"].value_counts()

    def top_users_chip_history(self, n: int = 50):
        max_page = 1 + int(np.ceil(n / 50))
        for i in np.arange(1, max_page):
            # for i in range(1, 101):
            print(f"Completion: {i/max_page:.2%}", end="\r")
            response = requests.get(
                f"https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_new_entries=1&page_standings={i}&phase=1",
                timeout=30,
            )

    def get_player_info(
        self, players: str | List[str] = None, window: int = 5
    ) -> pd.DataFrame:
        """Methhod to extract information for player(s), such as recent form.

        :param players: _description_, defaults to None
        :type players: str | List[str], optional
        :param window: window of game weeks to look back over. If current gameweek is 15 and `window=5` then function will return information from gameweek 10-15. Also is the value for future window, defaults to 5
        :type window: int, optional
        """
        if players is None:
            players = self.id_dict.keys()

        self.recent_form = {}
        self.recent_form_graph = {}
        for player_id in players:
            response = requests.get(
                f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
            )
            player_df = pd.DataFrame(json.loads(response.content)["history"])
            fixtures_df = pd.DataFrame(json.loads(response.content)["fixtures"])
            recent_df = player_df.query(f"round > {self.current_gw - window}")
            upcoming_fixtures_df = player_df.query(
                f"event < {self.current_gw + window}"
            )[["event", "difficulty", "id"]]

            # TODO: Consider using GW instead of kickoff_time
            self.recent_form_graph.update(
                {player_id: px.line(player_df, y="total_points", x="round")}
                # {player: px.line(recent_form_df, y="total_points", x="kickoff_time")}
            )
            self.recent_form.update({player_id: recent_df.total_points.mean()})


def clean_data():
    """
    Args:
    :param param1: asda
    """

    players_df.replace({"team": "team", "element_type": pos_dict}, inplace=True)

    teams_df = pd.DataFrame(players["teams"])
    fixtures_df = pd.DataFrame(players["events"])
    today = datetime.now().timestamp()
    fixtures_df = fixtures_df.loc[fixtures_df.deadline_time_epoch > today]
    if check_update(fixtures_df) == False:
        raise Exception("Game Week too far away.")

    gameweek = fixtures_df.iloc[0].id
    # players_df = players_df[columns]
    players_df.chance_of_playing_next_round = (
        players_df.chance_of_playing_next_round.fillna(100.0)
    )
    players_df.chance_of_playing_this_round = (
        players_df.chance_of_playing_this_round.fillna(100.0)
    )
    fixtures = get(
        "https://fantasy.premierleague.com/api/fixtures/?event=" + str(gameweek)
    )
    fixtures_df = pd.DataFrame(fixtures)

    teams = dict(zip(teams_df.id, teams_df.name))
    players_df["team_name"] = players_df["team"].map(teams)
    fixtures_df["team_a_name"] = fixtures_df["team_a"].map(teams)
    fixtures_df["team_h_name"] = fixtures_df["team_h"].map(teams)

    home_strength = dict(zip(teams_df.id, teams_df.strength_overall_home))
    away_strength = dict(zip(teams_df.id, teams_df.strength_overall_away))

    fixtures_df["team_a_strength"] = fixtures_df["team_a"].map(away_strength)
    fixtures_df["team_h_strength"] = fixtures_df["team_h"].map(home_strength)

    fixtures_df = fixtures_df.drop(columns=["id"])
    a_players = pd.merge(
        players_df, fixtures_df, how="inner", left_on=["team"], right_on=["team_a"]
    )
    h_players = pd.merge(
        players_df, fixtures_df, how="inner", left_on=["team"], right_on=["team_h"]
    )

    a_players["diff"] = a_players["team_a_strength"] - a_players["team_h_strength"]
    h_players["diff"] = h_players["team_h_strength"] - h_players["team_a_strength"]

    players_df = a_players.append(h_players)
    return players_df, fixtures_df, gameweek


def update_team(email, password, id):
    players_df, fixtures_df, gameweek = get_data()


def update_team(email, password, id) -> Tuple:
    players_df, fixtures_df, gameweek = get_data()


def check_update(df: pd.DataFrame):

    today = datetime.now()
    tomorrow = (today + timedelta(days=1)).timestamp()
    today = datetime.now().timestamp()
    df = df.loc[df.deadline_time_epoch > today]

    deadline = df.iloc[0].deadline_time_epoch
    if deadline < tomorrow:
        return True
    else:
        return False
