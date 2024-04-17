from src.utils import get_gw_transfers_mt
from src.db.db import create_connection_engine,get_entry_ids

import pandas as pd

def create_transfer_entries(conn, table_name=''):
    pass

if __name__ == "__main__":

    import argparse
    import gevent
    import time

    parser = argparse.ArgumentParser(prog="Writing ALL participant entries into DB")
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-s','--start', type= int, help="start counter", required=True, default= 0)
    parser.add_argument('-e', '--end', type=int, help="end counter", required=True)

    args = parser.parse_args()

    # TABLE_NAME = "Transfers"
    # engine = create_connection_engine(args.db_name)
    # create_transfer_entries(conn =engine, table_name= TABLE_NAME)
    
    #list of entry_ids is ordered in descending order, assuming ids are monotonically increasing
    # list_of_entry_ids,LENGTH = get_entry_ids(table_name="`314`")
    # last_element = next(list_of_entry_ids)
    start_time= time.time()
    from src.paths import MOCK_DIR
    from os.path import join
    import os


    for n in range(args.start,args.end, 100):
        #optimum number of spawned threads to 100
        cycle = args.start //100
        try:
            req = [gevent.spawn(get_gw_transfers_mt, gw=8, all = True,entry_id = i) for i in range(n, min(args.end, n+100), 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
            print(df)
            
        except AttributeError:
            time.sleep(10)
            req = [gevent.spawn(get_gw_transfers_mt, gw=8, all = True,entry_id = i) for i in range(n, min(args.end, n+100), 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
        finally:
            columns = df.columns
            os.makedirs(join(MOCK_DIR, 'transfers', str(columns[0])), exist_ok=True)
            df.to_json(path_or_buf=join(MOCK_DIR, 'transfers', str(columns[0]), f"transfers_{cycle+1}_.json"))
    end_time = time.time()
print(end_time-start_time)