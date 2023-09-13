import importlib
import pickle
from pprint import pprint

from FPL.src import FPLReport

if __name__ == "__main__":
    # Tunde user id
    rpt = FPLReport()

    # rpt.generate_leagues(tunde_id)

    # pprint(data)

    tunde_id = 5770588
    # rpt.generate_player_analysis([10, 13, 131, 99])
    # pprint(rpt.recent_df.columns)
    # pprint(rpt.player_analysis_list)
    # pprint(rpt.recent_df["round"])
    # pprint(rpt.upcoming_fixtures_df)
    # rpt.generate_leagues(tunde_id)
    
    

    rpt.full_report(top_n=500, user_id=tunde_id)
    rpt.run(debug=True, open_window=False)
