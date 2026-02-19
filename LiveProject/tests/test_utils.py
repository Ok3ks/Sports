from src.utils import (
    get_basic_stats,
    get_curr_event,
    get_gw_transfers,
    parse_transfers,
    check_gw,
)
import pytest



@pytest.mark.parametrize("correct_gw", [10])
@pytest.mark.parametrize("wrong_gw", [40])
def test_check_gw(wrong_gw, correct_gw):
    assert check_gw(correct_gw) == (True, correct_gw), "Only 38 games in a season"
    assert check_gw(wrong_gw) == (False, None), "Only 38 games in a season"


@pytest.mark.parametrize("gw_span", [[10, 12]])
def test_check_gw_span(gw_span):
    assert check_gw(gw_span) == (True, gw_span)


def test_get_basic_stats_integers():
    data = [1, 2, 3, 4, 5, 6, 7]

    q1, average, q3 = get_basic_stats(data)
    assert q1 == 2.5
    assert average == 4.0
    assert q3 == 5.5


def test_get_basic_stats_empty():
    q1, average, q3 = get_basic_stats([])
    assert q1 is None
    assert average is None
    assert q3 is None


def test_parse_transfers(transfer_obj):
    obj = parse_transfers(transfer_obj, {})
    entry_id = transfer_obj["entry"]
    assert entry_id in obj.keys()
    assert "element_in", "element_out" in obj[entry_id].keys()


def test_get_gw_transfers_one(participant):
    transfers = get_gw_transfers([participant], 3)
    assert len(transfers.keys()) == 1
    assert list(transfers[participant].keys()) == ["element_in", "element_out"]


def test_get_gw_transfers_span(participant, span_fixture):
    transfers = get_gw_transfers([participant], span_fixture)
    assert set(transfers.keys()).intersection(transfers.keys()) == set(transfers.keys())


def test_get_gw_transfers_all(participants):
    transfers = get_gw_transfers(participants, all=True)
    assert len(transfers.keys()) == get_curr_event()[0] - 1


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
    utils.get_curr_event()

    assert spy.call_count == 1
    assert len(spy.spy_return) == 2


if __name__ == "__main__":
    print("use pytest --sw to run tests")
