import pandas as pd
from src.db.db import create_connection_engine

from sqlalchemy import Integer, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

import requests
from src.urls import GW_URL


class Base(DeclarativeBase):
    pass


class PlayerGameweekScores(Base):
    __tablename__ = "Player_Gameweek_scores"

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    minutes: Mapped[int] = mapped_column(Integer)
    goals_scored: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    clean_sheets: Mapped[int] = mapped_column(Integer)
    goals_conceded: Mapped[int] = mapped_column(Integer)
    own_goals: Mapped[int] = mapped_column(Integer)
    penalties_saved: Mapped[int] = mapped_column(Integer)
    penalties_missed: Mapped[int] = mapped_column(Integer)
    yellow_cards: Mapped[int] = mapped_column(Integer)
    red_cards: Mapped[int] = mapped_column(Integer)
    saves: Mapped[int] = mapped_column(Integer)
    bonus: Mapped[int] = mapped_column(Integer)
    bps: Mapped[int] = mapped_column(Integer)
    influence: Mapped[float] = mapped_column(Float)
    creativity: Mapped[float] = mapped_column(Float)
    threat: Mapped[float] = mapped_column(Float)
    ict_index: Mapped[float] = mapped_column(Float)
    starts: Mapped[float] = mapped_column(Float)
    expected_goals: Mapped[float] = mapped_column(Float)
    expected_assists: Mapped[float] = mapped_column(Float)
    expected_goal_involvements: Mapped[float] = mapped_column(Float)
    expected_goals_conceded: Mapped[float] = mapped_column(Float)
    total_points: Mapped[int] = mapped_column(Integer)
    in_dreamteam: Mapped[bool] = mapped_column(Boolean)
    gameweek: Mapped[int] = mapped_column(Integer)


def update_db_gameweek_score(conn, gw):
    """This function retrieves current information of players
    from the API"""

    r = requests.get(GW_URL.format(gw))
    r = r.json()

    temp = {item["id"]: item["stats"] for item in r["elements"]}
    df = pd.DataFrame(temp)
    df = df.T
    df["gameweek"] = gw
    df.columns = [
        "minutes",
        "goals_scored",
        "assists",
        "clean_sheets",
        "goals_conceded",
        "own_goals",
        "penalties_saved",
        "penalties_missed",
        "yellow_cards",
        "red_cards",
        "saves",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "starts",
        "expected_goals",
        "expected_assists",
        "expected_goal_involvements",
        "expected_goals_conceded",
        "total_points",
        "in_dreamteam",
        "gameweek",
    ]

    df.reset_index(level=0, names="player_id", inplace=True)
    ##Combining all gameweeks into one database, which is why I am appending files
    df.to_sql(f"Player_gameweek_score", conn, if_exists="append", method="multi")
    print("Data insert successful")


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
        print("Gameweek is unavailable")
