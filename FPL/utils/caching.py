import os
import pickle
import time
from typing import Callable


def dir_cache(
    refresh: int = 30, cache_dir: str = "./.cache"
) -> Callable:
    """

    Parameters
    ----------
    `refresh (int)`: time (minutes) to check since last save, default=30

    `cache_dir (str)`: directory to cache results, defualt="./.cache"

    Return
    ------
    `Callable`

    """
    def _wrapper_func(func):
        def _wrapper_inner(*args, **kwargs):
            cache_file = f"{cache_dir}/{func.__name__}_result.pkl"

            # Try to read from cache
            print(refresh)
            print(os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < (refresh * 60))

            if os.path.exists(cache_file) and (
                time.time() - os.path.getctime(cache_file)
            ) < (refresh * 60):
                # modification_time = os.path.getmtime(cache_file)
                with open(cache_file, "rb") as f:
                    result = pickle.load(f)
            else:
                # If cache doesn't exist, run the function and save the result
                result = func(*args, **kwargs)
                with open(cache_file, "wb") as f:
                    pickle.dump(result, f)
            return result

        return _wrapper_inner
    return _wrapper_func


def clear_dir_cache(cache_dir: str="./.cache"):
    """
    function to clear cache folder
    
    Parameters
    ----------
    `cache_dir (str)`: folder path to cache directory
    
    Return
    ------
    `None`
    
    """
    if not os.path.isdir(cache_dir):
        raise ValueError(f"{cache_dir} is not a directory.")
    
    for file in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, file)
        if file_size := os.path.getsize(file_path) > 10**6:
            del_flag = input(
                f"Are you sure you want to delete {file_path} {file_size=}"
            )
            if del_flag:
                os.remove(file_path)
        else:
            os.remove(file_path)

