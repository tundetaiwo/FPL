import datetime

from FPL.utils import _get_api_url, fetch_request


def get_current_gw() -> int:
    """
    Function to call FPL API and get the most recent gameweek

    Return
    ------
    `int`: most recent game week

    """

    url = _get_api_url(key="bootstrap")
    data = fetch_request(url)

    current_time = datetime.datetime.now()

    for gameweek in data["events"]:
        deadline_time = datetime.datetime.strptime(
            gameweek["deadline_time"], "%Y-%m-%dT%H:%M:%SZ"
        )
        if deadline_time > current_time:
            current_gameweek = gameweek["id"] - 1
            break

    print(f"current gameweek is {current_gameweek}.")

    return current_gameweek
