from ..src.urls import (
    GW_URL,
    FIXTURE_URL,
    TRANSFER_URL,
    HISTORY_URL,
    H2H_LEAGUE,
    LEAGUE_URL,
    FPL_PLAYER,
    FPL_URL,
)

import requests
from ..src.utils import to_json
from ...paths import MOCK_DIR


def test_gameweek_endpoint(gw_fixture):
    # digit greater than 1 less than 38
    gameweek_url = GW_URL.format(gw_fixture)
    assert gameweek_url == "https://fantasy.premierleague.com/api/event/1/live/"

    r = requests.get(gameweek_url)
    assert r.status_code == 200, f"{r.status_code} - Url invalid, or unavailable"
    r = r.json()
    assert "elements" in r.keys()

    assert type(r["elements"]) is list
    assert type(r["elements"][0]) is dict

    element_keys = list(r["elements"][0].keys())
    element_keys_prev = ["id", " stats ", " explain "]

    assert len(set(element_keys_prev).difference(element_keys)), " "
    del element_keys

    stats_keys = set(r["elements"][0]["stats"].keys())
    stats_keys_prev = [
        "mng_win",
        "mng_underdog_draw",
        "mng_loss",
        "mng_draw",
        "mng_goals_scored",
        "mng_underdog_win",
        "mng_clean_sheets",
        "minutes",
        "goals_scored",
        "assists",
        "clean_sheets",
        "goals_conceded",
        "own_goals",
        "penalties_saved",
        "penalties_missed",
        "yellow_cards",
        "red_cards",
        "saves",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "starts",
        "expected_goals",
        "expected_assists",
        "expected_goal_involvements",
        "expected_goals_conceded",
        "total_points",
        "in_dreamteam",
    ]

    assert len(stats_keys.difference(set(stats_keys_prev))) == 0, (
        f"Keys have changed {stats_keys.difference(set(stats_keys_prev))}"
    )

    del stats_keys
    explain_key = r["elements"][0]["explain"][0].keys()
    explain_key_prev = {"fixture", "stats"}

    assert len(set(explain_key).difference(explain_key_prev)) == 0, (
        "Explain keys have changed"
    )

    assert r["elements"][0]["explain"][0]["stats"][0]["identifier"] == "minutes"
    assert "points" in r["elements"][0]["explain"][0]["stats"][0]
    assert "value" in r["elements"][0]["explain"][0]["stats"][0]

    to_json(r, f"{MOCK_DIR}/endpoints/gameweek_endpoint.json")


def test_fixture_endpoint():
    r = requests.get(FIXTURE_URL)
    assert r.status_code == 200, "endpoint unavailable"
    r = r.json()

    assert type(r) is list
    assert type(r[0]) is dict

    fixture_keys = list(r[0].keys())
    fixture_key_prev = [
        "code",
        "event",
        "finished",
        "finished_provisional",
        "id",
        "kickoff_time",
        "minutes",
        "provisional_start_time",
        "started",
        "team_a",
        "team_a_score",
        "team_h",
        "team_h_score",
        "stats",
        "team_h_difficulty",
        "team_a_difficulty",
        "pulse_id",
    ]

    diff = set(fixture_key_prev).difference(fixture_keys)
    assert len(diff) == 0, "Fixture keys have changed"
    assert type(r[0]["stats"]) is list  # type:ignore
    del fixture_keys

    out_dict = {"fixture": r}
    to_json(out_dict, f"{MOCK_DIR}/endpoints/fixture_endpoint.json")


def test_transfer_endpoint(participant):
    """Tests transfer endpoint given a valid entry_id.
    Response is a list of transfers for previous gameweeks"""
    r = requests.get(TRANSFER_URL.format(participant))
    print(r.status_code)

    assert r.status_code == 200, "Endpoint unavailable"
    r = r.json()

    assert type(r) is list, "Endpoint structure has changed"
    # Transfers is empty if there's no transfer

    if len(r) > 1:
        transfer_keys = r[0].keys()
        transfer_keys_prev = [
            "element_in",
            "element_in_cost",
            "element_out",
            "element_out_cost",
            "entry",
            "event",
            "time",
        ]
        diff = set(transfer_keys_prev).difference(transfer_keys)

        assert len(diff) == 0, f"Transfer keys have changed {diff}"

    out_dict = {"transfer": r}
    to_json(out_dict, f"{MOCK_DIR}/endpoints/transfer_endpoint.json")


def test_history_endpoint(participant):
    """Extracts a players history for prior seasons given an id"""

    r = requests.get(HISTORY_URL.format(participant))
    assert r.status_code == 200, "Endpoint unavailable"
    r = r.json()

    assert type(r) is dict, "Endpoint structure has changed"
    history_keys = list(r.keys())
    history_keys_prev = ["current", "past", "chips"]

    assert len(set(history_keys_prev).difference(set(history_keys))) == 0, (
        "History keys have changed"
    )

    assert type(r["current"]) is list, "Endpoint structure has changed"  # type: ignore
    assert type(r["current"][0]) is dict, "Endpoint structure has changed"  # type: ignore

    assert type(r["past"]) is list, "Endpoint structure has changed"  # type: ignore
    assert type(r["past"][0]) is dict, "Endpoint structure has changed"  # type: ignore

    assert type(r["chips"]) is list, "Endpoint structure has changed"  # type: ignore

    current_keys = r["current"][0].keys()

    current_keys_prev = [
        "event",
        "points",
        "total_points",
        "rank",
        "rank_sort",
        "percentile_rank",
        "overall_rank",
        "bank",
        "value",
        "event_transfers",
        "event_transfers_cost",
        "points_on_bench",
    ]

    assert len(set(current_keys).difference(set(current_keys_prev))) == 0, (
        "Current keys has changed"
    )

    assert len(current_keys) == 12, "Number of keys has changed"

    # Add conditional ifs
    past_keys = r["past"][0].keys()
    past_keys_prev = ["season_name", "total_points", "rank"]

    assert len(set(past_keys).difference(past_keys_prev)) == 0, "Past keys have changed"

    # Chips is empty if it has not been used

    to_json(r, f"{MOCK_DIR}/endpoints/history_endpoint.json")


def test_h2h_league_endpoint(h2h_league):
    """"""

    r = requests.get(H2H_LEAGUE.format(h2h_league))
    assert r.status_code == 200

    r = r.json()
    assert type(r) is dict, "Endpoint Structure has changed"

    h2h_keys = list(r.keys())
    h2h_keys_prev = ["has_next", "page", "results"]

    assert len(set(h2h_keys_prev).difference(set(h2h_keys))) == 0, (
        "H2h keys have changed"
    )

    results_keys = list(r["results"][0].keys())
    results_keys_prev = [
        "id",
        "entry_1_entry",
        "entry_1_name",
        "entry_1_player_name",
        "entry_1_points",
        "entry_1_win",
        "entry_1_draw",
        "entry_1_loss",
        "entry_1_total",
        "entry_2_entry",
        "entry_2_name",
        "entry_2_player_name",
        "entry_2_points",
        "entry_2_win",
        "entry_2_draw",
        "entry_2_loss",
        "entry_2_total",
        "is_knockout",
        "league",
        "winner",
        "seed_value",
        "event",
        "tiebreak",
        "is_bye",
        "knockout_name",
    ]

    assert len(set(results_keys_prev).difference(results_keys)) == 0, (
        "Results keys has changed"
    )
    to_json(r, f"{MOCK_DIR}/endpoints/h2h_league_endpoint.json")


def test_league_endpoint(classic_league):
    page = 1
    r = requests.get(LEAGUE_URL.format(classic_league, page))

    assert r.status_code == 200
    r = dict(r.json())

    assert type(r) is dict
    keys = list(r.keys())

    keys_prev = ["new_entries", "last_updated_data", "league", "standings"]

    assert len(set(keys_prev).difference(keys)) == 0, "League Keys have changed"

    assert type(r["league"]) is dict  # type: ignore
    assert type(r["new_entries"]) is dict  # type: ignore
    assert type(r["standings"]) is dict  # type: ignore

    league_keys = r["league"]  # type: ignore
    league_keys_prev = [
        "id",
        "name",
        "created",
        "closed",
        "max_entries",
        "league_type",
        "scoring",
        "admin_entry",
        "start_event",
        "code_privacy",
        "has_cup",
        "cup_league",
        "rank",
    ]
    assert len(set(league_keys).difference(league_keys_prev)) == 0, (
        "League keys have changed"
    )

    new_entries_keys = r["new_entries"]  # type: ignore
    new_entries_keys_prev = ["has_next", "page", "results"]
    assert len(set(new_entries_keys).difference(new_entries_keys_prev)) == 0, (
        "New Entries keys have changed"
    )

    standings_keys = r["standings"]  # type: ignore
    standings_keys_prev = ["has_next", "page", "results"]

    assert len(set(standings_keys).difference(standings_keys_prev)) == 0, (
        " Standings have changed"
    )

    participant_info = r["standings"]["results"][0]  # type: ignore
    participant_info_keys = [
        "id",
        "event_total",
        "player_name",
        "rank",
        "last_rank",
        "rank_sort",
        "total",
        "entry",
        "entry_name",
    ]
    assert len(set(participant_info_keys).difference(participant_info)) == 0, (
        "Participant info keys have changed"
    )

    to_json(r, f"{MOCK_DIR}/endpoints/league_endpoint.json")


def test_fpl_player_endpoint(participant, gw_fixture):
    r = requests.get(FPL_PLAYER.format(participant, gw_fixture))
    assert r.status_code == 200, "Endpoint unavailable, check player_id and gameweek"

    r = r.json()
    assert type(r) == dict

    keys = r.keys()

    assert "active_chip" in keys, "Keys have changed"
    assert "automatic_subs" in keys, "Keys have changed"
    assert "entry_history" in keys, "Keys have changed"
    assert "picks" in keys

    assert len(keys) == 4, "Keys have changed"

    entry_history_keys = list(r["entry_history"].keys())

    curr_entry_history_keys = [
        "event",
        "points",
        "total_points",
        "rank",
        "rank_sort",
        "percentile_rank",
        "overall_rank",
        "bank",
        "value",
        "event_transfers",
        "event_transfers_cost",
        "points_on_bench",
    ]

    print(entry_history_keys)
    assert len(set(entry_history_keys).difference(set(curr_entry_history_keys))) == 0, (
        "Keys have changed"
    )
    assert type(r["picks"]) is list

    picks_keys = list(r["picks"][0].keys())
    picks_keys_prev = {
        "element_type",
        "element",
        "position",
        "multiplier",
        "is_captain",
        "is_vice_captain",
    }

    assert len(set(picks_keys).difference(picks_keys_prev)) == 0, "Picks Keys changed"
    assert type(r["automatic_subs"]) is list
    to_json(r, f"{MOCK_DIR}/endpoints/player_endpoint.json")


def test_fpl_url_endpoint():
    r = requests.get(FPL_URL)
    assert r.status_code == 200, "Endpoint unavailable"

    r = r.json()
    assert type(r) is dict

    keys = list(r.keys())
    keys_prev = {
        "events",
        "game_settings",
        "phases",
        "teams",
        "total_players",
        "elements",
        "element_stats",
        "element_types",
    }
    diff = set(keys_prev).difference(set(keys))
    assert len(diff) == 0, f"Keys have changed {diff}"

    assert type(r["events"]) is list
    assert type(r["events"][0]) is dict

    event_keys = list(r["events"][0])
    event_keys_prev = [
        "id",
        "name",
        "deadline_time",
        "average_entry_score",
        "finished",
        "data_checked",
        "highest_scoring_entry",
        "deadline_time_epoch",
        "deadline_time_game_offset",
        "highest_score",
        "is_previous",
        "is_current",
        "is_next",
        "cup_leagues_created",
        "h2h_ko_matches_created",
        "chip_plays",
        "most_selected",
        "most_transferred_in",
        "top_element",
        "top_element_info",
        "transfers_made",
        "most_captained",
        "most_vice_captained",
    ]

    assert len(set(event_keys_prev).difference(set(event_keys))) == 0, (
        f"Keys have changed {set(event_keys_prev).difference(set(event_keys))}"
    )

    assert type(r["game_settings"]) is dict
    game_settings_keys = r["game_settings"].keys()

    game_settings_keys_prev = [
        "element_sell_at_purchase_price",
        "squad_special_max",
        "squad_special_min",
        "underdog_differential",
        "league_join_private_max",
        "league_join_public_max",
        "league_max_size_public_classic",
        "league_max_size_public_h2h",
        "league_max_size_private_h2h",
        "league_max_ko_rounds_private_h2h",
        "league_prefix_public",
        "league_points_h2h_win",
        "league_points_h2h_lose",
        "league_points_h2h_draw",
        "league_ko_first_instead_of_random",
        "cup_start_event_id",
        "cup_stop_event_id",
        "cup_qualifying_method",
        "cup_type",
        "featured_entries",
        "percentile_ranks",
        "squad_squadplay",
        "squad_squadsize",
        "squad_team_limit",
        "squad_total_spend",
        "ui_currency_multiplier",
        "ui_use_special_shirts",
        "ui_special_shirt_exclusions",
        "stats_form_days",
        "sys_vice_captain_enabled",
        "transfers_cap",
        "transfers_sell_on_fee",
        "max_extra_free_transfers",
        "league_h2h_tiebreak_stats",
        "timezone",
    ]
    diff = set(game_settings_keys).difference(game_settings_keys_prev)
    assert len(diff) == 0, f"Game setting keys have changed new {game_settings_keys}"

    assert type(r["phases"]) is list
    assert type(r["phases"][0]) is dict

    phase_keys = list(r["phases"][0])
    phase_keys_prev = {"id", "name", "start_event", "stop_event", "highest_score"}

    diff = set(phase_keys_prev).difference(phase_keys)
    assert len(diff) == 0, f"Game setting keys have changed new {diff}"

    assert type(r["teams"]) is list
    assert type(r["teams"][0]) is dict
    team_keys = list(r["teams"][0])
    team_keys_prev = {
        "code",
        "draw",
        "form",
        "id",
        "loss",
        "name",
        "played",
        "points",
        "position",
        "short_name",
        "strength",
        "team_division",
        "unavailable",
        "win",
        "strength_overall_home",
        "strength_overall_away",
        "strength_attack_home",
        "strength_attack_away",
        "strength_defence_home",
        "strength_defence_away",
        "pulse_id",
    }

    diff = set(team_keys).difference(team_keys_prev)
    assert len(diff) == 0, f"Team keys have changed new {diff}"

    element_stats_keys = r["element_stats"][0].keys()
    assert "label" in element_stats_keys
    assert "name" in element_stats_keys
    assert r["element_stats"][0]["name"] == "minutes", "Measurement metric has changed"
    assert r["element_stats"][0]["label"] == "Minutes played", (
        "Measurement metric has changed"
    )
    assert len(element_stats_keys) == 2

    element_types_keys = r["element_types"][0].keys()
    element_types_keys_prev = [
        "id",
        "plural_name",
        "plural_name_short",
        "singular_name",
        "singular_name_short",
        "squad_select",
        "squad_min_play",
        "squad_min_select",
        "squad_max_select",
        "squad_min_play",
        "squad_max_play",
        "ui_shirt_specific",
        "sub_positions_locked",
        "element_count",
    ]
    diff = set(element_types_keys).difference(element_types_keys_prev)
    assert len(diff) == 0, f"Keys have changed{diff}"

    elements_keys = r["elements"][0].keys()
    elements_keys_prev = [
        "chance_of_playing_next_round",
        "team_join_date",
        "mng_win",
        "mng_underdog_win",
        "can_transact",
        "mng_underdog_draw",
        "mng_clean_sheets",
        "mng_draw",
        "opta_code",
        "removed",
        "has_temporary_code",
        "mng_goals_scored",
        "can_select",
        "mng_loss",
        "team_join_datechance_of_playing_next_round",
        "chance_of_playing_this_round",
        "codecost_change_event",
        "cost_change_event_fall",
        "cost_change_start",
        "cost_change_start_fall",
        "dreamteam_count",
        "element_type",
        "ep_next",
        "ep_this",
        "event_points",
        "first_name",
        "form",
        "id",
        "in_dreamteam",
        "news",
        "news_added",
        "now_cost",
        "photo",
        "points_per_game",
        "second_name",
        "selected_by_percent",
        "special",
        "squad_number",
        "status",
        "team",
        "team_code",
        "total_points",
        "transfers_in",
        "transfers_in_event",
        "transfers_out",
        "transfers_out_event",
        "value_form",
        "value_season",
        "web_name",
        "minutes",
        "goals_scored",
        "assists",
        "clean_sheets",
        "goals_conceded",
        "own_goals",
        "penalties_saved",
        "penalties_missed",
        "yellow_cards",
        "red_cards",
        "saves",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "starts",
        "expected_goals",
        "expected_assists",
        "expected_goal_involvements",
        "expected_goals_conceded",
        "influence_rank",
        "influence_rank_type",
        "creativity_rank",
        "creativity_rank_type",
        "threat_rank",
        "threat_rank_type",
        "ict_index_rank",
        "ict_index_rank_type",
        "corners_and_indirect_freekicks_order",
        "corners_and_indirect_freekicks_text",
        "direct_freekicks_order",
        "direct_freekicks_text",
        "penalties_order",
        "penalties_text",
        "expected_goals_per_90",
        "saves_per_90",
        "expected_assists_per_90",
        "expected_goal_involvements_per_90",
        "expected_goals_conceded_per_90",
        "goals_conceded_per_90",
        "now_cost_rank",
        "now_cost_rank_type",
        "form_rank",
        "form_rank_type",
        "points_per_game_rank",
        "points_per_game_rank_type",
        "selected_rank",
        "selected_rank_type",
        "starts_per_90",
        "clean_sheets_per_90",
        "cost_change_event",
        "code",
        "region",
    ]

    diff = set(elements_keys).difference(set(elements_keys_prev))
    assert len(diff) == 0, f"Keys have changed {diff}"

    to_json(r, f"{MOCK_DIR}/endpoints/fpl_url_endpoint.json")


if __name__ == "__main__":
    pass
