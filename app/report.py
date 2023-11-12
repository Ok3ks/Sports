from utils import League, Player, Gameweek,get_player, to_json
from utils import get_participant_entry, get_gw_transfers
import pandas as pd

from functools import lru_cache
import os 

from paths import WEEKLY_REPORT_DIR

gw = 11
LEAGUE_ID = 1088941

#Downtown-85647
#Uptown-1088941

#classWeeklyReport

class LeagueWeeklyReport(League):

    def __init__(self, gw: int, league_id:int):
        super().__init__(league_id)
        self.gameweek = Gameweek(gw)

    @lru_cache
    def weekly_score_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""
        
        self.gameweek.weekly_score()
        
        one_df = pd.DataFrame(self.get_all_participant_entries(self.gameweek.gw))
        self.o_df = one_df[~one_df['players'].isna()]

        self.o_df['points_breakdown'] = self.o_df['players'].map(lambda x: [self.gameweek.get_points(y) for y in x.split(",")])
        self.o_df['captain_points'] = self.o_df['captain'].map(lambda x: self.gameweek.get_points(x) * 2)
        self.o_df['vice_captain_points'] = self.o_df['vice_captain'].map(lambda x: self.gameweek.get_points(x))
        
        self.o_df['rank'] = self.o_df['total_points'].rank(ascending=False)
        self.o_df['rank'] = self.o_df['rank'].map(int)
        return self.o_df

    @lru_cache
    def merge_league_weekly_transfer(self):

        """Merges Weekly score dataframe with transfers dataframe"""
        self.f = pd.DataFrame(self.get_gw_transfers(self.gameweek.gw))
        self.f = self.f.T

        self.f['transfer_points_in'] = self.f['element_in'].map(lambda x: sum([self.gameweek.get_points(y) for y in x]))
        self.f['transfer_points_out'] = self.f['element_out'].map(lambda x:sum([self.gameweek.get_points(y) for y in x]))
        self.f['transfers'] = self.f['element_out'].map(lambda x: len(x))
        self.f['delta'] = self.f['transfer_points_in'] - self.f['transfer_points_out']

        self.o_df['entry'] = self.o_df['entry'].astype(int)
        self.o_df.rename(columns={'entry':'entry_id'}, inplace= True)

        self.f.reset_index(inplace= True)
        self.f.rename(columns= {'index': 'entry_id'}, inplace= True)
        self.f = self.o_df.merge(self.f, on='entry_id', how='right')
        return self.f
    
    def add_auto_sub(self):
        
        self.f['auto_sub_in_player'] = self.f['auto_subs'].map(lambda x: x['in'])
        self.f['auto_sub_out_player'] = self.f['auto_subs'].map(lambda x: x['out'])
        self.f['auto_sub_in_points'] = self.f['auto_sub_in_player'].map(lambda x: sum([self.gameweek.get_points(y) for y in x]))
        self.f['auto_sub_out_points'] = self.f['auto_sub_in_player'].map(lambda x: sum([self.gameweek.get_points(y) for y in x]))
        
    def create_report(self,fp):

        self.captain = self.o_df['captain'].value_counts().to_dict()
        self.chips = self.o_df['active_chip'].value_counts().to_dict()
        self.no_chips = self.f[self.f['active_chip'].isna()]

        def outliers():
            Q1,league_average,Q3 = self.gameweek.basic_stats()
            IQR = Q3 - Q1

            exceptional_df = self.o_df[self.o_df['total_points'] > Q3 +1.5*IQR]
            abysmal_df = self.o_df[self.o_df['total_points'] < Q1 - 1.5*IQR]

            exceptional = []
            abysmal = []

            for i,j in zip(exceptional_df['entry_id'], exceptional_df['total_points']):
                exceptional.append((i,j))

            for i,j in zip(abysmal_df['entry_id'], abysmal_df['total_points']):
                abysmal.append((i,j))

            return {"exceptional": exceptional ,"abysmal": abysmal, "league_average": league_average}
#       
        def out_transfer_stats():
            counts = self.f['element_out'].value_counts().reset_index().to_dict('list')
            most_transf_out = [(counts['element_out'][i], counts['index'][i]) for i in range(3)]
            least_transf_out = [(counts['element_out'][-i], counts['index'][-i]) for i in range(1,4)]
            return {"most_transferred_out": most_transf_out, "least_transferred_out": least_transf_out}

        def in_transfer_stats():
            """Output = {"most_transferred_in" : [], "least_transferred_in": []}"""

            counts = self.f['element_in'].value_counts().reset_index().to_dict('list')
            most_transf_in = [(counts['element_in'][i], counts['index'][i]) for i in range(3)]
            least_transf_in = [(counts['element_in'][-i], counts['index'][-i]) for i in range(1,4)] #because -0 == 0
            return {"most_transferred_in" :most_transf_in, "least_transferred_in": least_transf_in}
#
        self.no_chips = self.no_chips.sort_values(by = 'delta', ascending=False)

        def worst_transfer_in():
            """Output = {"worst_transfer_in":[()]}"""
            worst_transfer_in = []

            for i in range(1,3):
                player_in = self.no_chips.iloc[-i,:]['element_in']
                player_out = self.no_chips.iloc[-i,:]['element_out']
                points_lost = int(self.no_chips.iloc[-1,:]['delta'])
                player_id = str(self.no_chips.iloc[-i,:]['entry_id'])
                
                worst_transfer_in.append((player_id, player_in, player_out, points_lost))
            return {"worst_transfer_in": worst_transfer_in}

        def best_transfer_in():
            """Output = {"best_transfer_in":[()]}"""
            best_transfer_in = []

            for i in range(1,3):
                player_in = self.no_chips.iloc[-i,:]['element_in']
                player_out = self.no_chips.iloc[-i,:]['element_out']
                points_gained = int(self.no_chips.iloc[-1,:]['delta'])
                player_id = str(self.no_chips.iloc[-i,:]['entry_id'])
                
                best_transfer_in.append((player_id, player_in, player_out, points_gained))
            return {"best_transfer_in": best_transfer_in}
        
        def jammy_points():
            """ """
            jammy_points = []
            self.f= self.f.sort_values(by='auto_sub_in_points', ascending=False)
            for i in range(3):
                auto_sub_in = self.f.iloc[i,:]['auto_sub_in_player']
                auto_sub_out = self.f.iloc[i,:]['auto_sub_out_player']
                auto_sub_points = int(self.f.iloc[i,:]['auto_sub_in_points'])
                player_id = str(self.f.iloc[i,:]['entry_id'])

                jammy_points.append((player_id, auto_sub_in, auto_sub_out, auto_sub_points, ))
            return {"jammy_points": jammy_points}
        
        def most_points_on_bench():

            self.f['points_on_bench'] = self.no_chips['points_on_bench'].astype(int)
            self.f = self.f.sort_values(by = 'points_on_bench', ascending= False)

            most_points = []
            for i in range(3):
                player_on_bench = self.f.iloc[i,:]['bench'].split(",")
                points_on_bench = int(self.f.iloc[i,:]['points_on_bench'])
                player_id = str(self.f.iloc[i,:]['entry_id'])
                most_points.append((player_id, player_on_bench, points_on_bench))
            return {"most_points" :most_points}

        output = {"captain":self.captain, "chips": self.chips }
        output.update(outliers())
  
        output.update(out_transfer_stats())
        output.update(in_transfer_stats())

        output.update(best_transfer_in())
        output.update(worst_transfer_in())
        
        output.update(most_points_on_bench())
        output.update(jammy_points())

        to_json(output, fp)

#Output of report page should be a json for a django template

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(prog = "weeklyreport", description = "Provide Gameweek ID and League ID")

    parser.add_argument('-g', '--gameweek_id', type= int, help = "Gameweek you are trying to get a report of")
    parser.add_argument('-l', '--league_id', type= int, help = "League_ID you are interested in")

    args = parser.parse_args()

    test = LeagueWeeklyReport(args.gameweek_id, args.league_id)
    test.weekly_score_transformation()
    test.merge_league_weekly_transfer()
    test.add_auto_sub()

    #output_name = os.path.join(REPORT_DIR, str(args.league_id)+'_'+ str(args.gameweek_id))
    test.create_report(f"{WEEKLY_REPORT_DIR}/{str(args.league_id)}_{str(args.gameweek_id)}.json")  #Move to S3
