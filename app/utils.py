import requests
import time
import pandas as pd
import json
import numpy as np

transfer_url = 'https://fantasy.premierleague.com/api/entry/{}/transfers/'
league_url = "https://fantasy.premierleague.com/api/leagues-classic/{}/standings/?page_standings={}"
fpl_player = "https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/"
gw_url = "https://fantasy.premierleague.com/api/event/{}/live/"


with open('json/epl_players.json') as ins_3:
    epl_players = json.load(ins_3)

def weekly_score(gw):

    r = requests.get(gw_url.format(gw))
    r = r.json()

    temp = {item['id'] :item['stats'] for item in r['elements']}
    df = pd.DataFrame(temp)
    df = df.T

    df.columns = ['minutes',
        'goals_scored',
        'assists',
        'clean_sheets',
        'goals_conceded',
        'own_goals',
        'penalties_saved',
        'penalties_missed',
        'yellow_cards',
        'red_cards',
        'saves',
        'bonus',
        'bps',
        'influence',
        'creativity',
        'threat',
        'ict_index',
        'starts',
        'expected_goals',
        'expected_assists',
        'expected_goal_involvements',
        'expected_goals_conceded',
        'total_points',
        'in_dreamteam']

    df.reset_index(level= 0, names = 'id', inplace = True)
    df['event'] = gw

    return df

def get_points(id, gw,df): #extract from DB
    """Obtains player points using ID"""

    if id == "NaN":
        print("{id} not found in db for week {gw}")
        pass
    else:
        assert gw in df['event'], 'All_df is not updated'
        temp_df = df[df['event'] == gw] #gw
        point = temp_df[temp_df['id'] == int(id)]['total_points'].values.tolist()
        #player = id_2_player.get(i)         #change to database
        return int(point[0]) 

def basic_stats(df):

    """Measures of Central Tendency for Total points"""
    average = np.mean(df['total_points'])
    IQR = np.percentile(df['total_points'], 75) - np.percentile(df['total_points'], 25)
    Q3 = np.percentile(df['total_points'], 75)
    Q1 = np.percentile(df['total_points', 25])

    return average,Q3,Q1,IQR

def get_player(i):
    """Obtains player name from id"""
    out = []
    if isinstance(i, list):
        for item in i:
            out.append(epl_players.get(str(item)))
        return out
    else:
        return epl_players.get(str(i))

def get_gw_transfers(alist,gw:int, all = False):
    """Input is a list of entry_id. Gw is the gameweek number
    All toggles between extracting all gameweeks or not"""
    row =  {}
    for entry_id in alist:
        r = requests.get(transfer_url.format(entry_id))

        if r.status_code == 200:
            obj = r.json()
            for item in obj:
                if all:
                    row[item['event']] = row.get(item['event'], {})
                    row[item['event']]['entry_id'] = item['entry']

                    row[item['event']][item['entry']] = row.get(item['entry'], {})

                    row[item['event']][item['entry']]['element_in'] = row[item['event']][item['entry']].get('element_in', [])
                    row[item['event']][item['entry']]['element_out'] = row[item['event']][item['entry']].get('element_out', [])

                    row[item['event']][item['entry']]['element_in'].append(item['element_in'])
                    row[item['event']][item['entry']]['element_out'].append(item['element_out'])
                else: 
                    if int(item['event']) == gw:
                        row[item['entry']] = row.get(item['entry'], {})

                        row[item['entry']]['element_in'] = row[item['entry']].get('element_in', [])
                        row[item['entry']]['element_out'] = row[item['entry']].get('element_out', [])

                        row[item['entry']]['element_in'].append(item['element_in'])
                        row[item['entry']]['element_out'].append(item['element_out'])     

    return row
        

#
def get_participant_entry(entry_id, gw):
    r = requests.get(fpl_player.format(entry_id, gw))
    #Logs
    print("Retrieving results, participant {} for event = {}".format(entry_id, gw))

    obj = r.json()
    team_list = {'auto_subs' : {'in': [], 'out': []}}
    
    if r.status_code == 200:

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
    #time.sleep(3)
    return team_list

#Leagues
def obtain_league_participants(league_id):
    """ This function uses the league url as an endpoint to query for participants of a league at a certain date.
    Should be used to update participants table in DB """
    
    has_next = True
    entries = []
    PAGE_COUNT = 1

    while has_next:
        r = requests.get(league_url.format(league_id, PAGE_COUNT))
        obj =r.json()

        assert r.status_code == 200, 'error connecting to the endpoint'
        del r
        entries.extend(obj['standings']['results'])
        has_next = obj['standings']['has_next']
        PAGE_COUNT += 1
        time.sleep(2)
    return entries

#get weekly points from api