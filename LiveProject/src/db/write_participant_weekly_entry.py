"""Multiprocessing script to write weekly entries to database"""

from src.utils import get_participant_entry
from pymysql import Error
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.db.db import create_connection_engine, get_entry_ids
import logging

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


if __name__ == "__main__":
    import argparse
    import gevent
    import time
    from src.db.participant_info_table import league_participant_info
    from itertools import islice
    import pandas as pd

    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-t", "--processes", type=int, help="Number of processes")
    parser.add_argument("-l", "--league_id", type=int)

    args = parser.parse_args()
    TABLE_NAME = f"Entries_League_{args.league_id}_Gameweek_{args.gameweek_id}"
    engine = create_connection_engine()

    league_participant_info(args.league_id, engine)
    list_of_entry_ids, LENGTH = get_entry_ids(
        table_name=f"League_{str(args.league_id)}"
    )
    if LENGTH > 1:
        create_gameweek_entries_table(conn=engine, table_name=TABLE_NAME)

    for n in range(0, LENGTH, 100):
        # optimum number of spawned threads to 100
        req = [
            gevent.spawn(get_participant_entry, gw=args.gameweek_id, entry_id=i)
            for i in islice(list_of_entry_ids, n, n + 100, 1)
        ]
        res = [response.value for response in gevent.iwait(req)]
        # chaining tuples obtained from spawned processes
        df = pd.DataFrame(res)
        df.to_sql(TABLE_NAME, engine, if_exists="append", method="multi", index=False)
        LOGGER.info("cycle {} complete".format(n))

        if n % 10_000 == 0:
            time.sleep(5)
