import pytest

from FPL.src.players import get_player_info


class TestGetPlayerInfo:
    def test_get_player_info_bad_name(self):
        with pytest.raises(ValueError):
            get_player_info(["False Name"])

    def test_get_player_info_bad_id(self):
        with pytest.raises(
            ValueError,
            match="IDs in list do not lie within id dictionary, please consult with get_player_id_dict method.",
        ):
            get_player_info([12_123])

    def test_get_player_info_bad_mix(self):
        with pytest.raises(
            ValueError,
            match="IDs must be either all strings or all integers.",
        ):
            get_player_info([121, "Kevin Debruyne"])
