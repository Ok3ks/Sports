#from utils import Gameweek, Player, League
import pandas as pd
import sqlite3
from sqlite3 import Error, OperationalError

from os.path import realpath,join
from paths import APP_DIR
from sqlalchemy import Integer,create_engine, select, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase

import requests
from urls import GW_URL

#clean up
class Base(DeclarativeBase):
    pass

class GameweekScores(Base):
    
    __tablename__ = "Gameweek" #issues with dynamically changing gameweek name

    player_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    minutes: Mapped[int] = mapped_column(Integer)
    goals_scored: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    clean_sheets: Mapped[int] = mapped_column(Integer)
    goals_conceded:Mapped[int] = mapped_column(Integer)
    own_goals:Mapped[int] = mapped_column(Integer)
    penalties_saved:Mapped[int] = mapped_column(Integer)
    penalties_missed:Mapped[int] = mapped_column(Integer)
    yellow_cards:Mapped[int] = mapped_column(Integer)
    red_cards:Mapped[int] = mapped_column(Integer)
    saves:Mapped[int] = mapped_column(Integer)
    bonus:Mapped[int] = mapped_column(Integer)
    bps:Mapped[int] = mapped_column(Integer)
    influence:Mapped[int] = mapped_column(Integer)
    threat:Mapped[int] = mapped_column(Integer)
    ict_index:Mapped[int] = mapped_column(Integer)
    starts:Mapped[int] = mapped_column(Integer)
    expected_goals:Mapped[int] = mapped_column(Integer)
    expected_assists:Mapped[int] = mapped_column(Integer)
    expected_goal_involvements:Mapped[int] = mapped_column(Integer)
    expected_goals_conceded: Mapped[int] = mapped_column(Integer)
    total_points:Mapped[int] = mapped_column(Integer)
    in_dreamteam: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"""player_id:{self.player_id}, minutes:{self.minutes}, goals_scored:{self.goals_scored}
                """
#Add functions to classes
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection has been created successfully")
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, gw):
    try:
        create_table_sql=f"""CREATE TABLE IF NOT EXISTS GAMEWEEK_{gw} (
                            player_id INTEGER PRIMARY KEY,
                            minutes INTEGER (10),
                            goals_scored INTEGER (10),
                            assists INTEGER (10),
                            clean_sheets INTEGER (10),
                            goals_conceded INTEGER (10),
                            own_goals INTEGER (10),
                            penalties_saved INTEGER (10),
                            penalties_missed INTEGER (10),
                            yellow_cards INTEGER (10),
                            red_cards INTEGER (10),
                            saves INTEGER (10),
                            bonus INTEGER (10),
                            bps INTEGER (10),
                            influence INTEGER (10),
                            threat INTEGER (10),
                            ict_index INTEGER (10),
                            starts INTEGER (10),
                            expected_goals INTEGER (10),
                            expected_assists INTEGER (10),
                            expected_goal_involvements INTEGER (10),
                            expected_goals_conceded INTEGER (10),
                            total_points INTEGER (10),
                            in_dreamteam VARCHAR (10) 
                        );
                        """
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    return conn

def insert(conn, data, gw):
    try:
        #assert columns in data - conftest 
        data.to_sql(f"Gameweek_{gw}",conn,if_exists='replace',index=False)
        conn.commit()
        print("Data Insert Successful")
    except Error as e:
        print(e)
    else:
        print("Pass a dataframe as data")

def insert_from_json(conn, path):
    file = pd.read_json(path)
    insert(conn, data = file)

def update_db_gameweek_score(conn, gw):
    """This function retrieves current information of players
    from the API"""
    
    r = requests.get(GW_URL.format(gw))
    r = r.json()

    temp = {item['id']:item['stats'] for item in r['elements']}
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

    df.reset_index(level= 0, names = 'player_id', inplace = True)
    #df['event'] = gw

    insert(conn, df, gw)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog = "update_gameweek_score", description = "Provide Gameweek ID and League ID")

    parser.add_argument('-g', '--gameweek_id', type= int, help = "Gameweek you are trying to get a report of")
    args = parser.parse_args()
    connection = create_connection(realpath(join(APP_DIR,"fpl"))) #Add database directory as constant

    try:
        update_db_gameweek_score(connection, args.gameweek_id)
    except ValueError:
        print("Gameweek is unavailable")
    