from app.urls import GW_URL, FIXTURE_URL, TRANSFER_URL, HISTORY_URL, H2H_LEAGUE,LEAGUE_URL, FPL_PLAYER, FPL_URL

import pytest
import requests

#from typing import Any, List, Dict

def test_gameweek_endpoint(GW_URL):

    #digit greater than 1 less than 38
    gameweek_url = GW_URL.format(4)
    
    print(gameweek_url)
    #assert url == "https://fantasy.premierleague.com/api/event/{4}/live/"
    
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
    
    explain_key = r['elements'][0]['explain'][0].keys()

    assert 'fixture' in explain_key
    assert 'stats' in explain_key

    assert  r['elements'][0]['explain'][0]['stats'][0]['identifier'] == 'minutes'
    assert 'points' in r['elements'][0]['explain'][0]['stats'][0]
    assert 'value' in r['elements'][0]['explain'][0]['stats'][0]

if __name__ == "__main__":
    test_gameweek_endpoint(GW_URL)