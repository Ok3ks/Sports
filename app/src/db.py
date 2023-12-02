#from utils import Gameweek, Player, League
import pandas as pd
import sqlite3
from sqlite3 import Error, OperationalError

from os.path import realpath,join
from app.src.paths import APP_DIR

from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase

import requests
from app.src.urls import FPL_URL

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection has been created successfully")
        return conn
    except Error as e:
        print(e)
    return conn

pat = realpath(join(APP_DIR, 'fpl'))
print(pat)
engine = create_engine(f"sqlite:///{pat}/")
print(engine)
session = Session(engine)

conn = create_connection(realpath(join(APP_DIR,"fpl")))

def get_player(id, session = session):
    out = []
    if isinstance(id, list):
        for item in id:
            stmt = select(Player).where(Player.player_id == int(item))
            obj = session.scalars(stmt).one()
            print(obj)
            out.append(obj.player_name)
    else:
        stmt = select(Player).where(Player.player_id == int(id))
        out = session.scalars(stmt).one()
        out = out.player_name
        #print(obj.player_name)
    return out

def get_player_stats_from_db(id, gw,conn):
    #GameweekSc
    query = f"SELECT * FROM Gameweek_{gw} WHERE player_id = {id}"
    c = conn.cursor()
    c.execute(query)
    print(c.fetchall())

#clean up

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

#Add functions to classes


def create_table(conn):
    try:
        create_table_sql="""CREATE TABLE IF NOT EXISTS EPL_PLAYERS_2023_1ST_HALF (
                            player_id INTEGER PRIMARY KEY,
                            position VARCHAR (2000),
                            team VARCHAR (255),
                            player_name VARCHAR (200)
                        );
                        """
        #this created tables with column names 0,1,2. had to use ALTER TABLE
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    return conn

def rename_columns(conn, mapping:dict):
    mapping = [(str(key),value,) for key,value in mapping.items()]
    c = conn.cursor()
    print(mapping)
    for item in mapping:
        rename_table_sql = f"ALTER TABLE EPL_PLAYERS_2023_1ST_HALF RENAME COLUMN '{item[0]}' TO '{item[1]}'"
        c.execute(rename_table_sql)

def dummy_insert(conn):
    data = [("Salah", "Midfield", "Liverpool" "2")]
    data = pd.DataFrame(data)
    insert(conn)

def insert(conn, data):
    try:
        #assert columns in data - conftest 
        data.to_sql("EPL_PLAYERS_2023_1ST_HALF",conn,if_exists='replace',index=False)
        conn.commit()
        print("Data Insert Successful")
    except Error as e:
        print(e)
    else:
        print("Pass a dataframe as data")

def insert_from_json(conn, path):
    file = pd.read_json(path)
    insert(conn, data = file)
    #assert entry in database has included
    #by the number of values in the list

def update_db_player_info(conn):
    """This function retrieves current information of players
    from the API"""
    
    home = requests.get(FPL_URL)
    home = home.json()

    team_code_to_name = {item['code']: item['name'] for item in home['teams']}
    pos_code_to_pos = {item['id'] : item['singular_name'] for item in home['element_types']}

    data = [(item['id'], team_code_to_name[item['team_code']], pos_code_to_pos[item['element_type']], item['first_name'] + " " + item['second_name'],) for item in home['elements']]
    data.columns = ['player_id','team', 'position', 'player_name']
    data = pd.DataFrame(data)


    insert(conn, data)
    print(f"{len(data)} has been added to the SQLite table")


if __name__ == "__main__":
    #pass -db filepath into argparts
    connection = create_connection(realpath(join(APP_DIR,"fpl"))) #Add database directory as constant
    create_table(connection)
    update_db_player_info(connection)
    try:
        rename_columns(connection, {"0": "player_id", "1":'team', "2": "position", "3": "player_name"})
    except OperationalError:
        pass
