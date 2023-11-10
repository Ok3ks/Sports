from utils import League, Player, Gameweek,get_player
from utils import get_participant_entry, get_gw_transfers
import pandas as pd
import numpy as np
import json

gw = 11
LEAGUE_ID = 1088941

#Downtown-85647
#Uptown-1088941
#cache functions and save compute

if __name__ == "__main__":
    
    import argparse
    args = argparse.PARSER("Provide Gameweek ID and League ID")

    args.add_argument('gameweek', type= int)
    #where to write output json to 


with open('/Users/max/Desktop/Sports/app/json/downtown_players.json') as ins_3:
    participants_json = json.load(ins_3)

#classWeeklyReport
class LeagueWeeklyReport(League):

    def __init__(self, gw: int, league_id:int):
        super().__init__(league_id)
        self.df = Gameweek(gw)

    def weekly_score_transformation(self):

        """Transforms weekly score into Dataframe"""

        one_df = pd.DataFrame(self.get_all_participant_entries(self.df.gw))
        self.o_df = one_df[~one_df['players'].isna()]

        self.o_df['points_breakdown'] = self.o_df['players'].map(lambda x: [self.df.get_points(y) for y in x.split(",")])
        self.o_df['captain_points'] = self.o_df['captain'].map(lambda x: self.df.get_points(x) * 2)
        self.o_df['vice_captain_points'] = self.o_df['vice_captain'].map(lambda x: self.df.get_points(x))
        
        self.o_df['rank'] = self.o_df['total_points'].rank(ascending=False)
        self.o_df['rank'] = self.o_df['rank'].map(int)
        return self.o_df
    
    #row = get_gw_transfers(participants_json.keys(), gw)
    def merge_league_weekly_transfer(self):

        self.f = pd.DataFrame(self.get_gw_transfers(self.df.gw))
        self.f = self.f.T

        self.f['transfer_points_in'] = self.f['element_in'].map(lambda x: sum([self.df.get_points(y) for y in x]))
        self.f['transfer_points_out'] = self.f['element_out'].map(lambda x:sum([self.df.get_points(y) for y in x]))
        self.f['transfers'] = self.f['element_out'].map(lambda x: len(x))
        self.f['delta'] = self.f['transfer_points_in'] - self.f['transfer_points_out']

        self.o_df['entry'] = self.o_df['entry'].astype(int)
        self.o_df.rename(columns={'entry':'entry_id'}, inplace= True)

        self.f.reset_index(inplace= True)
        self.f.rename(columns= {'index': 'entry_id'}, inplace= True)
        self.f = self.o_df.merge(self.f, on='entry_id', how='right')

        return self.f

    def create_report(self):

        captain = self.o_df['captain'].value_counts().to_dict()
        chips = self.o_df['active_chip'].value_counts().to_dict()
        no_chips = self.f[self.f['active_chip'].isna()]

        def outliers():
            
            Q1,league_average,Q3 = self.df.basic_stats()
            IQR = Q3 - Q1

            exceptional = self.o_df[self.o_df['total_points'] > Q3 +1.5*IQR]
            abysmal = self.o_df[self.o_df['total_points'] < Q1 - 1.5*IQR]

            return {"exceptional": exceptional,"abysmal" : abysmal}
#       
        def out_transfer_stats():
            counts = self.f['element_out'].value_counts().reset_index().to_dict('list')
            most_transf_out = [(counts['element_out'][i], counts['index'][i]) for i in range(3)]
            least_transf_out = [(counts['element_out'][-i], counts['index'][-i]) for i in range(1,4)]
            return {"most_transferred_out": most_transf_out, "least_transferred_out": least_transf_out}

        def in_transfer_stats():
            counts = f['element_in'].value_counts().reset_index().to_dict('list')
            most_transf_in = [(counts['element_in'][i], counts['index'][i]) for i in range(3)]
            least_transf_in = [(counts['element_in'][-i], counts['index'][-i]) for i in range(1,4)] #because -0 == 0
            return {"most_transferred_in" :most_transf_in, "least_transferred_in": least_transf_in}
        #
        def best_transfer_in():

            ###Print to terminal -- Work on next
            best_transf_in = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_out'].values[0][0])
            #best_transf_in = no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_out'].values[0][0]
            best_transf_out = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_in'].values[0][0])
            #best_transf_out = no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_in'].values[0][0]
            best_transf_points = max(no_chips['delta'])

            return {"best_transfer_in": best_transf_in, "best_transf_out": best_transf_out, "best_transf_points": best_transf_points}

        def worst_transfer_in():
            worst_transf_in = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0])
            #worst_transf_in = no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0]
            worst_transf_out = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_in'].values[0][0])
            #worst_transf_out = no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0]
            #worst_transf_points = min(no_chips['delta'])
            worst_transf_points = min(no_chips['delta'])
            return {"worst_transfer_in": worst_transf_in, "worst_transf_out": worst_transf_out, "worst_transf_points" : worst_transf_points}

#Output of report page should be a json for a django template