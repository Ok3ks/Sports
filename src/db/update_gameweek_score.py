#from utils import Gameweek, Player, League
import pandas as pd
import sqlite3
from sqlite3 import Error, OperationalError
from src.db.db import create_connection_engine

from os.path import realpath,join
from src.paths import BASE_DIR
from sqlalchemy import Integer,create_engine, select, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase
from src.db.db import insert, insert_from_json

import requests
from src.urls import GW_URL

#clean up
class Base(DeclarativeBase):
    pass

def update_db_gameweek_score(conn, gw):
    """This function retrieves current information of players
    from the API"""
    
    r = requests.get(GW_URL.format(gw))
    r = r.json()

    temp = {item['id']:item['stats'] for item in r['elements']}
    df = pd.DataFrame(temp)
    df = df.T
    df['gameweek'] = gw
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
            'in_dreamteam',
            'gameweek']

    df.reset_index(level= 0, names = 'player_id', inplace = True)
    #df['event'] = gw

    insert(conn, df, gw)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog = "update_gameweek_score", description = "Provide Gameweek ID and League ID")

    parser.add_argument('-g', '--gameweek_id', type= int, help = "Gameweek you are trying to get a report of")
    args = parser.parse_args()
    connection = create_connection_engine("fpl") #Add database directory as constant

    try:
        update_db_gameweek_score(connection, args.gameweek_id)
    except ValueError:
        print("Gameweek is unavailable")
    