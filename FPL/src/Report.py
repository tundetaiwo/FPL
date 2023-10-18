# %%
import time
import webbrowser
from typing import Dict, List, Optional

import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback_context, dash_table, dcc, html
from tqdm import tqdm

from FPL.src import (
    basic_player_df,
    get_league_data,
    get_player_id_dict,
    get_player_info,
    get_team_id_dict,
    get_user_leagues_id,
    get_users,
    get_users_id,
)
from FPL.utils import (
    POS_DICT,
    _get_api_url,
    dir_cache,
    fetch_request,
    get_current_gw,
    clear_dir_cache,
)
from tools.get_lan_ip import get_lan_ip


# %%
class FPLReport:
    def __init__(self, gw: Optional[int] = None):
        if gw is None:
            gw = get_current_gw()

        self.gw: int = gw
        self.app: Dash = None

        self.tab: dict = {}
        self.bootstrap_plots: dict = {}

        # Flags because easier to follow than hasattr
        self._general_summary_flag: bool = False
        self._top_players_flag: bool = False
        self._leagues_generated_flag: bool = False
        self._player_analysis_flag: bool = False

        # user league attributes
        self.user_league_ownership_tbls: Dict = {}
        self.user_league_standing_tbls: Dict = {}
        self.user_league_ownership_graphs: Dict = {}

        self.teams_id_dict = None

        # weekly summary attributes
        self.overall_top_n_tbl: Dict = {}
        self.overall_top_n_bar: Dict = {}
        self.n: int = None

        # player analysis attributes
        self.recent_df: pd.DataFrame = None
        self.upcoming_fixtures_df: pd.DataFrame = None
        self.player_analysis_features: List[str] = None
        self.player_analysis_list: List[str] = None

    def _get_league_player_ownership(self, league_id: int, n) -> pd.DataFrame:
        """

        Parameters
        ----------
        `league_id (int)`:

        `n (int)`: cap to put on number of top players to extract from league

        Return
        ------
        `pd.DataFrame`: dataframe of player ownership within that specific league

        """

        user_id = get_users_id(league_id=league_id, top_n=n)
        users = get_users(user_id, self.gw)

        user_players = []
        for user in users:
            user_players.append([player["element"] for player in user["picks"]])

        user_players = np.array(user_players).ravel()
        unique, count = np.unique(user_players, return_counts=True)
        league_player_tbl = (
            pd.DataFrame(
                {
                    "player": unique,
                    "count": count,
                    "ownership (%)": 100 * count / len(users),
                }
            )
            .replace({"player": get_player_id_dict()})
            .sort_values("count", ascending=False)
        )
        return league_player_tbl

    
    def generate_summary(self, refresh: int = 60):
        """
        Method to create top n

        Parameters
        ----------

        `refresh (int)`: time (minutes) to check since last save, default=60

        Return
        ------
        `None`

        """
        @dir_cache(refresh=refresh)
        def _generate_summary():
            self_dict = {}
            self_dict["_general_summary_flag"] = True

            # get bootstrap dataframe
            self_dict["teams_id_dict"] = get_team_id_dict()
            # TODO: delete??
            bootstrap_df: pd.DataFrame = basic_player_df()
            # fields that are always shown
            # TODO: maybe create overall rename dict and place in utils/definitions?
            always_fields_dict = {
                "full_name": "full name",
                "team": "team",
                "element_type": "position",
                "now_cost": "price",
            }

            core_fields_dict = {
                "event_points": "points this week",
                "points_per_game": "points per game",
                "total_points": "total points",
                "form": "form",
                "value_form": "value form",
                "yellow_cards": "yellow cards",
                "red_cards": "red cards",
                "goals_scored": "goals scored",
                "expected_goals": "expected goals",
                "expected_goals_per_90": "expected goals per 90",
                "assists": "assists",
            }

            transfer_fields_dict = {
                "selected_by_percent": "ownership (%)",
                "transfers_in_event": "transfers in event",
                "transfers_out_event": "transfers out event",
            }
            self_dict["gk_fields"] = [
                "saves",
                "saves_per_90",
                "clean_sheets",
                "clean_sheets_per_90",
            ]
            self_dict["def_fields"] = [
                "clean_sheets",
                "clean_sheets_per_90",
            ]
            bootstrap_df["full_name"] = (
                bootstrap_df["first_name"] + " " + bootstrap_df["second_name"]
            )

            # -- bootstrap dataframme cleanup -- #
            self_dict["bootstrap_df"] = (
                bootstrap_df.rename(
                    columns=dict(
                        **core_fields_dict, **always_fields_dict, **transfer_fields_dict
                    )
                )
                .astype({"ownership (%)": float})
                .replace({"team": self_dict["teams_id_dict"], "position": POS_DICT})
                .assign(price=lambda x: x["price"] / 10)
            )

            self_dict["core_fields"] = list(core_fields_dict.values())
            self_dict["always_fields"] = list(always_fields_dict.values())
            self_dict["transfer_fields"] = list(transfer_fields_dict.values())

            # Positions
            self_dict["pos_list"] = list(POS_DICT.values())

            return self_dict

        # do this way in order to cache inner function
        self_dict = _generate_summary()
        for name, attr in self_dict.items():
            setattr(self, name, attr)


    def generate_top_managers(self, n: int = 1000, refresh: int = 60):
        """

        Parameters
        ----------
        `n (int)`: number of top players to find, for example if 1000 then will extract data for top 1000 ranked players

        `refresh (int)`: time (minutes) to check since last save, default=60

        Return
        ------
        `None`

        """

        @dir_cache(refresh=refresh)
        def _generate_top_managers(n: int):
            self_dict = {}
            self_dict["_top_players_flag"] = True
            self_dict["overall_top_n_tbl"] = self._get_league_player_ownership(
                314, n
            )
            self_dict["overall_top_n_bar"] = px.bar(
                self_dict["overall_top_n_tbl"].head(30),
                # self.overall_top_n_tbl.query("count > 50"),
                x="player",
                y="ownership (%)",
                title=f"Top {n} ownership",
            )
            self_dict["n"] = n
            return self_dict

        # do this way in order to cache inner function
        self_dict = _generate_top_managers(n)
        for name, attr in self_dict.items():
            setattr(self, name, attr)

    def generate_player_analysis(
        self,
        players: Optional[List[str] | List[int]] = None,
        gw: int = None,
        window: int = 5,
        refresh: int = 30,
    ):
        """
        Method to generate analysis information of premier league players

        Parameters
        ----------
        `players (List[str])`: list of players to perform analysis on

        `gw (int)`: upper limit of gameweek to look at, if None then looks at most recent gameweek. Defualt=None

        `window (int)`: window of game weeks to look back over. If current gameweek is 15 and `window=5` then function will return information from gameweek 10-15. Also is the value for future window, defaults to 5

        `refresh (int)`: time (minutes) to check since last save, default=30

        Return
        ------
        `None`

        """

        @dir_cache(refresh=refresh)
        def _generate_player_analysis(
            players: List[str] | List[int], gw: int, window=5
        ) -> None:
            if gw is None:
                gw = self.gw

            id_dict = get_player_id_dict()
            if players is None:
                players = list(id_dict.keys())

            # if passing a list of players names replace names with ids
            if all(isinstance(ele, str) for ele in players):
                player_dict = get_player_id_dict(reverse=True)
                try:
                    players = [player_dict[name] for name in players]

                except KeyError as err:
                    raise ValueError(
                        """Player name cannot be found in player 
                                    id dictionary, please make sure player plays 
                                    for premier league or make sure id dictionary is up to date."""
                    ) from err
            elif not all(isinstance(ele, int) for ele in players):
                raise ValueError("IDs must be either all strings or all integers.")

            # calculating max like this is fairly inexpensive
            if any(ID > max(players) or ID <= 0 for ID in players):
                raise ValueError(
                    "IDs in list do not lie within id dictionary, please consult with get_player_id_dict method."
                )

            data = get_player_info(players)
            player_df = pd.DataFrame()
            fixtures_df = pd.DataFrame()
            for player in tqdm(data, "Player Analysis: "):
                player_name = id_dict[player["history"][0]["element"]]
                player_df = pd.concat([player_df, pd.DataFrame(player["history"])])

                df = pd.DataFrame(player["fixtures"])
                df["full name"] = id_dict[player["history"][0]["element"]]
                fixtures_df = pd.concat([fixtures_df, df])

            player_df.reset_index()
            fixtures_df.reset_index()

            self_dict = {}
            self_dict["recent_df"] = player_df.query(
                f"round > {gw - window} and round <= {gw}"
            )

            self_dict["player_analysis_features"] = self_dict[
                "recent_df"
            ].columns.tolist()
            self_dict["player_analysis_list"] = [id_dict[ID] for ID in players]

            self_dict["recent_df"].loc[:, "full name"] = (
                self_dict["recent_df"].loc[:, "element"].replace(id_dict)
            )

            # TODO: maybe want to up window from 10 to either <window> or 15?
            self_dict["upcoming_fixtures_df"] = (
                fixtures_df.query(f"event < {gw + 10}")
                .loc[:, ["full name", "event", "difficulty", "id", "is_home"]]
                .sort_values(by="event")
            )
            self_dict["_player_analysis_flag"] = True
            return self_dict

        # do this way in order to cache inner function
        self_dict = _generate_player_analysis(players, gw, window)
        for name, attr in self_dict.items():
            setattr(self, name, attr)

    def generate_leagues(self, id: Optional[List[int]] = None, refresh: int = 120):
        """
        Method to generate information on leagues

        Parameters
        ----------
        `id (List[int])`: player id to get league information

        `refresh (int)`: time (minutes) to check since last save. Setting to 0 will force a cache miss, default=120

        Return
        ------
        `None`

        """

        @dir_cache(refresh=refresh)
        def _generate_leagues(id: List[int]):
            league_ids = get_user_leagues_id(id)
            league_data = get_league_data(league_ids)
            self_dict = {}
            self_dict["user_league_standing_tbls"]={}

            for data in league_data:
                league_name = data["league"]["name"]
                league_id = data["league"]["id"]
                self_dict["user_league_standing_tbls"][league_name] = pd.DataFrame(
                    data["standings"]["results"]
                )[
                    [
                        "rank",
                        "player_name",
                        "entry_name",
                        "event_total",
                        "total",
                    ]
                ].rename(
                    columns={
                        "player_name": "player name",
                        "entry_name": "team name",
                        "last_rank": "previous_rank",
                        "event_total": "round total",
                    }
                )
                tbl = self._get_league_player_ownership(league_id, 300)
                self_dict["user_league_ownership_graphs"][league_name] = px.bar(
                    tbl.head(50),
                    x="player",
                    y="ownership (%)",
                    # y="count",
                    title=f"{league_name} ownership",
                )
                self_dict["user_league_ownership_tbls"][league_name] = tbl

            self_dict["_leagues_generated_flag"] = True
            return self_dict

        # do this way in order to cache inner function
        self_dict = _generate_leagues(id)
        for name, attr in self_dict.items():
            setattr(self, name, attr)

    def _build_tabs(self) -> None:
        if self._general_summary_flag:
            self.tab["overall_summary"] = dcc.Tab(
                label="Overall Summary",
                value="overall_summary",
                children=html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Ownership",
                                            style={"text-align": "center"},
                                        ),
                                        dash_table.DataTable(
                                            id="ownership_dt", page_size=10
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "margin-right": 20,
                                    },
                                ),
                                html.Div(
                                    [
                                        html.H3(
                                            "Transfers In",
                                            style={"text-align": "center"},
                                        ),
                                        dash_table.DataTable(
                                            id="transfers_in_dt", page_size=10
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "margin-left": 20,
                                        "margin-right": 20,
                                    },
                                ),
                                html.Div(
                                    [
                                        html.H3(
                                            "Transfers Out",
                                            style={"text-align": "center"},
                                        ),
                                        dash_table.DataTable(
                                            id="transfers_out_dt", page_size=10
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "margin-left": 20,
                                    },
                                ),
                            ],
                            style={"text-align": "center"},
                        ),
                        html.H2("Feature"),
                        dcc.Dropdown(
                            options=self.core_fields,
                            value=self.core_fields[0],
                            id="summary_dropdown",
                        ),
                        html.Button("<- Prev", id="prev_btn_ws", n_clicks=0),
                        html.Button("-> Next", id="next_btn_ws", n_clicks=0),
                        daq.BooleanSwitch(id="summary_boolswitch", on=True),
                        html.H2("Position"),
                        dcc.Dropdown(
                            options=self.pos_list,
                            value=self.pos_list,
                            id="summary_pos_dd",
                            multi=True,
                        ),
                        html.Br(),
                        dash_table.DataTable(id="summary_dt", page_size=10),
                    ]
                ),
            )

        if self._top_players_flag:
            top_n_dt = dash_table.DataTable(
                self.overall_top_n_tbl.to_dict("records"), id="top_n_tbl", page_size=10
            )
            self.tab["overall_top_n"] = dcc.Tab(
                label="Top N Managers",
                value="overall_top_n",
                children=html.Div(
                    [
                        html.H2(f"Top {self.n} FPL Managers"),
                        dcc.Graph(id="top_n_bar", figure=self.overall_top_n_bar),
                        top_n_dt,
                    ]
                ),
            )

        if self._leagues_generated_flag:
            self.league_options = list(self.user_league_ownership_graphs.keys())
            self.tab["user_leagues"] = dcc.Tab(
                label="User Leagues",
                value="user_leagues",
                children=html.Div(
                    [
                        html.H2("User League Information"),
                        dcc.Dropdown(
                            options=self.league_options,
                            value=self.league_options[0],
                            id="user_league_dropdown",
                        ),
                        html.Button("<- Prev", id="prev_btn_ul", n_clicks=0),
                        html.Button("-> Next", id="next_btn_ul", n_clicks=0),
                        html.H3(id="average_html"),
                        dash_table.DataTable(id="user_league_table", page_size=10),
                        html.H3("Ownwership"),
                        dcc.Graph(id="league_ownership_bar"),
                        dash_table.DataTable(id="league_ownership_tbl", page_size=10),
                    ]
                ),
            )

        if self._player_analysis_flag:
            self.tab["player_analysis"] = dcc.Tab(
                label="Player Analysis",
                value="player_analysis",
                children=html.Div(
                    [
                        html.H2("Weekly Player Analysis"),
                        dcc.Dropdown(
                            options=self.player_analysis_list,
                            value=self.player_analysis_list[0],
                            id="player_selection_dropdown",
                        ),
                        # player selection dropdown
                        html.Button("<- Prev", id="prev_btn_ps", n_clicks=0),
                        html.Button("-> Next", id="next_btn_ps", n_clicks=0),
                        dash_table.DataTable(id="player_analysis_tbl", page_size=5),
                        dcc.Dropdown(
                            options=self.player_analysis_features,
                            value=self.player_analysis_features[0],
                            id="player_analysis_dropdown",
                        ),
                        html.Button("<- Prev", id="prev_btn_pa", n_clicks=0),
                        html.Button("-> Next", id="next_btn_pa", n_clicks=0),
                        dcc.Graph("player_analysis_graph"),
                    ]
                ),
            )

    def _build_layout(self) -> None:
        """
        Function to build dash app layout combining the tabs if corresponding method has been run

        Return
        ------
        `None`

        """
        self.app.layout = html.Div(
            [
                html.H1(
                    "Fantasy Premier League Dashboard", style={"text-align": "center"}
                ),
                dcc.Tabs(
                    id="tabs",
                    value=list(self.tab.values())[0].value,
                    children=[tab for tab in self.tab.values()],
                ),
            ]
        )

    def _build_callback_fns(self) -> None:
        """
        Function to call all available callback functions

        Return
        ------
        `None`

        """

        def _dropdown(dd_feature, dd_list, ctx, prev_id, next_id):
            if ctx.triggered_id == f"{prev_id}":
                if dd_list.index(dd_feature) == 0:
                    dd_feature = dd_list[-1]
                else:
                    dd_feature = dd_list[dd_list.index(dd_feature) - 1]
            elif ctx.triggered_id == f"{next_id}":
                if dd_list.index(dd_feature) == len(dd_list) - 1:
                    dd_feature = dd_list[0]
                else:
                    dd_feature = dd_list[dd_list.index(dd_feature) + 1]
            return dd_feature

        if self._general_summary_flag:

            @self.app.callback(
                [
                    Output("summary_dt", "data"),
                    Output("ownership_dt", "data"),
                    Output("transfers_in_dt", "data"),
                    Output("transfers_out_dt", "data"),
                    Output("summary_dropdown", "value"),
                ],
                [
                    Input("summary_dropdown", "value"),
                    Input("summary_pos_dd", "value"),
                    Input("prev_btn_ws", "n_clicks"),
                    Input("next_btn_ws", "n_clicks"),
                    Input("summary_boolswitch", "on"),
                ],
            )
            def _weekly_summary_callback(
                dd_feature, dd_pos, prev_btn_ws, next_btn_ws, sum_bs
            ):
                # -- button functionality -- #
                ctx = callback_context
                dd_feature = _dropdown(
                    dd_feature, self.core_fields, ctx, "prev_btn_ws", "next_btn_ws"
                )
                # -- Filter data to relevant features -- #
                df_summary_out = self.bootstrap_df[
                    self.always_fields + [dd_feature]
                ].sort_values(by=dd_feature, ascending=not sum_bs)
                df_summary_out.insert(
                    0, "rank", range(1, self.bootstrap_df.shape[0] + 1)
                )

                # -- positional filtering -- #
                idx = df_summary_out["position"].isin(dd_pos)
                df_summary_out = df_summary_out[idx]

                df_transfers = self.bootstrap_df[
                    self.always_fields + self.transfer_fields
                ]
                df_transfers.insert(0, "rank", range(1, self.bootstrap_df.shape[0] + 1))

                df_ownership_out = df_transfers[
                    ["full name", self.transfer_fields[0]]
                ].sort_values(by=self.transfer_fields[0], ascending=False)

                df_transfers_in_out = df_transfers[
                    ["full name", self.transfer_fields[1]]
                ].sort_values(by=self.transfer_fields[1], ascending=False)

                df_transfers_out_out = df_transfers[
                    ["full name", self.transfer_fields[2]]
                ].sort_values(by=self.transfer_fields[2], ascending=False)
                return [
                    df_summary_out.to_dict("records"),
                    df_ownership_out.to_dict("records"),
                    df_transfers_in_out.to_dict("records"),
                    df_transfers_out_out.to_dict("records"),
                    dd_feature,
                ]

        if self._leagues_generated_flag:

            @self.app.callback(
                [
                    Output("user_league_table", "data"),
                    Output("league_ownership_bar", "figure"),
                    Output("league_ownership_tbl", "data"),
                    Output("average_html", "children"),
                    Output("user_league_dropdown", "value"),
                ],
                [
                    Input("user_league_dropdown", "value"),
                    Input("prev_btn_ul", "n_clicks"),
                    Input("next_btn_ul", "n_clicks"),
                ],
            )
            def _user_leagues_callback(league_name, prev_btn_ul, next_btn_ul):
                ctx = callback_context
                league_name = _dropdown(
                    league_name, self.league_options, ctx, "prev_btn_ul", "next_btn_ul"
                )

                standings_tbl = self.user_league_standing_tbls[league_name].to_dict(
                    "records"
                )
                ownership_graphs = self.user_league_ownership_graphs[league_name]
                ownership_tbl = self.user_league_ownership_tbls[league_name].to_dict(
                    "records"
                )
                gw_average = self.user_league_standing_tbls[league_name][
                    "round total"
                ].mean()
                average_html = f"""
                    '{league_name}' (GW {self.gw})\n
                    Average Points: {gw_average:.2f}
                """

                return [
                    standings_tbl,
                    ownership_graphs,
                    ownership_tbl,
                    average_html,
                    league_name,
                ]

        if self._player_analysis_flag:

            @self.app.callback(
                [
                    Output("player_analysis_graph", "figure"),
                    Output("player_analysis_tbl", "data"),
                    Output("player_selection_dropdown", "value"),
                    Output("player_analysis_dropdown", "value"),
                ],
                [
                    Input("player_selection_dropdown", "value"),
                    Input("prev_btn_ps", "n_clicks"),
                    Input("next_btn_ps", "n_clicks"),
                    Input("player_analysis_dropdown", "value"),
                    Input("prev_btn_pa", "n_clicks"),
                    Input("next_btn_pa", "n_clicks"),
                ],
            )
            def _player_analysis_callback(
                player_name,
                prev_btn_pa,
                next_btn_pa,
                feature_name,
                prev_btn_ps,
                next_btn_ps,
            ):
                # TODO: graph player stats on a weekly basis
                # TODO: table showing next fixtures, difficulty & percentage at home
                ctx = callback_context
                player_name = _dropdown(
                    player_name,
                    self.player_analysis_list,
                    ctx,
                    "prev_btn_ps",
                    "next_btn_ps",
                )
                feature_name = _dropdown(
                    feature_name,
                    self.player_analysis_features,
                    ctx,
                    "prev_btn_pa",
                    "next_btn_pa",
                )

                # Graph showing player stats on a weekly basis
                player_df = self.recent_df.query("`full name` == @player_name")[
                    ["round", feature_name]
                ]
                player_graph = px.line(player_df, x="round", y=feature_name)

                upcoming_tbl = (
                    (self.upcoming_fixtures_df)
                    .query("`full name` == @player_name")
                    .drop(columns="full name")
                )

                return [
                    player_graph,
                    upcoming_tbl.to_dict("records"),
                    player_name,
                    feature_name,
                ]

    def full_report(self, user_id: int, top_n: int = 1_000) -> None:
        """

        Parameters
        ----------
        `top_n (int)`: number of top players to find information on, default is 1000

        `user_id (int)`: user id to get league information

        Return
        ------
        `None`

        """
        self.generate_summary()
        self.generate_top_managers(n=top_n)
        self.generate_leagues(id=user_id)
        self.generate_player_analysis()

    def _prepare_run(self) -> None:
        """
        Function that creates dash app object and runs all necessary helper functions to build the app

        Return
        ------
        `None`

        """

        # external JavaScript files
        external_scripts = [
            "https://www.google-analytics.com/analytics.js",
            {"src": "https://cdn.polyfill.io/v2/polyfill.min.js"},
            {
                "src": "https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js",
                "integrity": "sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=",
                "crossorigin": "anonymous",
            },
        ]

        # external CSS stylesheets
        external_stylesheets = [
            "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/cerulean/bootstrap.min.css",
            {
                "integrity": "sha384-3fdgwJw17Bi87e1QQ4fsLn4rUFqWw//KU0g8TvV6quvahISRewev6/EocKNuJmEw",
                "crossorigin": "anonymous",
            },
        ]

        self.app = Dash(
            __name__,
            external_scripts=external_scripts,
            external_stylesheets=external_stylesheets,
        )

        self._build_tabs()
        self._build_layout()
        self._build_callback_fns()

    def run(
        self,
        host: str = None,
        port: int = 8080,
        open_window: bool = True,
        debug: bool = False,
    ) -> None:
        """
        Function to run dashboard

        Parameters
        ----------
        `host (str)`: IP Address to host dashboard

        `port (int)`: port to host dashboard on

        `open_window (bool)`: True/False flag whether to open dashboard in new window

        `debug (bool)`: Run dashboard in Dash's debug mode. Note does not work in an interactive window

        Return
        ------
        `None`

        """

        if host is None:
            host = get_lan_ip()

        self._prepare_run()
        if open_window:
            webbrowser.open_new_tab(url=f"http://{host}:{port}/")
        self.app.run(host=host, port=port, debug=debug)

    def clear_cache(self):
        """
        Clear the directory class is using to cache function calls

        Parameters
        ----------

        Return
        ------
        `None`

        """
        clear_dir_cache("./cache")


if __name__ == "__main__":
    import pickle
    from pprint import pprint

    # Tunde user id
    rpt = FPLReport()

    # rpt.generate_leagues(tunde_id)

    # pprint(data)

    tunde_id = 5770588
    rpt.generate_player_analysis([10, 13, 131, 99])
    rpt.full_report(top_n=100, user_id=tunde_id)
    # rpt.generate_leagues(tunde_id)
    rpt.run(debug=True, open_window=False)
