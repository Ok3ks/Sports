from src.utils import (
    to_json,
    check_gw,
    Participant,
    League,
    GameweekError,
)
import pytest
from os.path import join
import os


def test_to_json(transfer_obj, filepath):
    output_name = "test.json"
    to_json(transfer_obj, join(filepath, output_name))
    assert output_name in os.listdir(filepath)


def test_get_basic_stats(values):
    pass


def test_parse_transfers(transfer_obj):
    pass


@pytest.mark.parametrize("correct_gw", [10])
@pytest.mark.parametrize("wrong_gw", [40])
def test_check_gw(wrong_gw, correct_gw):
    assert check_gw(correct_gw) == (True, correct_gw), "Only 38 games in a season"
    assert check_gw(wrong_gw) == (False, None), "Only 38 games in a season"


def test_get_participant_entry(participant, gw_fixture, mocker):
    from src import utils
    spy = mocker.spy(utils, "get_participant_entry")

    utils.get_participant_entry(participant, gw_fixture)
    assert spy.call_count == 1
    assert list(spy.spy_return.keys()) == [
        "auto_sub_in",
        "auto_sub_out",
        "gw",
        "entry_id",
        "active_chip",
        "points_on_bench",
        "total_points",
        "event_transfers_cost",
        "players",
        "bench",
        "vice_captain",
        "captain"
    ]

def test_get_curr_event(mocker):
    from src import utils
    
    spy = mocker.spy(utils, "get_curr_event")
    curr_event = utils.get_curr_event()

    assert spy.call_count == 1
    assert len(spy.spy_return) == 2
    assert spy.spy_exception == None


class TestParticipant:
    def test_init(
        self,
        participant,
    ):
        pass

    def test_get_gw_transfers(self):
        pass

    def test_get_span_week_transfers(self):
        pass

    def test_get_all_week_transfers(self):
        pass

    @pytest.mark.parametrize("gameweek_list,gameweek_int", [([1, 10, 39], [13])])
    def test_get_all_week_entries_incl_invalid(
        self, participant, gameweek_list, gameweek_int
    ):
        test = Participant(participant, gameweek_int)

        with pytest.raises(GameweekError):
            test.get_all_week_entries(gameweek_list)


class TestLeague:

    def test_init(self, classic_league):
        test = League(classic_league)
        assert test.league_id == 1491605
        assert test.participants == []
        assert test.PAGE_COUNT == 1

    def test_league_obtain_league_participants(
        self, classic_league, league_fill_fixture
    ):
        test = League(classic_league)
        test.participants = league_fill_fixture

        obj = test.obtain_league_participants()
        keys = set(
            [
                "entry",
                "entry_name",
                "id",
                "event_total",
                "player_name",
                "rank",
                "last_rank",
                "rank_sort",
                "total",
            ]
        )

        diff = keys.difference(test.participants[0].keys())
        assert (
            keys.intersection(test.participants[0].keys()) == keys
        ), f"Vital keys missing, Add keys -  {diff}"

        assert len(test.participants) == len(obj)
        assert type(test.participants) == list

        assert test.entry_ids != None
        assert type(test.entry_ids) == list

    def test_league_get_participant_name(self, classic_league, league_fill_fixture):
        test = League(classic_league)
        test.participants = league_fill_fixture
        names = test.get_participant_name()

        assert "entry" in test.participants[0].keys()
        assert "entry_name" in test.participants[0].keys()

        assert type(list(test.participant_name.values())[0]) == str
        assert type(names) == dict


    def test_league_get_gw_transfers(self):
        pass


if __name__ == "__main__":
    print("use pytest --sw to run tests")
