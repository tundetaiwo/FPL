#%%###########
## Imports  ##
##############

import importlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import requests

# from helper.helper_fns import get_data
import src.helper_fns as helper
from Definitions import SUBWAY_LEAGUE

#%%
importlib.reload(helper)
gameweek = 24
user_id = 2960212
fpl_class = helper.Fantasy(gameweek)

# fpl_class.get_top_users(500)
# fpl_class.top_n_teams.element.value_counts()
# fpl_class.top_n_transfers_in
# fpl_class.get_user(user_id)
fpl_class.recent_form()
# %%
window = 5
response = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{13}/")
recent_form_df = pd.DataFrame(json.loads(response.content)["fixtures"])

recent_form_df.query(f"round > {fpl_class.current_gw - window}").total_points.mean()
# %%
