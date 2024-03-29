from typing import Optional


def _get_api_url(
    key: str,
    id: Optional[int] = None,
    gameweek: Optional[int] = None,
    page: int = 1,
) -> str:
    """
    Function to retrieve urls for fantasy football api

    Parameters
    ----------
    `key (str)`: key to pass to fantasy football api dictionary

    `id (int)`: id value to be passed when key is "entry", "element", "history", "transfers", "standings" and "picks"

    `gameweek (int)`: gameweek value to be passed when key is "gameweek" or "picks". Must be between 1 and 38

    `page (int)`: page to look for in leauge (50 managers per page), default=1

    Notes
    -----
    id:
        `element`: Remaining fixtures left for PL player as well as previous fixtures and seasons
        `entry`: Basic info on FPL Manager\n
        `history`: A summary of a FPL Manager for each GW up until the current GW. The past season results of a FPL Manager. The chips a FPL Manager has played"\n
        `transfers`: All transfers of given team ID\n
        `standings`: Information about league with id LID such as name and standings. Add ?page_standings={P} for leagues\n
    static:
        `bootstrap`: Main URL for all premier league players, teams, global gameweek summaries\n
        `fixtures`: A list of all 380 matches that will happen over the season\n
        `picks`: Squad information for given manager ID and gameweek\n

    Return
    ------
    `str`: url of api requested


    TODO: refactor so it's DRY for gameweek_id dict
    """

    static_dict = {
        # Main URL for all premier league players, teams, global gameweek summaries"
        "bootstrap": "https://fantasy.premierleague.com/api/bootstrap-static/",
        # A list of all 380 matches that will happen over the season
        "fixtures": "https://fantasy.premierleague.com/api/fixtures/",
    }
    id_dict = {
        # Remaining fixtures left for PL player as well as previous fixtures and seasons
        "element": f"https://fantasy.premierleague.com/api/element-summary/{id}/",
        # Basic info on FPL Manager
        "entry": f"https://fantasy.premierleague.com/api/entry/{id}/",
        # A summary of a FPL Manager for each GW up until the current GW. The past season results of a FPL Manager. The chips a FPL Manager has played"
        "history": f"https://fantasy.premierleague.com/api/entry/{id}/history/",
        # All transfers of given team ID
        "transfers": f"https://fantasy.premierleague.com/api/entry/{id}/transfers/",
    }
    gameweek_dict = {
        # Stats of all PL players that played in GW
        "gameweek": f"https://fantasy.premierleague.com/api/event/{gameweek}/live/",
    }
    gameweek_id_dict = {
        # Squad picks of team LID for week GW. Both TID and GW should be numeric
        "picks": f"https://fantasy.premierleague.com/api/entry/{id}/event/{gameweek}/picks/",
    }
    standings_dict = {
        # Information about league with id such as name and standings. Add ?page_standings={P} for leagues
        "standings": f"https://fantasy.premierleague.com/api/leagues-classic/{id}/standings/?page_new_entries=1&page_standings={page}&phase=1",
    }
    if key in static_dict:
        return static_dict[key]
    elif key in id_dict:
        if not isinstance(id, int):
            raise ValueError(f"For {key=}, must pass id value that's an integer.")

        return id_dict[key]
    elif key in gameweek_dict:
        if not isinstance(gameweek, int):
            raise ValueError(f"For {key=}, must pass gamweek value that's an integer")
        if gameweek < 1 or gameweek > 38:
            raise ValueError(
                f"gameweek must be between 0 and 38. Current Value: {gameweek}"
            )
        return gameweek_dict[key]
    elif key in standings_dict:
        if not isinstance(page, int):
            raise ValueError(f"For {key=}, must pass page value that's an integer")

        return standings_dict[key]
    elif key in gameweek_id_dict:
        if not isinstance(id, int):
            raise ValueError(f"For {key=} must pass, id value that's an integer.")
        if not isinstance(gameweek, int):
            raise ValueError(f"For {key=} Must pass, gamweek value that's an integer")
        if gameweek < 1 or gameweek > 38:
            raise ValueError(
                f"gameweek must be between 0 and 38. Current Value: {gameweek}"
            )
        return gameweek_id_dict[key]

    else:
        valid_keys = (
            list(id_dict.keys())
            + list(gameweek_dict.keys())
            + list(gameweek_id_dict.keys())
        )
        raise ValueError(f"key argument must be one of {valid_keys}")
