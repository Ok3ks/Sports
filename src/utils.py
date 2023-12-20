import requests
import time
import pandas as pd
import json
import numpy as np

from os.path import join, realpath


from src.urls import GW_URL,FIXTURE_URL,TRANSFER_URL, HISTORY_URL, FPL_URL
from src.urls import H2H_LEAGUE, LEAGUE_URL, FPL_PLAYER
from functools import lru_cache

from src.paths import APP_DIR
from src.db import Player
from typing import List, Union

def to_json(x:dict, fp):
    with open(fp, 'w') as outs:
        json.dump(x, outs)
    print(f"{x.keys()} stored in Json successfully. Find here {fp}")

def get_basic_stats(total_points:List[Union[int,float]]):
    """Measures of Central Tendency for Total points"""
    average = np.mean(total_points)
    Q3 = np.percentile(total_points, 75)
    Q1 = np.percentile(total_points, 25)
    return Q1,average,Q3

def parse_transfers(item:dict) -> dict:
    row = {}

    row[item['entry']] = row.get(item['entry'], {})
    row[item['entry']]['element_in'] = row[item['entry']].get('element_in', [])
    row[item['entry']]['element_out'] = row[item['entry']].get('element_out', [])
    row[item['entry']]['element_in'].append(item['element_in'])
    row[item['entry']]['element_out'].append(item['element_out'])     
   
    return row

def check_gw(gw):
    if type(gw) == int:
        assert gw in range(1,39), 'Only 38 gameweeks in a season, Choose value between 1 and 38 or all'
    else:
        for i in gw:
            check_gw(i)

def get_gw_transfers(alist:List[int], gw:Union[int,List[int]], all = False) -> dict : 
    """Input is a list of entry_id. Gw is the gameweek number.
    'all' toggles between extracting all gameweeks or not"""
    
    row =  {}

    check_gw(gw)
    
    for entry_id in alist:
        r = requests.get(TRANSFER_URL.format(entry_id))
        if r.status_code == 200:
            obj = r.json()
            for item in obj:
                if all:
                    row[item['event']] = parse_transfers(item)
                else: 
                    if type(gw) == int and int(item['event']) == gw:
                        row = parse_transfers(item)
                    elif type(gw) == list:
                        if int(item['event']) in gw:
                            row[item['event']] = parse_transfers(item)
        else:
            print("{} does not exist or Transfer URL endpoint unavailable".format(entry_id))
    return row

def get_participant_entry(entry_id:int, gw:int) -> dict:

    """Calls an Endpoint to retrieve a participants entry"""

    assert gw in range(1,39), 'Only 38 gameweeks in a season, Choose value between 1 and 38 or all'
    r = requests.get(FPL_PLAYER.format(entry_id, gw))
    
    print("Retrieving results, participant {} for event = {}".format(entry_id, gw))
    team_list = {'auto_subs' : {'in': [], 'out': []}}

    if r.status_code == 200:
        obj = r.json()
        team_list['gw'] = gw
        team_list['entry'] = entry_id
        team_list['active_chip'] = obj['active_chip']
        
        team_list['points_on_bench'] = obj['entry_history']['points_on_bench']
        team_list['total_points'] = obj['entry_history']['points']
        team_list['points_on_bench'] = obj['entry_history']['points_on_bench']
        team_list['event_transfers_cost'] = obj['entry_history']['event_transfers_cost']

        if obj['automatic_subs']:
            for item in obj['automatic_subs']:
                team_list['auto_subs']['in'].append(item['element_in'])
                team_list['auto_subs']['out'].append(item['element_out'])

        for item in obj['picks']:
            if item['is_captain']:
                team_list['captain'] = int(item['element'])
            elif item['is_vice_captain']:
                team_list['vice_captain'] = int(item['element'])
            else:
                if item['multiplier'] != 0:
                    if 'players' not in list(team_list.keys()):
                        team_list['players'] = str(item['element'])
                    else: 
                        team_list['players'] = team_list['players'] + ','+ str(item['element'])
                else:
                    if 'bench' not in list(team_list.keys()):
                        team_list['bench'] = str(item['element'])
                    else: 
                        team_list['bench'] = team_list['bench'] + ','+ str(item['element'])
    else:
        print("{} does not exist".format(entry_id))
    return team_list

#class gw():
    #def __init__(self,gameweek:range(1,39)):
        #self.gw = gameweek
        #self.prev_gw = max(gameweek - 1, 1)
        #self.next_gw = min(gameweek + 1, 38)
#add test
def get_curr_event():
    r = requests.get(FPL_URL)

    curr_event = []
    r = r.json()
    for event in r['events']:
        if event['is_current']:
            curr_event.append(event['id'])
            curr_event.append((event['finished'], event['data_checked']))
    return curr_event

#add test
class Participant():
    def __init__(self, entry_id, gw = get_curr_event()[0]):
        self.participant = entry_id
        self.gw = gw

    def get_all_week_entries(self):
        self.all_gw_entries = [get_participant_entry(self.participant,gw) for gw in range(1, self.gw+1)]
        return self.all_gw_entries
    
    def get_all_week_transfers(self):
        self.all_gw_transfers = [get_gw_transfers(self.participant,gw) for gw in range(1, self.gw+1)]
        return self.all_gw_transfers

class League():
    def __init__(self, league_id):
        self.league_id = league_id
        self.participants = []

    def obtain_league_participants(self):
        """This function uses the league url as an endpoint to query for participants of a league at a certain date.
        Should be used to update participants table in DB """
        
        if self.participants:
            return self.participants
        
        else:
            has_next = True
            PAGE_COUNT = 1
            while has_next:
                r = requests.get(LEAGUE_URL.format(self.league_id, PAGE_COUNT))
                obj =r.json()
                assert r.status_code == 200, 'error connecting to the endpoint'
                del r
                self.participants.extend(obj['standings']['results'])
                has_next = obj['standings']['has_next']
                PAGE_COUNT += 1
                time.sleep(2)
                print("All participants have been extracted")
        return self.participants
    
    def get_participant_name(self) -> dict:
        """ Creates participant id to name hash table """
        assert len(self.participants) > 0, 'No participants, call obtain_league_participants() first'
        output = {str(participant['entry']) : participant['entry_name'] for participant in self.participants}
        return output

    def get_all_participant_entries(self,gw) -> list:
        self.obtain_league_participants()
        self.participant_entries = [get_participant_entry(participant['entry'],gw) for participant in self.participants]
        return self.participant_entries
    
    def get_gw_transfers(self,gw) -> dict:
        if len(self.participants) > 1:
            self.entry_ids =[participant['entry'] for participant in self.participants]
            self.transfers = get_gw_transfers(self.entry_ids,gw)
        else:
            self.obtain_league_participants()
            self.transfers = get_gw_transfers(self.entry_ids,gw)
        return self.transfers
    

if __name__ == "__main__":
    print(get_curr_event())
    #participant = Participant(98120)
    #league.obtain_league_participants()
    #print(participant.get_all_week_entries())