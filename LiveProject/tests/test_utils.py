from LiveProject.src.utils import (
    get_basic_stats,
    get_gw_transfers,
    parse_transfers,
    get_participant_entry,
    to_json,
)
import pytest

from os.path import join
import os
import json

from LiveProject.src.utils import (
    check_gw,
    Participant,
    get_curr_event,
    League,
    GameweekError,
)
from LiveProject.src.urls import FPL_URL
import requests


def test_to_json(transfer_obj, filepath):
    output_name = "test.json"
    to_json(transfer_obj, join(filepath, output_name))
    assert output_name in os.listdir(filepath)


def test_from_json(filepath):
    output_name = "test.json"
    with open(join(filepath, output_name), "r") as ins:
        obj = json.load(ins)
    assert type(obj) == dict


def test_get_basic_stats(values):
    pass


def test_parse_transfers(transfer_obj):
    pass


def test_check_gw_int_is_true(gw_fixture):
    pass


def test_check_gw_span_is_true(span_fixture):
    pass


@pytest.mark.parametrize("diff_fixture", [40])
def test_check_gw_is_false(diff_fixture):
    assert check_gw(diff_fixture) == None, "Only 38 games in a season"


def test_get_curr_event():
    r = requests.get(FPL_URL)
    assert (
        r.status_code == 200
    ), "Endpoint unavailable, check participant_id and gameweek"

    r = r.json()
    assert type(r) == dict
    assert "events" in r.keys()

    check_set = r["events"][0]
    inter_ = set(["finished", "data_checked", "id", "is_current"])

    assert inter_.intersection(check_set) == inter_


def test_get_diff_gw_transfers(participant, span_fixture):
    row = get_gw_transfers([participant], span_fixture)
    assert list(row[span_fixture[0]].keys())[0] == participant
    assert set(row.keys()).union(set(span_fixture)) == set(span_fixture)


def test_get_all_gw_transfers(participant, span_fixture):
    row = get_gw_transfers([participant], span_fixture, all=True)
    keys = list(row.keys())

    start = keys[-1]
    end = keys[0]
    rang = [i for i in range(start, end + 1)]

    assert set(row.keys()).union(rang) == set(rang)


def test_get_participant_entry(participant, gw_fixture):
    pass


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

    @pytest.mark.parametrize("gameweek_list,gameweek_int", [([3, 10], 8)])
    def test_get_all_week_entries(self, participant, gameweek_list, gameweek_int):
        test = Participant(participant, gameweek_int)
        test_list = test.get_all_week_entries(gameweek_list)
        test_int = test.get_all_week_entries(gameweek_int)

        assert len(test_list) == len(gameweek_list)
        assert len(test_int) == gameweek_int

    @pytest.mark.parametrize("gameweek_list,gameweek_int", [([1, 10, 39], [13])])
    def test_get_all_week_entries_incl_invalid(
        self, participant, gameweek_list, gameweek_int
    ):
        test = Participant(participant, gameweek_int)

        with pytest.raises(GameweekError):
            test.get_all_week_entries(gameweek_list)


class TestLeague:
    def test_init(self, league_fixture):
        test = League(league_fixture)
        assert test.league_id == 538731
        assert test.participants == []
        pass

    def test_league_obtain_league_participants_empty(self):
        # Endpoint tests validates this
        pass

    def test_league_obtain_league_participants_fill(
        self, league_fixture, league_fill_fixture
    ):
        test = League(league_fixture)
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

    def test_league_get_participant_name(self, league_fixture, league_fill_fixture):
        test = League(league_fixture)
        test.participants = league_fill_fixture
        names = test.get_participant_name()

        assert "entry" in test.participants[0].keys()
        assert "entry_name" in test.participants[0].keys()

        assert type(list(test.participant_name.values())[0]) == str
        assert type(names) == dict

    def test_league_get_all_participant_entries(self, league_fixture):
        test = League(league_fixture)
        test_all_entries = test.get_all_participant_entries(10)
        # assert test_all_entries.__str__ is Generator

    def test_league_get_gw_transfers(self, league_fixture):
        pass


if __name__ == "__main__":
    print("use pytest to run tests")
