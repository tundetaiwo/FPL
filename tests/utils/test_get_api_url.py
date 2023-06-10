import pytest

from FPL.utils._get_api_url import _get_api_url


class TestGetAPIUrl:
    def test_invalid_key(self):
        with pytest.raises(ValueError):
            _get_api_url(key="invalid")

    def test_invalid_gameweek(self):
        with pytest.raises(ValueError):
            _get_api_url(key="gameweek", gameweek=0)

    def test_invalid_id(self):
        with pytest.raises(ValueError):
            _get_api_url(key="element", id="id")

    def test_invalid_gameweek_id1(self):
        with pytest.raises(ValueError):
            _get_api_url(key="picks", id="id", gameweek=-10)

    def test_invalid_gameweek_id2(self):
        with pytest.raises(ValueError):
            _get_api_url(key="picks", id=100, gameweek=-10)

    def test_invalid_gameweek_id3(self):
        with pytest.raises(ValueError):
            _get_api_url(key="picks", id="id", gameweek=10)
