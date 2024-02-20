#from utils import Gameweek, Player, League
import pandas as pd
import sqlite3
import pymysql
from sqlite3 import Error, OperationalError

from os.path import realpath,join
from src.paths import BASE_DIR

from sqlalchemy import Integer, String, create_engine, select,text,distinct,Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase,sessionmaker
from sqlalchemy import URL

import requests
from src.urls import FPL_URL



class Base(DeclarativeBase):
    pass

class Player(Base):
    __tablename__ = "EPL_PLAYERS_2023_1ST_HALF"

    player_id: Mapped[int] = mapped_column(Integer,primary_key = True)
    team: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    player_name: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Player(player_id={self.player_id}, team={self.team}, position ={self.position}, player_name={self.player_name})"

class PlayerGameweekScores(Base):
    __tablename__ = "Player_Gameweek_scores"

    player_id: Mapped[int] = mapped_column(Integer)
    minutes: Mapped[int]= mapped_column(Integer)
    goals_scored: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int]= mapped_column(Integer)
    clean_sheets:Mapped[int] = mapped_column(Integer)
    goals_conceded:Mapped[int] = mapped_column(Integer)
    own_goals:Mapped[int] = mapped_column(Integer)
    penalties_saved:Mapped[int] = mapped_column(Integer)
    penalties_missed:Mapped[int] = mapped_column(Integer)
    yellow_cards:Mapped[int] = mapped_column(Integer)
    red_cards: Mapped[int] = mapped_column(Integer)
    saves: Mapped[int] = mapped_column(Integer)
    bonus: Mapped[int]= mapped_column(Integer)
    bps: Mapped[int] = mapped_column(Integer)
    influence:Mapped[float] = mapped_column(Float)
    creativity: Mapped[float] = mapped_column(Float)
    threat: Mapped[float] = mapped_column(Float)
    ict_index: Mapped[float] = mapped_column(Float)
    starts: Mapped[float] = mapped_column(Float)
    expected_goals: Mapped[float] = mapped_column(Float)
    expected_assists: Mapped[float] = mapped_column(Float)
    expected_goal_involvements: Mapped[float] = mapped_column(Float)
    expected_goals_conceded: Mapped[float] = mapped_column(Float)
    total_points: Mapped[int] = mapped_column(Integer)
    in_dreamteam: Mapped[bool] = mapped_column(Boolean)
    gameweek: Mapped[int] = mapped_column(Integer,primary_key = True)


def insert(conn, data, gw):
    try:
        #assert columns in data - conftest 
        data.to_sql(f"Player_Gameweek_Scores",conn,if_exists='append',method = "multi", index=False)
        #conn.commit()
        print("Data Insert Successful")
    except Error as e:
        print(e)
        print("Pass a dataframe as data")

def insert_from_json(conn, path):
    file = pd.read_json(path)
    insert(conn, data = file)

def create_connection(db):
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost', 
            user='root',  
            password = "password", 
            db=db, 
        )
        #print("Connection has been created successfully")
        return conn
    except Error as e:
        print(e)
    return conn

def create_connection_engine(db):
    """Creates a SQLAlchemy engine with a mysql database"""

    url_object = URL.create(
        "mysql+pymysql",
        username="root",
        password="password", 
        host="localhost",
        database=db)

    #short syntax    
    #create_engine(f"mysql+pymysql://scott:tiger@localhost/{db}")
    return create_engine(url_object)

session = sessionmaker(create_connection_engine('fpl'))

def get_player(id, session = session):
    out = []
    with session() as session:
        if isinstance(id, list):
            for item in id:
                stmt = select(Player.player_name).where(Player.player_id == int(item))
                obj = session.scalars(stmt).all()
                out.append(obj[0])
            return out
        else:
            stmt = select(Player.player_name).where(Player.player_id == int(id))
            obj = session.scalars(stmt).one()
            return obj

def get_teams(session = sessionmaker(create_connection_engine('fpl'))):
    with session() as session:
        statement = select(distinct(Player.team))
        obj = session.execute(statement).all()
        return obj
    
def get_entry_ids(session = sessionmaker(create_connection_engine('fpl')), table_name = ''):
    with session() as session:
        statement = text(f"""SELECT id FROM {table_name} """)
        obj = session.execute(statement).all()
        return (i.id for i in obj)
    
#ORM for each gameweek
def get_player_stats_from_db(gw, session = session):
    stmt = text(f"SELECT player_id, total_points FROM Player_Gameweek_Scores WHERE gameweek = {gw}")
    #stmt = select(PlayerGameweekScores.total_points).where((PlayerGameweekScores.player_id == id)&(PlayerGameweekScores.gameweek == gw))
    with session() as session:
        c = session.execute(stmt).all()
        #c = session.scalars(stmt).all()
    return {i.player_id : i.total_points for i in c}

def check_minutes(id, gw, session = session):
    "Checks DB for captain's minutes"
    stmt = text(f"SELECT minutes FROM Player_Gameweek_Scores WHERE player_id={id} and gameweek = {gw}")
    with session() as session:
        c = session.execute(stmt)
    return c.fetchone()

def get_available_gameweek_scores(session = sessionmaker(create_connection_engine('fpl'))):

    #can be refactored to get_distinct of any column
    stmt = text(f"SELECT distinct(gameweek) FROM Player_Gameweek_Scores")
    with session() as session:
        c = session.execute(stmt)
    return c.fetchall()



def create_id_table(conn, table_name = "league_name"):

    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql=text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            player_id INTEGER PRIMARY KEY,
                            participant_entry_name VARCHAR (2000),
                            participant_player_name VARCHAR (200)
                        );
                        """)
        session = sessionmaker(conn)
        with session() as session:
            session.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    return conn




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Update Player information, this happens twice a year")
    
    #parser.add_argument('-t',"--table_name", type=str, help= "Table name", required=False)
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    
    args = parser.parse_args()
    engine = create_connection_engine(args.db_name) #Add database directory as constant
    session = sessionmaker(engine)
    print(get_player_stats_from_db(6))