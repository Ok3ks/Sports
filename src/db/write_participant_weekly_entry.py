from multiprocessing import Pool
from src.utils import get_participant_entry

from pymysql import Error
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from src.db.db import create_connection_engine,get_entry_ids


def create_participant_gameweek_table(conn = '', table_name = ''):
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

def insert(table_name, conn, rows = ()):
    try:
        create_table_sql=text(f"""INSERT INTO {table_name} 
                        {rows}; """)
        session = sessionmaker(conn)

        with session() as session:
            session.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    pass

if __name__ == "__main__":

    import argparse
    #from multiprocessing import Process,Value
    from concurrent.futures import ProcessPoolExecutor,as_completed
    import time
    from itertools import islice
    import pandas as pd

    conn = create_connection_engine('fpl')
    parser = argparse.ArgumentParser("Writing participant entries into DB")

    parser.add_argument('-g', '--gameweek_id', type= int, help= "Gameweek entry")
    parser.add_argument('-t', '--processes', type=int, help="Number of processes")
    parser.add_argument('-ta', '--table_name', default= "Overall", type =str)

    args = parser.parse_args()
    list_of_entry_ids = get_entry_ids(table_name="Nigeria")

    length = sum(1 for _ in get_entry_ids(table_name="Nigeria"))
    
    p = ProcessPoolExecutor(max_workers=4)

    create_participant_gameweek_table(conn =conn, table_name=f"Gameweek_{args.gameweek_id}")
    
    start_time= time.time()

    for start in range(0, length, 5000):
        fin = [p.submit(get_participant_entry, gw =args.gameweek_id, entry_id = i) for i in islice(list_of_entry_ids,start,start+5000)]
        df = pd.DataFrame([result.result() for result in as_completed(fin)])
        df.to_sql(f'Gameweek_{args.gameweek_id}', conn, if_exists='append',method='multi')

    end_time = time.time()
    print(end_time - start_time)

    #start_time = time.time()
    #for i in list_of_entry_ids:
        #get_participant_entry(i, args.gameweek_id)
    #end_time = time.time()
    #print(end_time - start_time)