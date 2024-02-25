from src.db.db import create_connection_engine
import requests
from src.urls import FPL_URL

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pymysql import Error

from sqlalchemy import Integer, String, create_engine, select,text,distinct
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase,sessionmaker

import pandas as pd

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
    
def create_table(conn, table_name = "EPL_PLAYERS_2023_1ST_HALF"):

    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql=text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            player_id INTEGER PRIMARY KEY,
                            team VARCHAR (255),
                            position VARCHAR (2000),
                            player_name VARCHAR (200)
                        );
                        """)
        session = sessionmaker(conn)
        with session() as session:
            session.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    return conn


def update_db_player_info(engine, table_name = "EPL_PLAYERS_2023_1ST_HALF"):
    """This function retrieves current information of players
    from the API"""
    
    home = requests.get(FPL_URL)
    home = home.json()

    team_code_to_name = {item['code']: item['name'] for item in home['teams']}
    pos_code_to_pos = {item['id'] : item['singular_name'] for item in home['element_types']}

    data = ((item['id'], team_code_to_name[item['team_code']], pos_code_to_pos[item['element_type']], item['first_name'] + " " + item['second_name'],) for item in home['elements'])
    data = pd.DataFrame(data)
    data.columns = ['player_id','team', 'position', 'player_name']
    
    print(f"{len(data)} is ready to be added to database table")
    data.to_sql(f"{table_name}",engine, if_exists= 'replace', method='multi', index=False)
    print(f"success adding data")

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser("Update Player information, this happens twice a year")
    
    parser.add_argument('-t',"--table_name", type=str, help= "Table name", required=False)
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    
    args = parser.parse_args()
    engine = create_connection_engine(args.db_name) 
    
    if args.table_name:
        create_table(engine, table_name=args.table_name)
        update_db_player_info(engine, table_name=args.table_name)
    else:
        create_table(engine)
        update_db_player_info(engine)