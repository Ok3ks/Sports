from src.db.db import create_connection_engine
import requests
from src.urls import FPL_URL
from src.utils import League

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pymysql import Error

def create_participant_table(conn = '', table_name = ''):
    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql=text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            auto_sub_in VARCHAR (200),
                            auto_sub_out VARCHAR (200),
                            gw INTEGER,
                            active_chip VARCHAR(200), 
                            points_on_bench INTEGER, 
                            total_points INTEGER, 
                            event_transfers_cost INTEGER,
                            players VARCHAR (1000),
                            bench VARCHAR (1000),
                            vice_captain INTEGER,
                            captain INTEGER, 
                            entry_id INTEGER PRIMARY KEY
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
    import pandas as pd
    from itertools import islice,chain

    import time
    import gevent
    from gevent.lock import Semaphore



    from multiprocessing import Process, Value

    parser = argparse.ArgumentParser("Update Player information, this happens twice a year")
    
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-l', '--league_id', type= int, required= True, help = "Gameweek you are trying to get a report of")
    
    args = parser.parse_args()
    connection  = create_connection_engine(args.db_name) #Add database directory as constant

    test = League(args.league_id)
    #test.get_participant_name()
    #semaphore = Semaphore(100)

    #dividing by apriori knowledge of number of pages
    for n in range(1,22_000,100):
        #optimum number of spawned threads to 100
        req = [gevent.spawn(test.get_league_participant_mp, test.league_id, i) for i in range(n,n+100,1)]
        res = [response.value for response in gevent.iwait(req)]
        count = sum(1 for _ in res)

        print(count)

        df = pd.DataFrame(chain.from_iterable(res))
        df.columns = ['id', 'participant_entry_name', 'participant_player_name']
        df.to_sql(str(test.league_id),connection, if_exists='append', chunksize=1000, method="multi")
        time.sleep(2)

        print(f"round {n} /done")

    #print("participants extracted successfully")
    #count = sum(1 for _ in test.id_participant)
    #counter = 0
        
    #for i in range(0, count, 5000):
        #counter += 1
        #df = pd.DataFrame(islice(test.id_participant, i, i+5000))

        #df.columns = ['id', 'participant_entry_name', 'participant_player_name']
        #df.to_sql(test.league_name,connection, if_exists='append', chunksize=1000, method="multi")

        #print("counter {}".format(counter))    


