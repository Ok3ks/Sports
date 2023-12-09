from app.src.utils import League, Player, Gameweek, to_json
from src.paths import WEEKLY_REPORT_DIR
from src.urls import FPL_PLAYER
from functools import lru_cache
import requests

import os 
import pandas as pd
from src.utils import get_basic_stats,get_participant_entry

from src.db import get_player, get_player_stats_from_db

#Refactor to composition instead of inheritance
class SpanReport():

    def __init__(self, player_id: int, span:int, gw: int):
        self.span = span
        self.gw = gw
        self.gameweek = Gameweek(gw)
        self.player_id = player_id

    @lru_cache
    def span_data_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""
        agg = []

        for i in range(self.gw-self.span, self.gw+1):
            agg.append(get_participant_entry(self.player_id, i))

        one_df = pd.DataFrame(agg)
        self.o_df = one_df[~one_df['players'].isna()]
        self.o_df['gw'] = self.o_df['gw'].astype(int)

        print(self.o_df)
        return self.o_df
    
#now analyse the span like others
#span report for leagues

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(prog = "weeklyreport", description = "Provide Gameweek ID and League ID")

    parser.add_argument('-p', '--player_id', type= int, help = "Player ID")
    parser.add_argument('-s', '--span', type = int, help= "Span of weeks to be analysed")
    parser.add_argument('-g', '--gameweek_id', type= int, help = "Last gameweek")

    args = parser.parse_args()

    subject = SpanReport(args.player_id, args.span, args.gameweek_id,  )
    subject.span_data_transformation()