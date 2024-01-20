# %%

from FPL.src import FPLReport, get_user_leagues_id

# from FPL.utils.Manager import Manager

if __name__ == "__main__":

    refresh = 60
    tunde_id = 5770588

    rpt = FPLReport()

    rpt.full_report(tunde_id, 1_000)

    local_host = {"host": "127.0.0.1", "port": 8080}
    rpt.run(**local_host)
