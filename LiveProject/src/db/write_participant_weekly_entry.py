"""Multiprocessing script to write weekly entries to database"""

from src.utils import get_participant_entry
from pymysql import Error
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.db.db import create_connection_engine
import logging
import gevent
from src.db.participant_info_table import league_participant_info
import pandas as pd


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


def participant_weekly_entry(entry_id: list[int] | int, to_json=False):
    """Downloads weekly entry for a list of entry Id"""
    new_directory = "data/participant/"
    if type(entry_id) is list:
        for n in range(0, len(entry_id), 100):
            # optimum number of spawned threads to 100
            req = [
                gevent.spawn(
                    get_participant_entry,
                    gw=args.gameweek_id,
                    entry_id=entry_id[n])
                ]
            res = [response.value for response in gevent.iwait(req)]
            filename = f"{entry_id[n]}.json"
            if not os.path.exists(new_directory):
                os.makedirs(new_directory)
            df = pd.DataFrame(res)
            df.to_json(os.path.join(new_directory, filename))
            print(f"done {filename}")

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
    parser.add_argument("-p", "--participant_id")

    args = parser.parse_args()
    # TABLE_NAME = f"Entries_League_{args.participant_id}_Gameweek_{args.gameweek_id}"
    # engine = create_connection_engine()
    participant_weekly_entry(args.participant_id, args.gameweek_id)
    
