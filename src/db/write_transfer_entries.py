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
    parser.add_argument('-gw','--gameweek', type= int, help= "Gameweek", required=True)
    parser.add_argument('-s','--start', type= int, help="start counter", required=True, default= 0)
    parser.add_argument('-e', '--end', type=int, help="end counter", required=True)

    args = parser.parse_args()

    #Run after gameweek 38, as it includes entries from gameweek 1 to 38
    start_time= time.time()
    from src.paths import MOCK_DIR
    from os.path import join
    import os

    for n in range(args.start,args.end, 100):
        #optimum number of spawned threads to 100
        cycle = args.start //100
        try:
            req = [gevent.spawn(get_gw_transfers_mt, gw=args.gameweek, all = True,entry_id = i) for i in range(n, min(args.end, n+100), 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
            print(df)
        except AttributeError or ConnectionResetError:
            time.sleep(10)
            req = [gevent.spawn(get_gw_transfers_mt, gw=args.gameweeks, all = True,entry_id = i) for i in range(n, min(args.end, n+100), 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
        finally:
            columns = df.columns
            os.makedirs(join(MOCK_DIR, 'transfers', str(columns[0])), exist_ok=True)
            df.to_json(path_or_buf=join(MOCK_DIR, 'transfers', f"transfers_{cycle+1}_.json"))
    end_time = time.time()
print(end_time-start_time)