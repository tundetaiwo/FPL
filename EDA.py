import plotly.express as px


columns = ['first_name', 'second_name', 'points_per_game', 'total_points',
           'now_cost', 'transfers_in','transfers_out', 'selected_by_percent'']
players_df.sort_values(by=['total_points'], inplace=True)
px.bar(players_df, x='first_name', y='')