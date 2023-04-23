#%%
import plotly.express as px

from main import get_data

players_df, fixtures_df, gameweek = get_data()

players_df.sort_values(
    by="total_points", ascending=False, inplace=True, ignore_index=True
)
columns = [
    "first_name",
    "second_name",
    "points_per_game",
    "total_points",
    "now_cost",
    "transfers_in",
    "transfers_out",
    "selected_by_percent",
]


forwards_df = players_df.loc[players_df.element_type == 4]
mid_df = players_df.loc[players_df.element_type == 3]
def_df = players_df.loc[players_df.element_type == 2]
gk_df = players_df.loc[players_df.element_type == 1]
#%%
gk_df[["second_name", "total_points", "now_cost"]].head(20)
#%%
forwards_df[["second_name", "total_points", "now_cost"]].head(20)
(
    forwards_df[["second_name", "total_points", "now_cost"]]
    .loc[forwards_df.now_cost <= 45]
    .head(20)
)
#%%
def_df[["second_name", "total_points", "now_cost"]].head(20)
(
    def_df[["second_name", "total_points", "now_cost"]]
    .loc[def_df.now_cost <= 40]
    .head(20)
)
#%%
mid_df[["second_name", "total_points", "now_cost"]].head(20)
(
    mid_df[["second_name", "total_points", "now_cost"]]
    .loc[mid_df.now_cost <= 80]
    .head(20)
)
#%%
px.bar(gk_df.head(50), x="second_name", y="total_points")
