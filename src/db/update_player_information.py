from src.db.db import create_connection_engine
import requests
from src.urls import FPL_URL

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pymysql import Error

from sqlalchemy import Integer, String

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

import pandas as pd


def update_db_player_info(engine, table_name="EPL_2024_PLAYER_INFO", half=1):
    """This function retrieves current information of players
    from the API"""

    home = requests.get(FPL_URL)
    home = home.json()

    team_code_to_name = {item["code"]: item["name"] for item in home["teams"]}
    pos_code_to_pos = {
        item["id"]: item["singular_name"] for item in home["element_types"]
    }

    team_code_to_id = {item["code"]: item["id"] for item in home["teams"]}

    data = (
        (
            item["id"],
            item["team_code"],
            team_code_to_name[item["team_code"]],
            team_code_to_id[item["team_code"]],
            pos_code_to_pos[item["element_type"]],
            item["first_name"] + " " + item["second_name"],
        )
        for item in home["elements"]
    )
    data = pd.DataFrame(data)
    data["half"] = half
    data.columns = ["player_id", "team_code",  "team", "team_id", "position", "player_name", "half"]

    print(f"{len(data)} is ready to be added to database table")
    data.to_sql(
        f"{table_name}", engine, if_exists="replace", method="multi", index=True
    )
    print(f"success adding {len(data)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Update Player information, this happens twice a year"
    )

    parser.add_argument(
        "-t", "--table_name", type=str, help="Table name", required=False
    )
    parser.add_argument(
        "-db", "--db_name", type=str, help="Database name", required=True
    )
    parser.add_argument(
        "-ha",
        "--half",
        type=int,
        choices=[1, 2],
        help="Half of the season",
        required=True,
    )

    args = parser.parse_args()
    engine = create_connection_engine()

    if args.table_name:
        update_db_player_info(engine, table_name=args.table_name, half=args.half)
    else:
        update_db_player_info(engine)
