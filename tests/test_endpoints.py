from src.urls import (
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

from src.utils import to_json
from src.paths import MOCK_DIR
from typing import List



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
                "in_dreamteam"
                ]

    assert (
        len(stats_keys.difference(set(stats_keys_prev))) == 0
    ), f"Keys have changed {stats_keys.difference(set(stats_keys_prev))}"

    del stats_keys
    explain_key = r["elements"][0]["explain"][0].keys()
    explain_key_prev = {'fixture', 'stats'}

    assert (
        len(set(explain_key).difference(explain_key_prev)) == 0
    ), "Explain keys have changed"

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
            'code', 'event', 'finished', 'finished_provisional',
            'id', 'kickoff_time', 'minutes', 'provisional_start_time',
            'started', 'team_a', 'team_a_score', 'team_h', 'team_h_score',
            'stats', 'team_h_difficulty', 'team_a_difficulty',
            'pulse_id'
            ]
    assert len(set(fixture_key_prev).difference(fixture_keys)) == 0, 'Fixture keys have changed'
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
                "time"
                ]
        
        assert set(transfer_keys_prev).difference(transfer_keys), "Transfer keys have changed"

    out_dict = {"transfer": r}
    to_json(out_dict, f"{MOCK_DIR}/endpoints/transfer_endpoint.json")


def test_history_endpoint(participant):
    """Extracts a players history for prior seasons given an id"""

    r = requests.get(HISTORY_URL.format(participant))
    assert r.status_code == 200, "Endpoint unavailable"
    r = r.json()

    assert type(r) is dict, "Endpoint structure has changed"
    history_keys = list(r.keys())
    history_keys_prev = [
        "current",
        "past",
        "chips"
    ]

    assert len(set(history_keys_prev).difference(set(history_keys))) == 0, 'History keys have changed'
    
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

    assert len(set(current_keys).difference(set(current_keys_prev))) == 0, "Current keys has changed"

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
    h2h_keys_prev = [
        "has_next",
        "page",
        "results"
    ]

    assert len(set(h2h_keys_prev).difference(set(h2h_keys))) == 0, "H2h keys have changed"

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
        "knockout_name"
    ]

    assert len(set(results_keys_prev).difference(results_keys)) == 0, "Results keys has changed"
    to_json(r, f"{MOCK_DIR}/endpoints/h2h_league_endpoint.json")


def test_league_endpoint(classic_league):
    page = 1
    r = requests.get(LEAGUE_URL.format(classic_league, page))

    assert r.status_code == 200
    r = dict(r.json())

    assert type(r) is dict
    keys = list(r.keys())

    keys_prev = [
        "new_entries",
        "last_updated_data",
        "league",
        "standings"
    ]

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
    assert len(set(league_keys).difference(league_keys_prev)) == 0, "League keys have changed"

    new_entries_keys = r["new_entries"]  # type: ignore
    new_entries_keys_prev = [
      "has_next",
      "page",
      "results"
    ]
    assert len(set(new_entries_keys).difference(new_entries_keys_prev)) == 0, "New Entries keys have changed"

    standings_keys = r["standings"]  # type: ignore
    standings_keys_prev = [
        "has_next",
        "page",
        "results"
    ]

    assert len(set(standings_keys).difference(standings_keys_prev)) == 0, " Standings have changed"

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
        "entry_name"
    ]
    assert len(set(participant_info_keys).difference(participant_info)) == 0, "Participant info keys have changed"

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
    assert len(set(entry_history_keys).difference(set(curr_entry_history_keys))) == 0, "Keys have changed"
    assert type(r["picks"]) is list

    picks_keys = list(r["picks"][0].keys())
    picks_keys_prev = {
        "element",
        "position",
        "multiplier",
        "is_captain",
        "is_vice_captain"
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
        "element_types"
    }

    assert (
        len(set(keys_prev).difference(set(keys))) == 0
    ), f"Keys have changed {set(keys_prev).difference(set(keys))}"

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

    assert (
        len(set(event_keys_prev).difference(set(event_keys))) == 0
    ), f"Keys have changed {set(event_keys_prev).difference(set(event_keys))}"

    assert type(r["game_settings"]) is dict
    game_settings_keys = r["game_settings"].keys()

    game_settings_keys_prev = [
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
    assert (
        len(set(game_settings_keys).difference(game_settings_keys_prev)) == 0
    ), f"Game setting keys have changed new {game_settings_keys}"

    assert type(r["phases"]) is list
    assert type(r["phases"][0]) is dict

    phase_keys = list(r["phases"][0])
    phase_keys_prev = {
        "id",
        "name",
        "start_event",
        "stop_event",
        "highest_score"
        }
    
    assert (
        len(set(phase_keys_prev).difference(phase_keys)) == 0
    ), f"Game setting keys have changed new {game_settings_keys}"

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
    
    assert (
        len(set(team_keys).difference(team_keys_prev)) == 0
    ), f"Team keys have changed new"

    element_stats_keys = r["element_stats"][0].keys()
    assert "label" in element_stats_keys
    assert "name" in element_stats_keys
    assert r["element_stats"][0]["name"] == "minutes", "Measurement metric has changed"
    assert r["element_stats"][0]["label"] == "Minutes played", "Measurement metric has changed"
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
    assert len(set(element_types_keys).difference(element_types_keys_prev)) == 0, "Keys have changed"

    elements_keys = r["elements"][0].keys()
    assert "chance_of_playing_next_round" in elements_keys
    assert "chance_of_playing_this_round" in elements_keys
    assert "code" in elements_keys
    assert "cost_change_event" in elements_keys
    assert "cost_change_event_fall" in elements_keys
    assert "cost_change_start" in elements_keys
    assert "cost_change_start_fall" in elements_keys
    assert "dreamteam_count" in elements_keys
    assert "element_type" in elements_keys
    assert "ep_next" in elements_keys
    assert "ep_this" in elements_keys
    assert "event_points" in elements_keys
    assert "first_name" in elements_keys
    assert "form" in elements_keys
    assert "id" in elements_keys
    assert "in_dreamteam" in elements_keys
    assert "news" in elements_keys
    assert "news_added" in elements_keys

    assert "now_cost" in elements_keys
    assert "photo" in elements_keys
    assert "points_per_game" in elements_keys
    assert "second_name" in elements_keys
    assert "selected_by_percent" in elements_keys
    assert "special" in elements_keys
    assert "squad_number" in elements_keys
    assert "status" in elements_keys
    assert "team" in elements_keys
    assert "team_code" in elements_keys
    assert "total_points" in elements_keys
    assert "transfers_in" in elements_keys
    assert "transfers_in_event" in elements_keys

    assert "transfers_out" in elements_keys
    assert "transfers_out_event" in elements_keys
    assert "value_form" in elements_keys
    assert "value_season" in elements_keys
    assert "web_name" in elements_keys
    assert "minutes" in elements_keys
    assert "goals_scored" in elements_keys
    assert "assists" in elements_keys

    assert "clean_sheets" in elements_keys
    assert "goals_conceded" in elements_keys
    assert "own_goals" in elements_keys
    assert "penalties_saved" in elements_keys
    assert "penalties_missed" in elements_keys
    assert "yellow_cards" in elements_keys
    assert "red_cards" in elements_keys

    assert "saves" in elements_keys
    assert "bonus" in elements_keys
    assert "bps" in elements_keys
    assert "influence" in elements_keys
    assert "creativity" in elements_keys

    assert "threat" in elements_keys
    assert "ict_index" in elements_keys
    assert "starts" in elements_keys
    assert "expected_goals" in elements_keys
    assert "expected_assists" in elements_keys
    assert "expected_goal_involvements" in elements_keys
    assert "expected_goals_conceded" in elements_keys

    assert "influence_rank" in elements_keys
    assert "influence_rank_type" in elements_keys
    assert "creativity_rank" in elements_keys
    assert "creativity_rank_type" in elements_keys
    assert "threat_rank" in elements_keys
    assert "threat_rank_type" in elements_keys
    assert "ict_index_rank" in elements_keys
    assert "ict_index_rank_type" in elements_keys

    assert "corners_and_indirect_freekicks_order" in elements_keys
    assert "corners_and_indirect_freekicks_text" in elements_keys
    assert "direct_freekicks_order" in elements_keys
    assert "direct_freekicks_text" in elements_keys
    assert "penalties_order" in elements_keys
    assert "penalties_text" in elements_keys
    assert "expected_goals_per_90" in elements_keys

    assert "saves_per_90" in elements_keys
    assert "expected_assists_per_90" in elements_keys
    assert "expected_goal_involvements_per_90" in elements_keys
    assert "expected_goals_conceded_per_90" in elements_keys
    assert "goals_conceded_per_90" in elements_keys

    assert "now_cost_rank" in elements_keys
    assert "now_cost_rank_type" in elements_keys
    assert "form_rank" in elements_keys
    assert "form_rank_type" in elements_keys

    assert "points_per_game_rank" in elements_keys
    assert "points_per_game_rank_type" in elements_keys
    assert "selected_rank" in elements_keys
    assert "selected_rank_type" in elements_keys
    assert "starts_per_90" in elements_keys
    assert "clean_sheets_per_90" in elements_keys

    assert len(elements_keys) == 88, "Keys have changed"

    to_json(r, f"{MOCK_DIR}/endpoints/fpl_url_endpoint.json")


if __name__ == "__main__":
    pass
