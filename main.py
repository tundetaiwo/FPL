# %%

from FPL.src import FPLReport, get_user_leagues_id
from FPL.src import FPLReport

# from FPL.utils.Manager import Manager

if __name__ == "__main__":

    refresh = 60
    tunde_id = 2352647
    top_n = 1_000

    rpt = FPLReport()

    rpt.full_report(tunde_id, 1_000)

    local_host = {"host": "127.0.0.1", "port": 8080}
    rpt.run(**local_host)
