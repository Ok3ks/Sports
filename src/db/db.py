#from utils import Gameweek, Player, League
import pandas as pd
import sqlite3
import pymysql

from sqlite3 import Error, OperationalError

from os.path import realpath,join
from src.paths import BASE_DIR

from src.paths import REPORT_DIR
from sqlalchemy import Integer, String, create_engine, select,text,distinct
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase,sessionmaker
from sqlalchemy import URL

from src.urls import FPL_URL

class Base(DeclarativeBase):
    pass

class Player_1(Base):
    __tablename__ = "EPL_PLAYERS_2023_1ST_HALF"

    player_id: Mapped[int] = mapped_column(Integer,primary_key = True)
    team: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    player_name: Mapped[str] = mapped_column(String)
    team_code : Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Player(player_id={self.player_id}, team={self.team}, position ={self.position}, player_name={self.player_name})"

class Player_2(Base):
    __tablename__ = "EPL_PLAYERS_2023_2ND_HALF"

    player_id: Mapped[int] = mapped_column(Integer,primary_key = True)
    team: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    player_name: Mapped[str] = mapped_column(String)
    team_code : Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Player(player_id={self.player_id}, team={self.team}, position ={self.position}, player_name={self.player_name})"

def create_connection(db, host = "localhost", user = "root", password = "password"):
    conn = None
    try:

        conn = pymysql.connect(
            host=host, 
            user=user,  
            password =password, 
            db=db, 
        )
        return conn
    except Error as e:
        print(e)
    return conn

def create_connection_engine(db, host = "localhost", user = "root", password = "password"):
    """Creates a SQLAlchemy engine with a mysql database"""

    url_object = URL.create(
        "mysql+pymysql",
        username=user,
        password=password, 
        host=host,
        database=db)

    #short syntax    
    #create_engine(f"mysql+pymysql://scott:tiger@localhost/{db}")
    return create_engine(url_object)

session = sessionmaker(create_connection_engine('fpl'))

def no_sql_db():
    return redis.Redis(
        host ="""redis-15909.c302.asia-northeast1-1
        .gce.cloud.redislabs.com""",
        port=15909,
        password='55DzcTvYLBDNTGOVBlUQg1BOs86lmX4N'
    )

def get_player(id:list, session = session):
    out = []
    with session() as session:
        if isinstance(id, list):
            for item in id:
                try:
                    stmt = select(Player_1.player_name).where(Player_1.player_id == int(item))
                    obj = session.scalars(stmt).all()
                    out.append(obj[0])
                except IndexError:
                    stmt = select(Player_2.player_name).where(Player_2.player_id == int(item))
                    obj = session.scalars(stmt).all()
                    out.append(obj[0])
            return out


#buggy, does not work with id 
def get_teams(id:list, 
              session = session):
    teams = []
    with session() as session:
        if isinstance(id, list):
            for item in id:
                try:
                    stmt = select(Player_1.team).where(Player_1.player_id == int(item))
                    #stmt = text(f"""SELECT team FROM EPL_PLAYERS_2023_1ST_HALF where player_id = {id} """ )
                    obj = session.scalars(stmt).all()
                    teams.append(obj[0])
                except IndexError:
                    stmt = select(Player_2.team).where(Player_2.player_id == int(item))
                    obj = session.scalars(stmt).all()
                    teams.append(obj[0])
        else:
            statement = select(distinct(Player_1.team))
            obj = session.scalars(statement).all()
            return obj[0]
    return teams

    
def get_position(id:list, session = session):
    out = []
    with session() as session:
        if isinstance(id, list):
            for item in id:

                try:
                    stmt = select(Player_1.position).where(Player_1.player_id == int(item))
                    obj = session.scalars(stmt).all()

                    out.append(obj[0])
                except IndexError:
                    stmt = select(Player_2.position).where(Player_2.player_id == int(item))
                    obj = session.scalars(stmt).all()

                    out.append(obj[0])
        else:
            statement = select(distinct(Player_1.position))
            obj = session.execute(statement).all()
            return obj[0]
    return out

def get_entry_ids(session = sessionmaker(create_connection_engine('fpl')), table_name = ''):
    with session() as session:
        
        statement_1 = text(f"""SELECT id FROM {table_name} ORDER BY id""" )
        statement_2 = text(f"""SELECT count(id) FROM {table_name}""" )
        obj = session.execute(statement_1).all()
        obj_2 = session.execute(statement_2).one()
        return (i.id for i in obj), obj_2[0]
    
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
   pass
