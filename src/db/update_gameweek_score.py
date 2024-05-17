import pandas as pd
from src.db.db import create_connection_engine,get_teams,get_position


from sqlalchemy import Integer,Boolean,Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

import requests
from src.urls import GW_URL

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
    print(df[df['in_dreamteam'] == True])
    ##Combining all gameweeks into one database, which is why I am appending files
    #add team and position

    df['team'] = get_teams(id = df['player_id'].to_list())
    print(df.head())
    df['position'] = get_position(id = df['player_id'].to_list())
    #print(df.tail())

    df.to_sql(f"Player_gameweek_score", conn, if_exists='append', method= 'multi')
    print("Data insert successful")

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog = "update_gameweek_score", description = "Provide Gameweek ID")

    parser.add_argument('-g', '--gameweek_id', type= int, help = "Gameweek you are trying to get a report of")
    args = parser.parse_args()
    connection = create_connection_engine("fpl") #Add database directory as constant

    try:
        update_db_gameweek_score(connection, args.gameweek_id)
    except ValueError:
        print("Debug and find error")
    