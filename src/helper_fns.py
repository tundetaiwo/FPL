import datetime
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
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
            # "transfers_in",
            # "transfers_out",
            "id",
            "selected_by_percent",
            "form",
        ]

        players_df = pd.DataFrame(fpl_json["elements"])

        # --  Data Cleaning -- #
        players_df = players_df.sort_values(
            by=["form"], ignore_index=True, ascending=False
        )[columns]

        pos_dict = dict(
            pd.DataFrame(
                fpl_json["element_types"], columns=["id", "plural_name_short"]
            ).values
        )
        players_df.replace({"team": "team", "element_type": pos_dict}, inplace=True)

        response = requests.get(
            f"https://fantasy.premierleague.com/api/event/{gameweek}/live/", timeout=30
        )
        gameweek_json = json.loads(response.content)

        # -- Top Users -- #
        # get
        response = requests.get(
            "https://fantasy.premierleague.com/api/leagues-classic/314/standings/",
            timeout=30,
        )
        overall_league_json = json.loads(response.content)

        self.current_gw = gameweek

    def get_user(self, user_id: int, get_chips: bool=False) -> pd.DataFrame:

        # send request to FPL API
        response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{user_id}/", timeout=30
        )
        user_json = json.loads(response.content)

        # get active team
        active_team = pd.DataFrame(user_json["picks"])

        user_id = 2960212
        # TODO: complete 
        if get_chips:
            
            for GW in range(1, self.current_gw):
                # GW = 20
                response = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{GW}/picks/",
                    timeout=30,
                )
                user_json = json.loads(response.content)
                if user_json.get("active_chip"):
                    print(f"Game Week: {GW}, \nchip: {user_json.get('active_chip')}")
                    
        return active_team

    def get_top_users(self, n: int=50) -> pd.DataFrmae():
        """Method to get information of top n users in the overall league table.

        Parameters
        ----------
        `n (int)`: Top n players to return, defaults is 50
        """
        
        response = requests.get(
            "https://fantasy.premierleague.com/api/leagues-classic/314/standings/",
            timeout=30,
        )

        overall_league_json = json.loads(response.content)
        top_n_ids = []
        for user in overall_league_json["standings"]["results"]:
            if user["rank"]
            self.get_user(user["entry"])
            
        


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
