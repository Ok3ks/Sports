from multiprocessing import Pool
from src.utils import get_participant_entry

from pymysql import Error
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from src.db.db import create_connection_engine,get_entry_ids


def create_gameweek_entries_table(conn = '', table_name = ''):
    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql=text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            auto_sub_in VARCHAR(200),
                            auto_sub_out VARCHAR(200),
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
    import gevent
    import time

    from itertools import islice
    import pandas as pd

    parser = argparse.ArgumentParser(prog="Writing ALL participant entries into DB")
    parser.add_argument('-g', '--gameweek_id', type= int, help= "Gameweek entry")
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-s','--start', type= int, help="start counter", required=True, default= 0)
    parser.add_argument('-e', '--end', type=int, help="end counter", required=True)

    args = parser.parse_args()
    engine = create_connection_engine(args.db_name)

    #list of entry_ids is ordered in descending order, assuming ids are monotonically increasing
    list_of_entry_ids,LENGTH = get_entry_ids(table_name=f"`314`")
    last_element = next(list_of_entry_ids)
    print(LENGTH) 

    TABLE_NAME = f"Entries_Gameweek_{args.gameweek_id}"
    create_gameweek_entries_table(conn =engine, table_name= TABLE_NAME)
    start_time= time.time()

    for n in range(args.start,args.end,100):
        #optimum number of spawned threads to 100
        req = [gevent.spawn(get_participant_entry, gw=args.gameweek_id, entry_id = i) for i in range(n, n+100, 1)]
        res = [response.value for response in gevent.iwait(req)]
        #chaining tuples obtained from spawned processes
        try:
            df = pd.DataFrame(res)
        except AttributeError:
            time.sleep(30)
            req = [gevent.spawn(get_participant_entry, gw=args.gameweek_id, entry_id = i) for i in range(n, n+100, 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
        finally:
            print(df)
            df.to_sql(TABLE_NAME, engine, if_exists='append',method='multi', index = False)
            print("cycle {} complete".format(n+100))

        if n%10_000 == 0:
            time.sleep(5)

    end_time = time.time()
    print(end_time - start_time)

    

    

    