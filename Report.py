# %%
import webbrowser
from typing import Dict, Optional

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
    get_top_users_id,
    get_users,
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
        top_user_id = get_top_users_id(n)

    def generate_leagues(self, id: int = None):
        """

        Parameters
        ----------
        `id (int)`: TODO: maybe need this

        Return
        ------
        `return`:

        """
        ...

    def _build_tabs(self) -> None:
        if hasattr(self, "bootstrap_df"):
            self.tab["overall_summary"] = dcc.Tab(
                label="Overall Summary",
                value="Overall_Summary",
                children=html.Div(
                    [
                        html.H2("Feature"),
                        dcc.Dropdown(
                            options=self.core_fields,
                            value=self.core_fields[0],
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
                if self.core_fields.index(dd_feature) == 0:
                    dd_feature = self.core_fields[-1]
                else:
                    dd_feature = self.core_fields[
                        self.core_fields.index(dd_feature) - 1
                    ]
            elif ctx.triggered[0]["prop_id"] == "next_btn.n_clicks":
                if self.core_fields.index(dd_feature) == len(self.core_fields) - 1:
                    dd_feature = self.core_fields[0]
                else:
                    dd_feature = self.core_fields[
                        self.core_fields.index(dd_feature) + 1
                    ]

            # -- Filter data to relevant features -- #
            df_out = self.bootstrap_df[self.always_fields + [dd_feature]].sort_values(
                by=dd_feature, ascending=not sum_bs
            )
            df_out.insert(0, "rank", range(1, self.bootstrap_df.shape[0] + 1))

            # -- positional filtering -- #
            idx = df_out["position"].isin(dd_pos)
            df_out = df_out[idx]

            return [df_out.to_dict("records"), dd_feature]

    def _prepare_run(self) -> None:
        """
        Function that creates dash app object and runs all necessary helper functions to build the app

        Return
        ------
        `None`

        """
        from dash import Dash, html

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
            webbrowser.open_new(url=f"http://{host}:port/")

        self.app.run(host=host, port=port, debug=debug)


# %%
# team_dict = get_team_id_dict()
rpt = FPLReport(3)
rpt.generate_summary()
rpt.run(debug=True, open_window=False)
# rpt.run(open_window=True)


# %% bootstrap dataframe analysis

if __name__ != "__main__":
    # %%
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

# %%
