from src.urls import GW_URL, FIXTURE_URL, TRANSFER_URL, HISTORY_URL, H2H_LEAGUE,LEAGUE_URL, FPL_PLAYER, FPL_URL

import pytest
import requests

#from typing import Any, List, Dict

def test_gameweek_endpoint(gw_fixture):

    #digit greater than 1 less than 38
    gameweek_url = GW_URL.format(gw_fixture)
    assert gameweek_url == "https://fantasy.premierleague.com/api/event/8/live/"
    
    r = requests.get(gameweek_url)
    assert r.status_code == 200, f'{r.status_code} - Url invalid, or unavailable'
    
    r = r.json()
    assert 'elements' in r.keys()
    
    assert type(r['elements']) == list
    assert type(r['elements'][0]) == dict

    element_keys = list(r['elements'][0].keys())
    assert 'id' in element_keys
    assert 'stats' in element_keys
    assert 'explain' in element_keys 
    del element_keys

    stats_keys = r['elements'][0]['stats'].keys()
    assert 'minutes' in stats_keys
    assert 'goals_scored' in stats_keys
    assert 'assists' in stats_keys
    assert 'clean_sheets' in stats_keys
    assert 'goals_conceded' in stats_keys
    assert 'own_goals' in stats_keys
    assert 'penalties_saved' in stats_keys
    assert 'penalties_missed' in stats_keys
    assert 'yellow_cards' in stats_keys
    assert  'red_cards' in stats_keys
    assert 'saves' in stats_keys
    assert 'bonus' in stats_keys
    assert 'bps' in stats_keys
    assert 'influence' in stats_keys
    assert 'creativity' in stats_keys
    assert 'threat' in stats_keys
    assert 'ict_index' in stats_keys
    assert 'starts' in stats_keys
    assert 'expected_goals' in stats_keys
    assert 'expected_assists' in stats_keys
    assert 'expected_goal_involvements' in stats_keys
    assert 'expected_goals_conceded' in stats_keys
    assert 'total_points' in stats_keys
    assert 'in_dreamteam' in stats_keys

    del stats_keys
    explain_key = r['elements'][0]['explain'][0].keys()

    assert 'fixture' in explain_key
    assert 'stats' in explain_key

    assert  r['elements'][0]['explain'][0]['stats'][0]['identifier'] == 'minutes'
    assert 'points' in r['elements'][0]['explain'][0]['stats'][0]
    assert 'value' in r['elements'][0]['explain'][0]['stats'][0]

def test_fixture_endpoint():
    
    r = requests.get(FIXTURE_URL)
    assert r.status_code == 200, 'endpoint unavailable'
    r = r.json()

    assert type(r) == list
    assert type(r[0]) == dict

    fixture_keys = list(r[0].keys())
    
    assert 'code' in fixture_keys
    assert 'event' in fixture_keys
    assert 'finished' in fixture_keys
    assert 'finished_provisional' in fixture_keys
    assert 'id' in fixture_keys
    assert 'kickoff_time' in fixture_keys
    assert 'minutes' in fixture_keys
    assert 'provisional_start_time' in fixture_keys
    assert 'started' in fixture_keys
    assert 'team_a' in fixture_keys
    assert 'team_a_score' in fixture_keys
    assert 'team_h' in fixture_keys
    assert 'team_h_score' in fixture_keys
    assert 'stats' in fixture_keys
    assert 'team_h_difficulty' in fixture_keys
    assert 'team_a_difficulty' in fixture_keys
    assert 'pulse_id' in fixture_keys

    assert len(fixture_keys) == 17

    assert type(r[0]['stats']) == list
    del fixture_keys

def test_transfer_endpoint(player):
    """Tests transfer endpoint given a valid entry_id. 
    Response is a list of transfers for previous gameweeks"""
    r = requests.get(TRANSFER_URL.format(player))
    print(r.status_code)
    
    assert r.status_code == 200, 'Endpoint unavailable'
    r = r.json()
    
    assert type(r) == list, 'Endpoint structure has changed'
    assert type(r[0]) == dict

    transfer_keys = r[0].keys()
    
    assert 'element_in' in transfer_keys
    assert 'element_in_cost' in transfer_keys
    assert 'element_out' in transfer_keys
    assert 'element_out_cost' in transfer_keys
    assert 'entry' in transfer_keys
    assert 'event' in transfer_keys
    assert 'time' in transfer_keys

    assert len(transfer_keys) == 7


def test_history_endpoint(player):

    """Extracts a players history for prior seasons given an id"""

    r = requests.get(HISTORY_URL.format(player))
    assert r.status_code == 200, 'Endpoint unavailable'
    r = r.json()

    assert type(r) == dict, "Endpoint structure has changed"
    history_keys = list(r.keys())

    assert 'current' in history_keys
    assert 'past' in history_keys
    assert 'chips' in history_keys
    assert len(history_keys) == 3 

    assert type(r['current']) == list, "Endpoint structure has changed"
    assert type(r['current'][0]) == dict, "Endpoint structure has changed"

    assert type(r['past']) == list, "Endpoint structure has changed"
    assert type(r['past'][0]) == dict, "Endpoint structure has changed"

    assert type(r['chips']) == list, "Endpoint structure has changed"
    assert type(r['chips'][0]) == dict, "Endpoint structure has changed"

    current_keys = r['current'][0].keys()

    assert 'event' in current_keys
    assert 'points' in current_keys
    assert 'total_points' in current_keys
    assert 'rank' in current_keys
    assert 'rank_sort' in current_keys

    assert 'overall_rank' in current_keys
    assert 'bank' in current_keys
    assert 'value' in current_keys
    assert 'event_transfers' in current_keys
    assert 'event_transfers_cost' in current_keys
    assert 'points_on_bench' in current_keys

    assert len(current_keys) == 11, "Number of keys has changed"

    past_keys = r['past'][0].keys()

    assert 'season_name' in past_keys
    assert 'total_points' in past_keys
    assert 'rank' in past_keys

    assert len(past_keys) == 3, "Number of keys has changed"

    chips_keys = r['chips'][0].keys()

    assert 'name' in chips_keys
    assert 'time' in chips_keys
    assert 'event' in chips_keys

    assert len(chips_keys) == 3, "Number of keys has changed"
    

def test_h2h_league_endpoint(h2h_league):
    """"""

    r = requests.get(H2H_LEAGUE.format(h2h_league))
    assert r.status_code == 200
    
    r = r.json()
    assert(type(r)) == dict, "Endpoint Structure has changed"

    h2h_keys = list(r.keys())

    assert 'has_next' in h2h_keys
    assert 'page' in h2h_keys
    assert 'results' in h2h_keys

    assert type(r['results']) == list
    assert type(r['results'][0]) == dict

    results_keys = list(r['results'][0].keys())
    
    assert 'id' in results_keys
    assert 'entry_1_entry' in results_keys
    assert 'entry_1_name' in results_keys
    assert 'entry_1_player_name' in results_keys
    assert 'entry_1_points' in results_keys
    assert 'entry_1_win' in results_keys
    assert 'entry_1_draw' in results_keys
    assert 'entry_1_loss' in results_keys
    assert 'entry_1_total' in results_keys
    
    assert 'entry_2_entry' in results_keys
    assert 'entry_2_name' in results_keys
    assert 'entry_2_player_name' in results_keys
    assert 'entry_2_points' in results_keys
    assert 'entry_2_win' in results_keys
    assert 'entry_2_draw' in results_keys
    assert 'entry_2_loss' in results_keys
    assert 'entry_2_total' in results_keys

    assert 'is_knockout' in results_keys
    assert 'league' in results_keys
    assert 'winner' in results_keys
    assert 'seed_value' in results_keys
    assert 'event' in results_keys
    assert 'tiebreak' in results_keys
    assert 'is_bye' in results_keys
    assert 'knockout_name' in results_keys

    assert len(results_keys) == 25, "Number of keys has changed"

def test_league_endpoint(classic_league):

    page = 1
    r = requests.get(LEAGUE_URL.format(classic_league, page))
    
    assert r.status_code == 200
    r = r.json()

    assert type(r) == dict 
    keys = list(r.keys())

    assert 'new_entries' in keys
    assert 'last_updated_data' in keys
    assert 'league' in keys
    assert 'standings' in keys

    assert len(keys) == 4
    assert type(r['league']) == dict 
    assert type(r['new_entries']) == dict 
    assert type(r['standings']) == dict 
   
   
    league_keys = r['league']

    assert 'id' in league_keys  
    assert 'name' in league_keys    
    assert 'created' in league_keys 
    assert 'closed' in league_keys  
    assert 'max_entries' in league_keys  
    assert 'league_type' in league_keys  
    assert 'scoring' in league_keys  
    assert 'admin_entry' in league_keys
    assert 'start_event' in league_keys
    assert 'code_privacy' in league_keys
    assert 'has_cup' in league_keys
    assert 'cup_league' in league_keys
    assert 'rank' in league_keys

    assert len(league_keys) == 13, "Keys have changed"
    
    new_entries_keys = r['new_entries']
    assert 'has_next' in new_entries_keys
    assert 'page' in new_entries_keys
    assert 'results' in new_entries_keys

    assert(len(new_entries_keys)) == 3, "Keys have changed"
    
    standings_keys = r['standings']
    assert 'has_next' in standings_keys
    assert 'page' in standings_keys
    assert 'results' in standings_keys

    assert(len(standings_keys)) == 3, "Keys have changed"

    assert type(r['standings']['results']) == list
    assert type(r['new_entries']['results']) == list 

    participant_info = r['standings']['results'][0]

    assert 'id' in participant_info
    assert 'event_total' in participant_info
    assert 'player_name' in participant_info
    assert 'rank' in participant_info
    assert 'last_rank' in participant_info
    assert 'rank_sort' in participant_info
    assert 'total' in participant_info
    assert 'entry' in participant_info
    assert 'entry_name' in participant_info


def test_fpl_player_endpoint(player,gw_fixture):

    r = requests.get(FPL_PLAYER.format(player, gw_fixture))
    assert r.status_code == 200, 'Endpoint unavailable, check player_id and gameweek'

    r = r.json()    
    assert type(r) == dict

    keys = r.keys()

    assert 'active_chip' in keys, "Keys have changed"
    assert 'automatic_subs' in keys, "Keys have changed"
    assert 'entry_history' in keys, "Keys have changed"
    assert 'picks' in keys

    assert len(keys) == 4, "Keys have changed"

    entry_history_keys = list(r['entry_history'].keys())
    
    assert 'event' in entry_history_keys
    assert 'points' in entry_history_keys
    assert 'total_points' in entry_history_keys
    assert 'rank' in entry_history_keys
    assert 'rank_sort' in entry_history_keys
    assert 'overall_rank' in entry_history_keys
    assert 'bank' in entry_history_keys
    assert 'value' in entry_history_keys
    assert 'event_transfers' in entry_history_keys
    assert 'event_transfers_cost' in entry_history_keys
    assert 'points_on_bench' in entry_history_keys

    assert len(entry_history_keys) == 11, 'Keys have changed'
    assert type(r['picks']) == list
    
    picks_keys = list(r['picks'][0].keys())

    assert 'element' in picks_keys
    assert 'position' in picks_keys
    assert 'multiplier' in picks_keys
    assert 'is_captain' in picks_keys
    assert 'is_vice_captain' in picks_keys

    assert len(picks_keys) == 5, 'Keys have changed'
    assert type(r['automatic_subs']) == list

def test_fpl_url_endpoint():
    r = requests.get(FPL_URL)
    assert r.status_code == 200, "Endpoint unavailable"

    r = r.json()
    keys = list(r.keys())

    assert 'events' in keys
    assert 'game_settings' in keys
    assert 'phases' in keys
    assert 'teams' in keys
    assert 'total_players' in keys
    assert 'elements' in keys
    assert 'element_stats' in keys
    assert 'element_types' in keys

    assert type(r['events']) == list
    assert type(r['events'][0]) == dict
    event_keys = list(r['events'][0])
    print(r['events'][15])

 

    assert 'id' in event_keys
    assert 'name' in event_keys
    assert 'deadline_time' in event_keys
    assert 'average_entry_score' in event_keys
    assert 'finished' in event_keys
    assert 'data_checked' in event_keys
    assert 'highest_scoring_entry' in event_keys
    assert 'deadline_time_epoch' in event_keys
    assert 'deadline_time_game_offset' in event_keys
    assert 'highest_score' in event_keys
    assert 'is_previous' in event_keys
    assert 'is_current' in event_keys
    assert 'is_next' in event_keys
    assert 'cup_leagues_created' in event_keys
    assert 'h2h_ko_matches_created' in event_keys
    assert 'chip_plays' in event_keys
    assert 'most_selected' in event_keys
    assert 'most_transferred_in' in event_keys
    assert 'top_element' in event_keys
    assert 'top_element_info' in event_keys
    assert 'transfers_made' in event_keys
    assert 'most_captained' in event_keys
    assert 'most_vice_captained' in event_keys
    assert len(event_keys) == 23, 'Keys have changed'


    assert type(r['game_settings']) == dict
    game_settings_keys = r['game_settings'].keys()
    
    assert 'league_join_private_max'  in game_settings_keys
    assert 'league_join_public_max'  in game_settings_keys
    assert 'league_max_size_public_classic'  in game_settings_keys

    assert 'league_max_size_public_h2h'  in game_settings_keys
    assert 'league_max_size_private_h2h'  in game_settings_keys
    assert 'league_max_ko_rounds_private_h2h'  in game_settings_keys
    assert 'league_prefix_public'  in game_settings_keys

    assert 'league_points_h2h_win'  in game_settings_keys
    assert 'league_points_h2h_lose'  in game_settings_keys
    assert 'league_points_h2h_draw'  in game_settings_keys
    assert 'league_ko_first_instead_of_random'  in game_settings_keys

    assert 'cup_start_event_id'  in game_settings_keys
    assert 'cup_stop_event_id'  in game_settings_keys
    assert 'cup_qualifying_method'  in game_settings_keys
    assert 'sys_vice_captain_enabled'  in game_settings_keys

    assert 'squad_total_spend'  in game_settings_keys
    assert 'squad_team_limit'  in game_settings_keys
    assert 'squad_squadsize'  in game_settings_keys
    assert 'squad_squadplay'  in game_settings_keys

    assert 'cup_type'  in game_settings_keys
    assert 'featured_entries'  in game_settings_keys 

    assert 'stats_form_days'  in game_settings_keys
    assert 'ui_special_shirt_exclusions'  in game_settings_keys
    assert 'ui_use_special_shirts'  in game_settings_keys
    assert 'ui_currency_multiplier'  in game_settings_keys

    assert 'transfers_cap'  in game_settings_keys
    assert 'transfers_sell_on_fee'  in game_settings_keys
    assert 'league_h2h_tiebreak_stats'  in game_settings_keys
    assert 'timezone'  in game_settings_keys
    

    assert len(r['game_settings']) == 29, 'Keys have changed'
    

    assert type(r['phases']) == list
    assert type(r['phases'][0]) == dict
    phase_keys = list(r['phases'][0])
    assert 'id' in phase_keys
    assert 'name' in phase_keys
    assert 'start_event' in phase_keys
    assert 'stop_event' in phase_keys
    assert len(phase_keys) == 4

    assert type(r['teams']) == list
    assert type(r['teams'][0]) == dict
    team_keys = list(r['teams'][0])
    assert 'code' in team_keys
    assert 'draw' in team_keys
    assert 'form' in team_keys
    assert 'id' in team_keys
    assert 'loss' in team_keys
    assert 'name' in team_keys
    assert 'played' in team_keys
    assert 'points' in team_keys
    assert 'position' in team_keys
    assert 'short_name' in team_keys
    assert 'strength' in team_keys
    assert 'team_division' in team_keys
    assert 'unavailable' in team_keys
    assert 'win' in team_keys
    assert 'strength_overall_home' in team_keys
    assert 'strength_overall_away' in team_keys
    assert 'strength_attack_home' in team_keys
    assert 'strength_attack_away' in team_keys
    assert 'strength_defence_home' in team_keys
    assert 'strength_defence_away' in team_keys
    assert 'pulse_id' in team_keys
    assert len(team_keys) == 21, 'Keys have changed '

    element_stats_keys = r['element_stats'][0].keys()
    assert 'label' in element_stats_keys
    assert 'name'  in element_stats_keys
    assert r['element_stats'][0]['name'] == 'minutes', "Measurement metric has changed" 
    assert r['element_stats'][0]['label'] == 'Minutes played', "Measurement metric has changed"
    assert len(element_stats_keys) == 2

    element_types_keys = r['element_types'][0].keys()
    assert 'id' in element_types_keys
    assert 'plural_name' in element_types_keys
    assert 'plural_name_short' in element_types_keys
    assert 'singular_name' in element_types_keys
    assert 'singular_name_short' in element_types_keys
    assert 'squad_select' in element_types_keys
    assert 'squad_min_play' in element_types_keys
    assert 'squad_max_play' in element_types_keys
    assert 'ui_shirt_specific' in element_types_keys
    assert 'sub_positions_locked' in element_types_keys
    assert 'element_count' in element_types_keys
    assert len(element_types_keys) == 11, "Keys have changed"

    elements_keys = r['elements'][0].keys()
    assert 'chance_of_playing_next_round' in elements_keys
    assert 'chance_of_playing_this_round' in elements_keys
    assert 'code' in elements_keys    
    assert 'cost_change_event' in  elements_keys
    assert 'cost_change_event_fall' in elements_keys
    assert 'cost_change_start' in elements_keys
    assert 'cost_change_start_fall' in elements_keys
    assert 'dreamteam_count' in elements_keys
    assert 'element_type' in elements_keys
    assert 'ep_next' in elements_keys
    assert 'ep_this' in elements_keys
    assert 'event_points' in elements_keys
    assert 'first_name' in elements_keys
    assert 'form' in elements_keys
    assert 'id' in elements_keys
    assert 'in_dreamteam' in elements_keys
    assert 'news' in elements_keys
    assert 'news_added' in elements_keys

    assert 'now_cost' in elements_keys
    assert 'photo' in elements_keys
    assert 'points_per_game' in elements_keys
    assert 'second_name' in elements_keys
    assert 'selected_by_percent' in elements_keys
    assert 'special' in elements_keys
    assert 'squad_number' in elements_keys
    assert 'status' in elements_keys
    assert 'team' in elements_keys
    assert 'team_code' in elements_keys
    assert 'total_points' in elements_keys
    assert 'transfers_in' in elements_keys
    assert 'transfers_in_event' in elements_keys

    assert 'transfers_out' in elements_keys
    assert 'transfers_out_event' in elements_keys
    assert 'value_form' in elements_keys
    assert 'value_season' in elements_keys
    assert 'web_name' in elements_keys
    assert 'minutes' in elements_keys
    assert 'goals_scored' in elements_keys
    assert 'assists' in elements_keys

    assert 'clean_sheets' in elements_keys
    assert 'goals_conceded' in elements_keys
    assert 'own_goals' in elements_keys
    assert 'penalties_saved' in elements_keys
    assert 'penalties_missed' in elements_keys
    assert 'yellow_cards' in elements_keys
    assert 'red_cards' in elements_keys

    assert 'saves' in elements_keys
    assert 'bonus' in elements_keys
    assert 'bps' in elements_keys
    assert 'influence' in elements_keys
    assert 'creativity' in elements_keys

    assert 'threat' in elements_keys
    assert 'ict_index' in elements_keys
    assert 'starts' in elements_keys
    assert 'expected_goals' in elements_keys
    assert 'expected_assists' in elements_keys
    assert 'expected_goal_involvements' in elements_keys
    assert 'expected_goals_conceded' in elements_keys

    assert 'influence_rank' in elements_keys
    assert 'influence_rank_type' in elements_keys
    assert 'creativity_rank' in elements_keys
    assert 'creativity_rank_type' in elements_keys
    assert 'threat_rank' in elements_keys
    assert 'threat_rank_type' in elements_keys
    assert 'ict_index_rank' in elements_keys
    assert 'ict_index_rank_type' in elements_keys

    assert 'corners_and_indirect_freekicks_order' in elements_keys
    assert 'corners_and_indirect_freekicks_text' in elements_keys
    assert 'direct_freekicks_order' in elements_keys
    assert 'direct_freekicks_text' in elements_keys
    assert 'penalties_order' in elements_keys
    assert 'penalties_text' in elements_keys
    assert 'expected_goals_per_90' in elements_keys

    assert 'saves_per_90' in elements_keys
    assert 'expected_assists_per_90' in elements_keys
    assert 'expected_goal_involvements_per_90' in elements_keys
    assert 'expected_goals_conceded_per_90' in elements_keys
    assert 'goals_conceded_per_90' in elements_keys

    assert 'now_cost_rank' in elements_keys
    assert 'now_cost_rank_type' in elements_keys
    assert 'form_rank' in elements_keys
    assert 'form_rank_type' in elements_keys
    
    assert 'points_per_game_rank' in elements_keys
    assert 'points_per_game_rank_type' in elements_keys
    assert 'selected_rank' in elements_keys
    assert 'selected_rank_type' in elements_keys
    assert 'starts_per_90' in elements_keys
    assert 'clean_sheets_per_90' in elements_keys

    assert len(elements_keys) == 88, "Keys have changed"

    def a_b(key = 'total_players'):
        if type(r[key]) == dict:
            print(r[key].keys())
            print(len(r[key].keys()))
        elif type(r[key]) == list:
            print('-')
            print(r[key][0].keys())
            print(len(r[key][0].keys()))
        else: 
            print (type(r[key]))

    a_b(key = 'elements')


if __name__ == "__main__":
    test_fpl_url_endpoint()