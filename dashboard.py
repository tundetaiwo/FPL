#%%
import numpy as np
import pandas as pd
import plotly
from dash import Dash, html

import src.helper_fns as helper

app = Dash()
app.title = "Fantasy Football Dashboard"
app.layout = html.Div()
app.run()

#%%
