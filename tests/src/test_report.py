import pytest

from FPL.src import FPLReport
from FPL.src.players import get_player_info


class TestGetPlayerInfo:
    rpt = FPLReport()

    def test_get_player_info_bad_name(self):
        with pytest.raises(ValueError):
            self.rpt.generate_player_analysis(["False Name"])

    def test_get_player_info_bad_id(self):
        with pytest.raises(
            ValueError,
            match="IDs in list do not lie within id dictionary, please consult with get_player_id_dict method.",
        ):
            self.rpt.generate_player_analysis([12_123])

    def test_get_player_info_bad_mix(self):
        with pytest.raises(
            ValueError,
            match="IDs must be either all strings or all integers.",
        ):
            self.rpt.generate_player_analysis([121, "Kevin Debruyne"])
