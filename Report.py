# %%
import time
import webbrowser
from typing import Dict, List, Optional

import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback_context, dash_table, dcc, html

from FPL.src import (
    basic_player_df,
    get_league_data,
    get_manager_leagues_id,
    get_player_id_dict,
    get_player_info,
    get_team_id_dict,
    get_users,
    get_users_id,
)
from FPL.utils import POS_DICT, _get_api_url, fetch_request, get_current_gw
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
        self._general_summary_flag = False
        self._top_players_flag = False
        self._leagues_generated_flag = False

        
        # user league attributes
        self.user_league_ownership_tbls = {}
        self.user_league_standing_tbls = {}
        self.user_league_ownership_graphs = {}

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
        i = 0
        from pprint import pprint
        for user in users:
            i += 1
            user_players.append([player["element"] for player in user["picks"]])
        
            # print("")
            # pprint(user["picks"])
        user_players = np.array(user_players).ravel()
        pprint(user_players)
        unique, count = np.unique(user_players, return_counts=True)
        league_player_tbl = (
            pd.DataFrame(
                {"player": unique, "count": count, "ownership (%)": 100 * count / n}
            )
            .replace({"player": get_player_id_dict()})
            .sort_values("count", ascending=False)
        )
        return league_player_tbl

    def generate_summary(self):
        """
        method to create top n
        Parameters
        ----------
        `param1 (type)`:

        Return
        ------
        `return`:

        """

        self._general_summary_flag = True

        # get bootstrap dataframe
        self.teams_id_dict = get_team_id_dict()
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
            "selected_by_percent": "ownership (%)",
            "transfers_in_event": "transfers in event",
            "transfers_out_event": "transfers out event",
        }

        self.gk_fields = [
            "saves",
            "saves_per_90",
            "clean_sheets",
            "clean_sheets_per_90",
        ]
        self.def_fields = [
            "clean_sheets",
            "clean_sheets_per_90",
        ]
        bootstrap_df["full_name"] = (
            bootstrap_df["first_name"] + " " + bootstrap_df["second_name"]
        )

        # -- bootstrap dataframme cleanup -- #
        self.bootstrap_df = (
            bootstrap_df.rename(columns=dict(**core_fields_dict, **always_fields_dict))
            .astype({"ownership (%)": float})
            .replace({"team": self.teams_id_dict, "position": POS_DICT})
            .assign(price=lambda x: x["price"] / 10)
        )

        self.core_fields = list(core_fields_dict.values())
        self.always_fields = list(always_fields_dict.values())

        # Positions
        self.pos_list = list(POS_DICT.values())

    def generate_top_players(self, n: int = 1000):
        """

        Parameters
        ----------
        `n (int)`: number of top players to find, for example if 1000 then will extract data for top 1000 ranked players

        Return
        ------
        `None`

        """
        self._top_players_flag = True
        self.overall_top_n_tbl = self._get_league_player_ownership(314, n)
        self.overall_top_n_bar = px.bar(
            self.overall_top_n_tbl.head(30),
            # self.overall_top_n_tbl.query("count > 50"),
            x="player",
            y="ownership (%)",
            title=f"Top {n} ownership",
        )
        self.n = n


    def generate_player_analysis(self, players: Optional[List[str]]) -> None:
        """
        Method to generate analysis information of premier league players

        Parameters
        ----------
        `players (List[str])`: list of players to perform analysis on

        Return
        ------
        `None`

        """
        ...

    def generate_leagues(self, id: Optional[List[int]] = None):
        """
        Method to generate information on leagues

        Parameters
        ----------
        `id (List[int])`: player id to get league information

        Return
        ------
        `None`

        """
        self._leagues_generated_flag = True
        league_ids = get_manager_leagues_id(id)
        league_data = get_league_data(league_ids)

        for data in league_data:
            league_name = data["league"]["name"]
            league_id = data["league"]["id"]
            print(league_name)
            self.user_league_standing_tbls[league_name] = pd.DataFrame(
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
            self.user_league_ownership_graphs[league_name] = px.bar(
                tbl,
                # tbl.head(50),
                x="player",
                y="ownership (%)",
                title=f"{league_name} ownership",
            )
            self.user_league_ownership_tbls[league_name] = tbl

        return None

    def _build_tabs(self) -> None:

        if self._general_summary_flag:
            self.tab["overall_summary"] = dcc.Tab(
                label="Overall Summary",
                value="overall_summary",
                children=html.Div(
                    [
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
                        dash_table.DataTable(id="user_league_table", page_size=10),
                        dcc.Graph(id="league_ownership_bar"),
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
        print(list(self.tab.values())[0].value)
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

        if hasattr(self, "overall_top_n_tbl"):

            @self.app.callback(
                [Output("summary_dt", "data"), Output("summary_dropdown", "value")],
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
                df_out = self.bootstrap_df[
                    self.always_fields + [dd_feature]
                ].sort_values(by=dd_feature, ascending=not sum_bs)
                df_out.insert(0, "rank", range(1, self.bootstrap_df.shape[0] + 1))

                # -- positional filtering -- #
                idx = df_out["position"].isin(dd_pos)
                df_out = df_out[idx]

                return [df_out.to_dict("records"), dd_feature]

        if self._leagues_generated_flag:
            @self.app.callback(
                [
                    Output("user_league_table", "data"),
                    Output("league_ownership_bar", "figure"),
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
                dd_value = _dropdown(
                    league_name, self.league_options, ctx, "prev_btn_ul", "next_btn_ul"
                )

                return [
                    self.user_league_standing_tbls[dd_value].to_dict("records"),
                    self.user_league_ownership_graphs[league_name],
                    dd_value,
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
        self.generate_top_players(n=top_n)
        self.generate_leagues(id=user_id)

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
            "https://codepen.io/chriddyp/pen/bWLwgP.css",
            {
                "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
                "rel": "stylesheet",
                "integrity": "sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
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
        """Function to run dashboard

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


if __name__ == "__main__":
    from pprint import pprint
    import pickle
    # Tunde user id
    tunde_id = 5770588
    rpt = FPLReport()

    # rpt.generate_leagues(tunde_id)

    # pprint(data)

    rpt.full_report(top_n=100, user_id=tunde_id)
    rpt.run(debug=True, open_window=False)

