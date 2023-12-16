from src.utils import get_basic_stats,get_gw_transfers, parse_transfers, get_participant_entry, to_json
import pytest
from os.path import join, realpath
import os
import json

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

def test_parse_transfers(player, transfer_obj):
    
    #test_transfer_endpoint(player)
    row = parse_transfers(transfer_obj)
    row_keys = list(row.keys())

    assert type(row) == dict
    assert row_keys[0] == transfer_obj['entry'] 
    assert row[98120]['element_in'] == [transfer_obj['element_in']]
    assert row[98120]['element_out'] == [transfer_obj['element_out']]

def test_get_diff_gw_transfers(player, diff_gw_fixture):
    row = get_gw_transfers([player], diff_gw_fixture)
    assert list(row[diff_gw_fixture[0]].keys())[0] == player
    assert set(row.keys()).union(set(diff_gw_fixture)) == set(diff_gw_fixture)

def test_get_all_gw_transfers(player,diff_gw_fixture):
    row = get_gw_transfers([player], diff_gw_fixture, all = True)
    keys = list(row.keys())

    start = keys[-1]
    end = keys[0]
    rang = [i for i in range(start, end+1)]

    assert set(row.keys()).union(rang) == set(rang) 

def test_get_participant_entry(player, gw_fixture):

    team_list = get_participant_entry(player, gw_fixture)
    team_list_keys = list(team_list.keys())

    assert "gw" in team_list_keys
    assert "entry" in team_list_keys
    assert "active_chip" in team_list_keys
    assert "points_on_bench" in team_list_keys
    assert "event_transfers_cost" in team_list_keys
    assert "captain" in team_list_keys
    assert "players" in team_list_keys
    assert "bench" in team_list_keys


if __name__ == "__main__":
   print("use pytest to run tests")