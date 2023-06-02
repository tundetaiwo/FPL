import pytest

from ..src import helper_fns


@pytest.fixture
def gameweek():
    return 23


# TODO: test fantasy as a class
def test_fantasy():
    helper_fns.Fantasy(gameweek)
