import os
import numpy as np
import pandas as pd
from FPL.utils.caching import clear_dir_cache, dir_cache
import pytest

@pytest.fixture
def data():
    n = 1000
    return pd.DataFrame(
        {
            "x1": np.random.randint(1, 1000, n),
            "x2": np.random.randint(1, 1000, n),
            "x3": np.random.randint(1, 1000, n),
            "x8": np.random.randint(2, 1000, n),
        }
    )
 
@pytest.fixture(scope="function")
def cache_dir():
    folder = "./.cache_folder_test"
    os.makedirs(folder, exist_ok=True)
    return folder

class TestCaching:

    def test_clear_dir_cache(self, cache_dir):
        clear_dir_cache(cache_dir=cache_dir)
        assert os.listdir(cache_dir) == []
        os.rmdir(cache_dir)

    def test_dir_cache(self, data, cache_dir):
        @dir_cache(cache_dir=cache_dir)
        def f():
            return data
        # run twice one to cache then to read in
        result = f()
        assert os.path.exists(f"{cache_dir}/")
        result_cached = f()
        assert result_cached == result




            