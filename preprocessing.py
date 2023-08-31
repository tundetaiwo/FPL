# %%
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

data = pd.read_csv("./data/2022-23/gws/merged_gw.csv")
data["kickoff_time"] = pd.to_datetime(data["kickoff_time"])

# %%
# TODO: will need  to extend for other years
# creating my own player dictionary as FPL one provided may be different each year
player_unique = data["name"].unique()
player_dict = {
    key: value for key, value in zip(player_unique, range(player_unique.shape[0]))
}

team_unique = data["team"].unique()
team_dict = {key: value for key, value in zip(team_unique, range(team_unique.shape[0]))}

position_unqiue = data["position"].unique()
position_dict = {
    key: value for key, value in zip(position_unqiue, range(position_unqiue.shape[0]))
}
# %% Preprocessing
data = data.drop(columns=["kickoff_time"]).replace(
    {"name": player_dict, "team": team_dict, "position": position_dict}
)
data
# %% Create train and test split
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(data):
    train_data, test_data = data.loc[train_idx], data.loc[test_idx]

train_data.to_pickle("./data/train_data.pkl")
test_data.to_pickle("./data/test_data.pkl")
