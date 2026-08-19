from anyio import to_thread
import anyio
from src.db.db import create_connection_engine
from src.utils import async_client
from src.urls import FPL_URL
import pandas as pd
import sqlalchemy


async def update_db_player_info(engine, table_name, half=1):
    """This function retrieves current information of players
    from the API"""

    home = await async_client.get(FPL_URL)
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
    data.columns = [
        "player_id",
        "team_code",
        "team",
        "team_id",
        "position",
        "player_name",
        "half",
    ]

    print(f"{len(data)} is ready to be added to database table")
    await to_thread.run_sync(_save, data, engine, table_name)
    print(f"success adding {len(data)}")


def _save(df: pd.DataFrame, engine: sqlalchemy.Engine, table_name: str):
    return df.to_sql(
        table_name, con=engine, if_exists="append", method="multi", index=True
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        "Update Player information, this happens twice a year"
    )

    parser.add_argument(
        "-t",
        "--table_name",
        type=str,
        help="Table name",
        default="EPL_2025_PLAYER_INFO",
    )
    parser.add_argument(
        "-db", "--db_name", type=str, help="Database name", default="fpl"
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

    anyio.run(update_db_player_info, engine, args.table_name, args.half, backend="trio")
