# %%
import asyncio
import json

import aiohttp
import lightgbm as lgbm
import pandas as pd
import plotly.express as px
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

# %%
train_data = pd.read_pickle("./data/train_data.pkl")
test_data = pd.read_pickle("./data/test_data.pkl")

X_train, y_train = train_data.drop(columns="total_points"), train_data["total_points"]
X_test, y_test = test_data.drop(columns="total_points"), test_data["total_points"]
# %%
params = {
    "objective": "regression",
    "metric": "mse",
    "boosting_type": "gbdt",
    "num_leaves": 31,
}

cat_features = ["position", "name", "team"]
mdl = lgbm.LGBMRegressor(**params)
mdl.fit(X_train, y_train, categorical_feature=cat_features)

# %%
preds = mdl.predict(X_test.query(""))
px.histogram(preds)
# %%
print(f"MAE: {mean_absolute_error(preds, y_test)}")
print(f"MSE: {mean_squared_error(preds, y_test)}")

# %%
