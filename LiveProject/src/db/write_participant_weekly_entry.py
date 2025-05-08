"""Multiprocessing script to write weekly entries to database"""

from src.utils import get_participant_entry
import logging
import gevent
from src.db.participant_info_table import league_participant_info
import pandas as pd
from src.utils import bucket_client

LOGGER = logging.getLogger(__name__)


def create_gameweek_entries_table(conn="", table_name=""):
    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql = text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
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




# bucket=bucket_client()

def participant_weekly_entry(entry_id: list[int] | int, to_json=False, upload=True):
    """Downloads weekly entry for a list of entry Id"""
    new_directory = f"data/participant/{args.gameweek_id}"
    if type(entry_id) is list:
        START = 0
        for n in range(0, len(entry_id), 100):
            # optimum number of spawned threads to 100
            req = [
                gevent.spawn(
                    get_participant_entry,
                    gw=args.gameweek_id,
                    entry_id=i) 
                    for i in entry_id[START:START+100]
                ]
            res = [response.value for response in gevent.iwait(req)]
            filename = f"{entry_id[0] + n}.json"
            destination_path = os.path.join(new_directory, filename)

            df = pd.DataFrame(res)
            df.set_index("entry_id", inplace=True)
            if not os.path.exists(new_directory):
                os.makedirs(new_directory)
            if to_json:
                df.to_json(destination_path)
                print(f"{filename} saved to json")

            if n % 10_000 == 0:
                time.sleep(5)
            # if upload:
                # print(bucket.exists())
                # blob = bucket.blob(f"{args.gameweek_id}/{filename}")
                # blob.upload_from_filename(destination_path)

            START += 100
            # chaining tuples obtained from spawned processes
    else:
        import json
        res = get_participant_entry(gw=args.gameweek_id, entry_id=entry_id)
        filename = f"{entry_id}.json"
        with open(filename, 'w') as outs:
            json.dump(res, outs)
    



if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-t", "--processes", type=int, help="Number of processes")
    parser.add_argument("-s", "--start", type=int)
    parser.add_argument("-e", "--end", type=int)

    args = parser.parse_args()
    import time

    # league_participant_info(args.league_id, engine)
    # list_of_entry_ids, LENGTH = get_entry_ids(
    #     table_name=f"League_{str(args.league_id)}"
    # )
    # if LENGTH > 1:
    #     create_gameweek_entries_table(conn=engine, table_name=TABLE_NAME)

    participant_weekly_entry([n for n in range(args.start, args.end)], to_json=True, upload=False)


