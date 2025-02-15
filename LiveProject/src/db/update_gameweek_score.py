from sqlite3 import OperationalError
import sqlite3
import pandas as pd
import sqlalchemy
from src.db.db import (
    create_connection_engine,
    get_gameweek_scores,
    delete_gameweek_scores,
)

from src.db.db import GameweekScore

import requests
from src.urls import GW_URL
import logging

LOGGER = logging.getLogger(__name__)

def update_db_gameweek_score(conn, gw):
    """This function retrieves current information of players
    from the API"""

    r = requests.get(GW_URL.format(gw))
    r = r.json()
    temp = {item["id"]: item["stats"] for item in r["elements"]}
    
    df = pd.DataFrame(temp)
    df = df.T
    df["gameweek"] = gw
    df.reset_index(level=0, names="player_id", inplace=True)

    # Write first, so we're assured table is always created
    df.to_sql("Player_gameweek_score", conn, if_exists="append", method="multi")

    if get_gameweek_scores(gw) > 0:
        print(delete_gameweek_scores(gw, table_name=GameweekScore.__tablename__))
        df.to_sql("Player_gameweek_score", conn, if_exists="append", method="multi")
        LOGGER.info("Data insert successful")
    else:
        # Combining all gameweeks into one database table,
        df.to_sql("Player_gameweek_score", conn, if_exists="append", method="multi")
        LOGGER.info("Data insert successful")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="update_gameweek_score", description="Provide Gameweek ID and League ID"
    )

    parser.add_argument(
        "-g",
        "--gameweek_id",
        type=int,
        help="Gameweek you are trying to get a report of",
    )
    args = parser.parse_args()
    connection = create_connection_engine()  # Add database directory as constant

    try:
        update_db_gameweek_score(connection, args.gameweek_id)
    except ValueError:
        LOGGER.info("Gameweek is unavailable")
