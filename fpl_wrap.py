
import operator
import requests
import pandas as pd
import os
from os.path import join, realpath

from src.urls import FPL_PLAYER, HISTORY_URL
from src.paths import FPL_WRAP_DIR
import seaborn.objects as so

def get_participant_entry(entry_id, gw):
    r = requests.get(FPL_PLAYER.format(entry_id, gw))
    #Logs
    print("Retrieving results, participant {} for event = {}".format(entry_id, gw))

    obj = r.json()
    team_list = {'auto_subs' : {'in': [], 'out': []}, 'players':[], 'bench':[]}
    
    if r.status_code == 200:

        team_list['gw'] = str(gw)
        team_list['entry'] = str(entry_id)
        team_list['active_chip'] = obj['active_chip']
        
        team_list['points_on_bench'] = str(obj['entry_history']['points_on_bench'])
        team_list['total_points'] = str(obj['entry_history']['points'])
        team_list['points_on_bench'] = str(obj['entry_history']['points_on_bench'])
        team_list['event_transfers_cost'] = str(obj['entry_history']['event_transfers_cost'])

        if obj['automatic_subs']:
            for item in obj['automatic_subs']:
                team_list['auto_subs']['in'].append(str(item['element_in']))
                team_list['auto_subs']['out'].append(str(item['element_out']))

        for item in obj['picks']:
            if item['is_captain']:
                team_list['captain'] = str(int(item['element']))
                team_list['players'].append(str(item['element']))
            elif item['is_vice_captain']:
                team_list['vice_captain'] = str(int(item['element']))
                team_list['players'].append(str(item['element']))
            else:
                if item['multiplier'] != 0:
                    team_list['players'].append(str(item['element']))
                    team_list['bench'] = str(item['element'])
    return team_list


def frequency_counter(metric:dict, key = 'players'):
    assert key in metric.keys()
    count = {}
    for i in metric[key]:
        count[i] = count.get(i, 0) + 1

    count = sorted(count.items(), key=operator.itemgetter(1), reverse=True)

    return {key: count}


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog = "FPLWRAP", description = "Provide ")

    parser.add_argument('-g', '--gameweek', type= int, help = "Gameweek you are trying to get a report of")
    parser.add_argument('-l', '--player_id', type= int, help = "ID of pkayer you're interested in ")
    args = parser.parse_args()

    all_gw_entries = [get_participant_entry(args.player_id, i) for i in range(args.gameweek)]
    grand_dict = {key:[] for key in all_gw_entries[1].keys()}

    print(grand_dict)

    all_df = pd.DataFrame(all_gw_entries[1:])
    all_df.fillna(value = 0, inplace= True)
    all_df['gw'] = all_df['gw'].astype(int)
    all_df['points_on_bench'] = all_df['points_on_bench'].astype(int)

    all_df.fillna(value = 0, inplace= True)
    all_df['gw'] = all_df['gw'].astype(int)
    all_df['points_on_bench'] = all_df['points_on_bench'].astype(int)

    for i in all_df.columns:
        print(all_df[i].dtypes)

    r = requests.get(HISTORY_URL.format(args.player_id))
    r = r.json()

    history = r['current']
    history = pd.DataFrame(history) 
    history['value'] = history['value']/10
    history['bank'] = history['bank']/10

    history.rename(columns={'event':'gameweek'}, inplace=True)
    history.set_index("gameweek", inplace=True)


    captain_bar_chart = so.Plot(all_df, x = 'captain').add(so.Bars(), so.Count())\
        .scale(y = so.Continuous().tick(every=1))\
        .label(y = "Count")
            
   
    os.makedirs(realpath(join(FPL_WRAP_DIR, str(args.player_id))), exist_ok=True)
    captain_bar_chart.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), 'captain_bar_chart.png')))

    points_on_bench =  so.Plot(all_df, y = 'points_on_bench',  x="gw")\
                    .add(so.Lines())\
                    .add(so.Dots(color= 'C2'))\
                    .scale(y = so.Continuous().tick(every=2),
                        x = so.Continuous().tick(every=1))
                    
    points_on_bench.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), 'points_on_bench.png')))
    
    line_plot =  so.Plot(history, x = 'gameweek',  y="points")\
                .add(so.Lines(color= 'C1'))\
                .add(so.Dots(color= 'C2'), so.Agg('min'))\
                .add(so.Dots(color= 'C2'), so.Agg('max'))\
                .scale(x=so.Continuous().tick(every=1),
        color=so.Continuous().tick(at=history.index))
    line_plot.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), 'line_plot.png')))

    rank_plot = so.Plot(history, x = 'gameweek',  y="overall_rank")\
                .add(so.Lines(color= 'C1'))\
                .scale(x=so.Continuous().tick(every=1),
                       y =so.Continuous().label(like="{x:,}"),
        color=so.Continuous().tick(at=history.index))\
        .limit(y = (2_000_000, 0))\
        .label(title= "Overall rank versus gameweek", )
    rank_plot.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), 'rank_plot.png')))  
