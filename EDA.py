# %%
import webbrowser
from typing import Dict

import dash_daq as daq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback_context, dash_table, dcc, html

from FPL.src import (
    basic_player_df,
    get_player_id_dict,
    get_player_info,
    get_team_id_dict,
)
from FPL.utils import POS_DICT, _get_api_url, fetch_request
from tools.get_lan_ip import get_lan_ip


# %%
class EDA_FPL:
    def __init__(self, gw: int):
        self.gw: int = gw
        self.app: Dash = None

        self.tab: dict = {}
        self.bootstrap_plots: dict = {}

    def create_top_n(self):
        """
        method to create top n
        Parameters
        ----------
        `param1 (type)`:

        Return
        ------
        `return`:

        """

        # get bootstrap dataframe
        self.teams_id_dict = get_team_id_dict()
        # TODO: delete??
        bootstrap_df: pd.DataFrame = basic_player_df()
        self.bootstrap_features = [
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
        bootstrap_df["full_name"] = (
            bootstrap_df["first_name"] + " " + bootstrap_df["second_name"]
        )
        self.bootstrap_df = bootstrap_df.rename(
            columns={"element_type": "position"}
        ).replace({"team": self.teams_id_dict, "position": POS_DICT})

        # Positions
        self.pos_list = list(POS_DICT.values())

    def _build_tabs(self) -> None:
        if hasattr(self, "bootstrap_df"):
            self.tab["overall_summary"] = dcc.Tab(
                label="Overall Summary",
                value="Overall_Summary",
                children=html.Div(
                    [
                        html.H2("Feature"),
                        dcc.Dropdown(
                            options=self.bootstrap_features,
                            value=self.bootstrap_features[0],
                            id="summary_dropdown",
                        ),
                        html.Button("<- Prev", id="prev_btn", n_clicks=0),
                        html.Button("-> Next", id="next_btn", n_clicks=0),
                        daq.BooleanSwitch(id="summary_boolswitch", on=True),
                        html.H2("Position"),
                        dcc.Dropdown(
                            options=self.pos_list,
                            value=self.pos_list,
                            id="summary_pos_dd",
                            multi=True,
                        ),
                        html.Br(),
                        dash_table.DataTable(id="summary_dt"),
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
        self.app.layout = html.Div([tab for tab in self.tab.values()])

    def _build_callback_fns(self) -> None:
        """
        Function to call all available callback functions

        Return
        ------
        `None`

        """

        @self.app.callback(
            [Output("summary_dt", "data"), Output("summary_dropdown", "value")],
            [
                Input("summary_dropdown", "value"),
                Input("summary_pos_dd", "value"),
                Input("prev_btn", "n_clicks"),
                Input("next_btn", "n_clicks"),
                Input("summary_boolswitch", "on"),
            ],
        )
        def _create_weekly_summary(dd_feature, dd_pos, prev_btn, next_btn, sum_bs):
            # -- button functionality -- #
            ctx = callback_context
            if ctx.triggered[0]["prop_id"] == "prev_btn.n_clicks":
                if self.bootstrap_features.index(dd_feature) == 0:
                    dd_feature = self.bootstrap_features[-1]
                else:
                    dd_feature = self.bootstrap_features[
                        self.bootstrap_features.index(dd_feature) - 1
                    ]
            elif ctx.triggered[0]["prop_id"] == "next_btn.n_clicks":
                if (
                    self.bootstrap_features.index(dd_feature)
                    == len(self.bootstrap_features) - 1
                ):
                    dd_feature = self.bootstrap_features[0]
                else:
                    dd_feature = self.bootstrap_features[
                        self.bootstrap_features.index(dd_feature) + 1
                    ]

            # -- positional filtering -- #
            df_out = self.bootstrap_df[
                ["first_name", "second_name", "position"] + [dd_feature]
            ].sort_values(by=dd_feature, ascending=not sum_bs)

            idx = df_out["position"].isin(dd_pos)
            df_out = df_out[idx]

            # print(df_out.head())
            return [df_out.to_dict("records"), dd_feature]

    def _prepare_run(self) -> None:
        """
        Function that creates dash app object and runs all necessary helper functions to build the app

        Return
        ------
        `None`

        """
        self.app = Dash(__name__)
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
            webbrowser.open_new_tab(url=f"{host}: port")

        self.app.run(host=host, port=port, debug=debug)


# %%
team_dict = get_team_id_dict()
rpt = EDA_FPL(3)
rpt.create_top_n()
rpt.run(debug=True, open_window=False)


# %% bootstrap dataframe analysis

if __name__ != "__main__":
    # pd.to_pickle(get_player_info(), "./player_info.pkl")
    player_info = pd.read_pickle("./player_info.pkl")
    # # %% load in data
    url = _get_api_url("bootstrap", gameweek=3)
    tmp = fetch_request(url)
    keys = list(tmp.keys())
    print(ele := keys[5])

    df = pd.DataFrame(tmp["elements"])
    # %%
    for col in df.columns.sort_values():
        print(col)
    # %%
    df["element_type"].value_counts()
    df["pos"] = df["element_type"].replace(POS_DICT)
    df["pos"]
