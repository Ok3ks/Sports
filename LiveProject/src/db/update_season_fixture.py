"https://fantasy.premierleague.com/api/fixtures/"

from src.db.db import create_connection_engine
import requests
from src.urls import FIXTURE_URL

from sqlalchemy import Integer, Boolean, String

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
import pandas as pd


class Base(DeclarativeBase):
    pass


class Fixture(Base):
    __tablename__ = "2024_2025_FIXTURES"

    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    gameweek: Mapped[int] = mapped_column(Integer)
    finished: Mapped[bool] = mapped_column(Boolean)
    home: Mapped[str] = mapped_column(String)
    away: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String)
    homegoals: Mapped[str] = mapped_column(String)
    awaygoals: Mapped[str] = mapped_column(String)
    homedifficulty: Mapped[str] = mapped_column(String)
    awaydifficulty: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"""{self.home} {self.homegoals} vs {self.awaygoals} 
            {self.away}. Date {self.date}"""


def update_season_fixture(engine=None, table_name="2024_2025_FIXTURES"):
    """This function retrieves current information of players
    from the API"""

    fix = requests.get(FIXTURE_URL)
    fix = fix.json()
    fixture_df = pd.DataFrame(fix)

    fixture_df = fixture_df.rename(
        {
            "event": "gameweek",
            "team_h_difficulty": "homedifficulty",
            "team_a_difficulty": "awaydifficulty",
            "team_h": "home",
            "team_a": "away",
            "team_h_score": "homegoals",
            "team_a_score": "awaygoals",
            "kickoff_time": "date",
        },
        axis=1,
    )
    # pd.set_option()
    fixture_df = fixture_df[
        [
            "homedifficulty",
            "awaydifficulty",
            "home",
            "away",
            "homegoals",
            "awaygoals",
            "code",
            "gameweek",
            "finished",
            "date",
        ]
    ]

    if engine:
        fixture_df.to_sql(
            table_name, con=engine, if_exists="replace", chunksize=100, index=False
        )
        print(fixture_df.head())
    else:
        return fixture_df


if __name__ == "__main__":
    update_season_fixture(engine=create_connection_engine())
