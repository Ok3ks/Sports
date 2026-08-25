"https://fantasy.premierleague.com/api/fixtures/"

import anyio
import sqlalchemy
from src.db.db import create_connection_engine
from anyio import to_thread
from src.urls import FIXTURE_URL, FPL_URL

from sqlalchemy import Integer, Boolean, String

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
import pandas as pd
from src.utils import async_client
from src.db import SEASON


class Base(DeclarativeBase):
    pass


class Fixture(Base):
    __tablename__ = f"{SEASON}_FIXTURES"

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


async def update_season_fixture(engine=None, table_name=f"{SEASON}_FIXTURES"):
    """This function retrieves current information of players
    from the API"""

    fix = await async_client.get(FIXTURE_URL)
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
    home = await async_client.get(FPL_URL)
    home = home.json()
    team_id_to_name = {item["id"]: item["name"] for item in home["teams"]}

    fixture_df["home"] = fixture_df["home"].map(lambda x: team_id_to_name[x])
    fixture_df["away"] = fixture_df["away"].map(lambda x: team_id_to_name[x])
    if engine:
        await to_thread.run_sync(_save, fixture_df, engine, table_name)
    else:
        return fixture_df


def _save(df: pd.DataFrame, engine: sqlalchemy.Engine, table_name):
    return df.to_sql(
        table_name, con=engine, if_exists="replace", chunksize=100, index=False
    )


if __name__ == "__main__":
    anyio.run(update_season_fixture, create_connection_engine())
