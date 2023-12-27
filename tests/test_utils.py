from src.utils import get_basic_stats,get_gw_transfers, parse_transfers, get_participant_entry, to_json
import pytest

from os.path import join, realpath
import os
import json

from tests.test_endpoints import test_fpl_url_endpoint
from src.utils import check_gw, Participant, get_curr_event,League

from src.urls import FPL_URL,TRANSFER_URL
import requests

def test_to_json(transfer_obj, filepath):
    output_name = 'test.json'
    to_json(transfer_obj, join(filepath, output_name))
    assert output_name in os.listdir(filepath)

def test_from_json(filepath):
    output_name = 'test.json'
    with open(join(filepath, output_name), 'r') as ins:
        obj = json.load(ins)
    assert type(obj) == dict

def test_get_basic_stats(values):
    Q1, average, Q3 = get_basic_stats(values)
    assert Q1 == 1.75
    assert round(average, 2) == 7.75 
    assert Q3  == 11.75

def test_parse_transfers(transfer_obj):
    
    row = parse_transfers(transfer_obj)
    row_keys = list(row.keys())

    assert type(row) == dict
    assert row_keys[0] == transfer_obj['entry'] 
    assert row[98120]['element_in'] == [transfer_obj['element_in']]
    assert row[98120]['element_out'] == [transfer_obj['element_out']]


def test_check_gw_int_is_true(gw_fixture):
    assert check_gw(gw_fixture)[0] == True , 'Only 38 games in a season'
    assert check_gw(gw_fixture)[1] == 8

def test_check_gw_span_is_true(span_fixture):
    assert check_gw(span_fixture)[0] == True
    assert check_gw(span_fixture)[1] == [8, 10, 3]

@pytest.mark.parametrize("diff_fixture", [40] )
def test_check_gw_is_false(diff_fixture):
    assert check_gw(diff_fixture) == None , 'Only 38 games in a season'

def test_get_curr_event():
    r = requests.get(FPL_URL)
    assert r.status_code == 200, 'Endpoint unavailable, check participant_id and gameweek'

    r = r.json()    
    assert type(r) == dict
    assert 'events' in r.keys()

    check_set = r['events'][0]
    inter_ = set(['finished', 'data_checked', 'id', 'is_current'])

    assert inter_.intersection(check_set) == inter_

def test_get_diff_gw_transfers(participant, span_fixture):
    row = get_gw_transfers([participant], span_fixture)
    assert list(row[span_fixture[0]].keys())[0] == participant
    assert set(row.keys()).union(set(span_fixture)) == set(span_fixture)

def test_get_all_gw_transfers(participant,diff_gw_fixture):
    row = get_gw_transfers([participant], diff_gw_fixture, all = True)
    keys = list(row.keys())

    start = keys[-1]
    end = keys[0]
    rang = [i for i in range(start, end+1)]

    assert set(row.keys()).union(rang) == set(rang) 

def test_get_participant_entry(participant, gw_fixture):

    team_list = get_participant_entry(participant, gw_fixture)
    team_list_keys = list(team_list.keys())

    assert "gw" in team_list_keys
    assert "entry" in team_list_keys
    assert "active_chip" in team_list_keys
    assert "points_on_bench" in team_list_keys
    assert "event_transfers_cost" in team_list_keys
    assert "captain" in team_list_keys
    assert "participants" in team_list_keys
    assert "bench" in team_list_keys
    assert "auto_subs" in team_list_keys

    assert len(team_list['players']) == 11 , 'Onfield players must be 11'
    assert len(team_list['bench']) == 5, "Bench players must be 4"
    assert len(team_list['captain']) == 1, "One captain"
    assert len(team_list['vice_captain']) == 1, "One vice captain"

class TestParticipant():

    def test_init(self,participant):
        test = Participant(participant)
        assert test.participant == 98120

    def test_get_gw_transfers(self,participant, gw_fixture):
        test = Participant(participant)
        output = test.get_gw_transfers(gw_fixture)
        
        assert type(output) == dict
        assert gw_fixture in list(output.keys())

        elems_keys = output[gw_fixture].keys()
        elems = set(['element_in', 'element_out'])
        
        assert elems.union(elems_keys) == elems
        output_not_all_not_check_gw = test.get_gw_transfers(39,all = False)
        
        assert type(output_not_all_not_check_gw) == dict
        assert len(output_not_all_not_check_gw.keys()) == 0
    
    def test_get_span_week_transfers(self,participant, span_fixture):
        test = Participant(participant)
        output = test.get_span_week_transfers(span_fixture)

        assert type(output) == dict
        event_keys = list(output.keys())
        span_set = set(span_fixture)

        assert span_set.union(event_keys) == span_set

    def test_get_all_week_transfers(self,participant):
        test = Participant(participant)
        curr_gw = get_curr_event()
        curr_gw = curr_gw[0]

        output = test.get_all_week_transfers()

        assert type(output) == dict
        #some weeks transfers are saved, so assertions cannot work 
        #event_keys = set(list(output.keys()))
        #all_keys = [i for i in range(1, curr_gw+1)]
        #assert event_keys.union(all_keys) == event_keys

    def test_get_all_week_entries():
        pass

    def test_participant_get_all_week_entries():
        pass

    def test_participant_get_span_week_transfers():
        pass

    def test_participant_get_all_week_transfers():
        pass

class TestLeague():
    
    def test_init(self, league_fixture):
        test = League(league_fixture)
        assert test.league_id == 1088941
        assert test.participants == [] 
        pass

    def test_league_obtain_league_participants_empty(self):
        #Endpoint tests validates this
        pass

    def test_league_obtain_league_participants_fill(self,league_fixture,league_fill_fixture):
        test = League(league_fixture)
        test.participants = league_fill_fixture

        obj = test.obtain_league_participants()
        keys = set(['entry', 'entry_name', 'id', 'event_total', 'player_name', 'rank', 'last_rank', 'rank_sort', 'total'])

        diff = keys.difference(test.participants[0].keys())
        assert keys.intersection(test.participants[0].keys()) == keys, f"Vital keys missing, Add keys -  {diff}"

        assert len(test.participants) == len(obj)
        assert type(test.participants) == list
        
        assert test.entry_ids != None
        assert type(test.entry_ids) == list

    
    def test_league_get_participant_name(self,league_fixture,league_fill_fixture):
        test = League(league_fixture)
        test.participants = league_fill_fixture
        names = test.get_participant_name()

        assert 'entry' in test.participants[0].keys()
        assert 'entry_name' in test.participants[0].keys()
    
        assert type(names) == dict

    def test_league_get_all_participant_entries():
        pass

    def test_league_get_gw_transfers():
        pass

if __name__ == "__main__":
   print("use pytest to run tests")