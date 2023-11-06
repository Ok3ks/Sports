from utils import League, Player, Gameweek
from utils import get_participant_entry, get_gw_transfers
import pandas as pd
import numpy as np

#if __name__ == "__main__":
gw = 10
LEAGUE_ID = 1088941

league = League(LEAGUE_ID)
league.obtain_league_participants
print(league.obtain_league_participants())
one_results_list = league.get_all_participant_entries(gw)

df = Gameweek(gw)
df.weekly_score()

one_df = pd.DataFrame(one_results_list)
o_df = one_df[~one_df['players'].isna()]
#l

o_df['points_breakdown'] = o_df['players'].map(lambda x: [df.get_points(y) for y in x.split(",")])
o_df['captain_points'] = o_df['captain'].map(lambda x: df.get_points(x) * 2)
o_df['vice_captain_points'] = o_df['vice_captain'].map(lambda x: df.get_points(x))
o_df['rank'] = o_df['total_points'].rank(ascending=False)
o_df['rank'] = o_df['rank'].map(int)

#row = get_gw_transfers(participants_json.keys(), gw)
row = league.get_gw_transfers(gw)
print(row)
f = pd.DataFrame(row)
f = f.T

#print(f)
#f.reset_index()
#f.drop(axis ='Index', index= 'entry_id', inplace= True)

f['transfer_points_in'] = f['element_in'].map(lambda x: sum([df.get_points(y) for y in x]))
f['transfer_points_out'] = f['element_out'].map(lambda x:sum([df.get_points(y) for y in x]))
o_df['entry'] = o_df['entry'].astype(int)
o_df.rename(columns={'entry':'entry_id'}, inplace= True)

#Detecting Exceptional and Abysmal performances 
Q1,league_average,Q3 = df.basic_stats()
IQR = Q3 - Q1
exceptional = o_df[o_df['total_points'] > Q3 +1.5*IQR]
abysmal = o_df[o_df['total_points'] < Q1 - 1.5*IQR]

#
f['transfers'] = f['element_out'].map(lambda x: len(x))
f['delta'] = f['transfer_points_in'] - f['transfer_points_out']
f.reset_index(inplace= True)
f.rename(columns= {'index': 'entry_id'}, inplace= True)
f = o_df.merge(f, on='entry_id', how='right')

#
counts = f['element_out'].value_counts().reset_index().to_dict('list')
most_transf_out = [(counts['element_out'][i], counts['index'][i]) for i in range(3)]
least_transf_out = [(counts['element_out'][-i], counts['index'][-i]) for i in range(1,4)]

counts = f['element_in'].value_counts().reset_index().to_dict('list')
most_transf_in = [(counts['element_in'][i], counts['index'][i]) for i in range(3)]
least_transf_in = [(counts['element_in'][-i], counts['index'][-i]) for i in range(1,4)] #because -0 == 0

#
captain = o_df['captain'].value_counts().to_dict()
chips = o_df['active_chip'].value_counts().to_dict()
no_chips = f[f['active_chip'].isna()]
no_chips = no_chips.sort_values(by = 'delta', ascending=False)

###Print to terminal -- Work on next
#best_transf_in = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_out'].values[0][0])
best_transf_in = no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_out'].values[0][0]
#best_transf_out = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_in'].values[0][0])
best_transf_out = no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_in'].values[0][0]
#best_transf_points = max(no_chips['delta'])

#worst_transf_in = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0])
worst_transf_in = no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0]
#worst_transf_out = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_in'].values[0][0])
worst_transf_out = no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0]
#worst_transf_points = min(no_chips['delta'])
worst_transf_points = min(no_chips['delta'])

print("--")
print(best_transf_in, best_transf_out)

#write to json
##compute then display
#print("{} Made at least one transfer".format(len(f))) #use percentage to report
#print("{} participants took a hit".format(len(f[f['transfers'] > 1])))
#print(f"\nBest transfer decision of the week ")
#print("\t")

#for i in range(3):
    #player_in = get_player(no_chips.iloc[i,:]['element_in']) #
    #player_out = get_player(no_chips.iloc[i,:]['element_out'])
    #points_gained = no_chips.iloc[i,:]['delta']
    #player_id = no_chips.iloc[i,:]['entry_id']

    #print(f"Team name {participants_json[player_id]}\n")
    #print(f"Players In: {','.join(player_in)}\n Players Out: {','.join(player_out)} \n Points gained: {points_gained} ..")
    #print("\n")

#print(f"\nWorst transfer decision of the week ")
#print("\t")

#for i in range(1,3):
    #player_in = get_player(no_chips.iloc[-i,:]['element_in'])
    #player_out = get_player(no_chips.iloc[-i,:]['element_out'])
    #points_lost = no_chips.iloc[-1,:]['delta']
    #player_id = no_chips.iloc[-i,:]['entry_id']
    
    #print(f"Team name : {participants_json[player_id]}\n")
    #print(f"Players In: {','.join(player_in)}\n Players Out: {','.join(player_out)} \n Points lost: {points_lost}")
    #print("\n")

#print("\nMost transferred in players are :")
#for atuple in most_transf_in:
    #print("\t{}, transferred in {} times".format(get_player(atuple[1][0]), atuple[0]))

#print("\nLeast transferred in players are :")
#for atuple in least_transf_in:
    #print("\t{}, transferred in {} times".format(get_player(atuple[1][0]), atuple[0]))

#print("\nMost transferred out players are :") 
#for atuple in most_transf_out:
    #print("\t{}, transferred in {} times".format(get_player(atuple[1][0]), atuple[0]))

#print("\nLeast transferred out players are :")
#for atuple in least_transf_out:
    #print("\t{}, transferred in {} times".format(get_player(atuple[1][0]), atuple[0]))

#print("\nCaptain stats of the week")
#for key,value in captain.items():
    #print("\t{}, was captained {} times. Total Points = {}".format(get_player(int(key)), value, get_points(key, gw,df)*2))

#print("\nChip Usage")
#for key,value in chips.items():
    #print("\t{}, was activated by {} people.".format(key, value)) #how many people left

#print("\n")
#for i,j in zip(exceptional['entry_id'], exceptional['total_points']):
    #player_name = participants_json.get(i)
    #print(f"Player {player_name} scored {j} points, {j - league_average} above the league average")

#print("\n")
#for i,j in zip(abysmal['entry_id'], abysmal['total_points']):
    #player_name = participants_json.get(i)
    #print(f"Player {player_name} scored {j} points, {j - league_average} below the league average")

#functionality to sort by total points and design appropriately

