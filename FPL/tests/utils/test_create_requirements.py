import os
import subprocess

import pytest

# from ...Definitions import SOURCE_DIR
from ...utils import create_requirements


class TestCreateRequirements:
    def test_created_text_files(self):
        SOURCE_DIR = os.path.abspath("./")
        print(SOURCE_DIR)
        path_unix = f"{SOURCE_DIR}/requirements_test_unix.txt"
        path_win = f"{SOURCE_DIR}/requirements_test_win.txt"

        write_names = ["test_win", "test_unix"]
        try:
            create_requirements(folder=SOURCE_DIR, os_names=write_names)
            assert os.path.exists(path_unix)
            assert os.path.exists(path_win)
        finally:
            os.remove(path_unix)
            os.remove(path_win)

    def test_isdir_error(self):
        SOURCE_DIR = "../.."
        folder = f"{SOURCE_DIR}/main.py"
        with pytest.raises(ValueError):
            create_requirements(folder)

    def test_create_requirements(self):
        pass
