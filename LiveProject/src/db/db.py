# from utils import Gameweek, Player, League
import sqlite3
from types import NoneType

from sqlite3 import Error  # type: ignore
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
    select,
    text,
    distinct,
    delete,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import URL
import os
import math
# from update_gameweek_score import PlayerGameweekScores #decide which to remove on refactor


class Base(DeclarativeBase):
    pass


class PlayerInfo(Base):
    __tablename__ = "EPL_2024_PLAYER_INFO"

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_code: Mapped[int] = mapped_column(Integer)
    team: Mapped[str] = mapped_column(String)
    team_code: Mapped[int] = mapped_column(Integer)
    team_id: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String)
    player_name: Mapped[str] = mapped_column(String)
    half: Mapped[str] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Player(player_id={self.player_id}, team={self.team}, position={self.position}, player_name={self.player_name}, half={self.half})"


class GameweekScore(Base):
    __tablename__ = "Player_gameweek_score"

    index: Mapped[int] = mapped_column(Integer)
    player_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )  # there should be a foreign key here
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
    influence: Mapped[int] = mapped_column(Integer)
    creativity: Mapped[int] = mapped_column(Integer)
    threat: Mapped[int] = mapped_column(Integer)
    ict_index: Mapped[int] = mapped_column(Integer)
    starts: Mapped[int] = mapped_column(Integer)
    expected_goals: Mapped[String] = mapped_column(String)
    expected_assists: Mapped[String] = mapped_column(String)
    expected_goal_involvements: Mapped[String] = mapped_column(String)
    expected_goals_conceded: Mapped[String] = mapped_column(String)
    mng_win: Mapped[int] = mapped_column(Integer)
    mng_draw: Mapped[int] = mapped_column(Integer)
    mng_loss: Mapped[int] = mapped_column(Integer)
    mng_underdog_win: Mapped[int] = mapped_column(Integer)
    mng_underdog_draw: Mapped[int] = mapped_column(Integer)
    mng_clean_sheets: Mapped[int] = mapped_column(Integer)
    mng_goals_scored: Mapped[int] = mapped_column(Integer)
    total_points: Mapped[int] = mapped_column(Integer)
    in_dreamteam: Mapped[int] = mapped_column(Integer)
    gameweek: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"GameweekScore(player_id={self.player_id}, goals_scored={self.goals_scored}, total_points={self.total_points}, gameweek={self.gameweek}, dreamteam={self.in_dreamteam})"


class Fixtures(Base):
    __tablename__ = "2024_2025_FIXTURES"

    homedifficulty: Mapped[int] = mapped_column(Integer)
    awaydifficulty: Mapped[int] = mapped_column(Integer)
    home: Mapped[int] = mapped_column(Integer)
    away: Mapped[int] = mapped_column(Integer)
    homegoals: Mapped[int] = mapped_column(Integer)
    awaygoals: Mapped[int] = mapped_column(Integer)
    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    gameweek: Mapped[int] = mapped_column(Integer)
    finished: Mapped[bool] = mapped_column(Boolean)
    date: Mapped[String] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"""
                Fixture({team_short_name_mapping[self.home]} {int(self.homegoals)} : {team_short_name_mapping[self.away]} {int(self.awaygoals)} 
                        Code: {self.code},"""


team_short_name_mapping = {
    1: "ARS",
    2: "AVL",
    3: "BOU",
    4: "BRE",
    5: "BHA",
    6: "CHE",
    7: "CRY",
    8: "EVE",
    9: "FUL",
    10: "IPS",
    11: "LEI",
    12: "LIV",
    13: "MCI",
    14: "MUN",
    15: "NEW",
    16: "NFO",
    17: "SOU",
    18: "TOT",
    19: "WHU",
    20: "WOL",
}


team_name_to_code = {
    "Arsenal": 1,
    "Aston Villa": 2,
    "Bournemouth": 3,
    "Brentford": 4,
    "Brighton": 5,
    "Chelsea": 6,
    "Crystal Palace": 7,
    "Everton": 8,
    "Fulham": 9,
    "Ipswich": 10,
    "Leicester": 11,
    "Liverpool": 12,
    "Man City": 13,
    "Man Utd": 14,
    "Newcastle": 15,
    "Nott'm Forest": 16,
    "Southampton": 17,
    "Spurs": 18,
    "West Ham": 19,
    "Wolves": 20,
}


def create_connection(db, db_type="sqlite"):
    """
        Create Direct Database connection using
        either postgresql, mysql or sqlite
    """
    conn = None

    if db_type == "sqlite":
        try:
            conn = sqlite3.connect(
                os.getenv("DB_PATH"),
                check_same_thread=True,
                timeout=10,
                uri=True)
            return conn
        except Error as e:
            print(e)
        return conn

    if db_type == "postgres":
        try:
            conn = None
            return conn
        except Error as e:
            print(e)
        return conn
    else:
        try:
            conn = None
            return conn
        except Error as e:
            print(e)
        return conn


def create_connection_engine(db="sqlite3"):
    """Creates a SQLAlchemy engine with a database"""

    if db == "sqlite3":
        return create_engine('sqlite:///db.sqlite3', pool_recycle=3600, echo=True)

    else:
        url_object = URL.create(
            drivername=os.getenv("DB_DRIVER_NAME"),
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
        )

        return create_engine(url_object, pool_pre_ping=True)


# def create_cache_engine():
#     """Ensure Redis Instance is running, either docker image or cloud"""

#     return redis.Redis(
#                 host=os.getenv("REDISHOST"),
#                 port=os.getenv("REDISPORT"),
#                 password=os.getenv("REDISPASSWORD"),
#                 db=0).from_pool(
#                     redis.connection.ConnectionPool.from_url(
#                         f"redis://{os.getenv("REDISHOST")}:{os.getenv("REDISPORT")}/0"
#                         ))


session = sessionmaker(create_connection_engine())


def get_player_gql(id, gameweek, session=session):
    half = 1 if gameweek < 19 else 2
    with session() as session:
        try:
            id = int(id)
        except Exception:
            pass
        finally:
            stmt = (
                select(PlayerInfo)
                .where(PlayerInfo.player_id == id)
                .where(PlayerInfo.half == int(half))
            )
            player_info = session.scalars(stmt).all()[0].__dict__
            player_info.pop("_sa_instance_state")

        stmt = select(GameweekScore).where(
            (GameweekScore.player_id == id) & (GameweekScore.gameweek == gameweek)
        )

        # Add fixture later
        gameweek_score = session.scalars(stmt).one().__dict__
        gameweek_score.pop("_sa_instance_state")

        return {"player_id": id, "info": player_info, "gameweek_score": gameweek_score}


def get_player(id, session=session):
    out = []
    with session() as session:
        if isinstance(id, list):
            for item in id:
                stmt = select(PlayerInfo.player_name).where(
                    PlayerInfo.player_id == int(item)
                )
                obj = session.scalars(stmt).all()
                out.append(obj[0])
            return out
        else:
            stmt = select(PlayerInfo.player_name).where(PlayerInfo.player_id == int(id))
            obj = session.scalars(stmt).one()
            return obj


def get_teams(session=session):
    with session() as session:
        statement = select(distinct(PlayerInfo.team))
        obj = session.execute(statement).all()
        return obj


def get_teams_id(session=session) -> dict:
    """Return a mapping of team id to teams"""
    with session() as session:
        statement_1 = text('SELECT team_id,team FROM EPL_2024_PLAYER_INFO')
        obj = session.execute(statement_1).all()
        obj = {i[0]: i[1] for i in obj}
        return obj


def get_player_team_map(session=session) -> dict:
    """Return a mapping of Player id to teams"""
    with session() as session:
        statement_1 = text('SELECT player_id, team FROM EPL_2024_PLAYER_INFO')
        obj = session.execute(statement_1).all()
        obj = {i[0]: i[1] for i in obj}
        return obj


def get_player_position_map(session=session) -> dict:
    """Return a mapping of Player id to teams"""
    with session() as session:
        statement_1 = text(
            'SELECT player_id, position FROM "EPL_2024_PLAYER_INFO"'
        )
        obj = session.execute(statement_1).all()
        obj = {i[0]: i[1] for i in obj}
        return obj


# r
# raw sql queries make it hard to switch databases
# tests are good


def get_entry_ids(session=sessionmaker(create_connection_engine()), table_name=""):
    with session() as session:
        statement_1 = text(f"""SELECT id FROM {table_name}""")
        statement_2 = text(f"""SELECT count(id) FROM {table_name}""")
        obj = session.execute(statement_1).all()
        obj_2 = session.execute(statement_2).one()
        return (i.id for i in obj), obj_2[0]


# ORM for each gameweek
def get_player_stats_from_db_gql(id, gw, session=session):
    with session() as session:
        stmt = select(GameweekScore).where(
            (GameweekScore.player_id == id) & (GameweekScore.gameweek == gw)
        )
        c = session.scalars(stmt).one()
        return c


def get_player_stats_from_db(gw, session=session):
    stmt = text(
        f'SELECT player_id, total_points FROM Player_gameweek_score WHERE gameweek = {gw}'
    )
    # stmt = select(PlayerGameweekScores.total_points).where((PlayerGameweekScores.player_id == id)&(PlayerGameweekScores.gameweek == gw))
    with session() as session:
        c = session.execute(stmt).all()
        # c = session.scalars(stmt).all()
    return {i.player_id: i.total_points for i in c}


def get_ind_player_stats_from_db(id, gw, session=session):
    if (id and gw):
        stmt = text(
            f'SELECT total_points FROM Player_gameweek_score WHERE gameweek = {gw} and player_id = {id}'
        )
        with session() as session:
            c = session.execute(stmt).one()
        if isinstance(c[0], int):
            return c[0]
        else:
            pass


def get_gameweek_stats(gw, session=session):
    """Return all stats for a particular gameweek."""
    stmt = text(f'SELECT * FROM Player_gameweek_score WHERE gameweek = {gw}')
    with session() as session:
        c = session.execute(stmt).all()
    return c


def get_season_stats(session=session):
    """Return all season stats"""
    stmt = text(
        f'SELECT * FROM Player_gameweek_score ORDER BY GAMEWEEK DESC '
    )
    with session() as session:
        c = session.execute(stmt).all()
    return c


def get_fixtures(session=session):
    """Return all fixtures."""
    stmt = text(f'SELECT  * FROM 2024_2025_FIXTURES')
    with session() as session:
        c = session.execute(stmt).all()
    return c


def check_minutes(id, gw, session=session):
    """Checks DB for captain's minutes"""

    if not math.isnan(id):
        stmt = text(
            f'SELECT minutes FROM Player_gameweek_score WHERE player_id={id} and gameweek = {gw}'
        )
        with session() as session:
            c = session.execute(stmt)
        return c.fetchone()
    else:
        return [0]


## Gameweek


def get_available_gameweek_scores(
    session=sessionmaker(create_connection_engine()),
):
    # can be refactored to get_distinct of any column
    stmt = text('SELECT distinct(gameweek) FROM Player_gameweek_score')
    with session() as session:
        c = session.execute(stmt)
    return c.fetchall()


def get_gameweek_scores(gameweek: int, session=session):
    #Causes an issue, if database table has not been created from start
    with session() as session:
        stmt = (
            select(func.count("*"))
            .select_from(GameweekScore)
            .where(GameweekScore.gameweek == gameweek)
        )
        obj = session.scalars(stmt).one()
        return obj

def delete_gameweek_scores(gameweek: int, session=session, table_name=""):
    with session() as session:
        stmt = text(f'DELETE FROM {table_name} where gameweek = {gameweek}')
        session.execute(stmt)
        session.commit()


# raw sql queries make it hard to switch databases
# tests are good

# Leagues


def get_entry_ids(session=sessionmaker(create_connection_engine()), table_name=""):
    with session() as session:
        statement_1 = text(f'SELECT id FROM {table_name}')
        statement_2 = text(f'SELECT count(id) FROM {table_name}')
        obj = session.execute(statement_1).all()
        obj_2 = session.execute(statement_2).one()
        return (i.id for i in obj), obj_2[0]


# Teams
def get_teams(session=sessionmaker(create_connection_engine())):
    with session() as session:
        statement = select(distinct(PlayerInfo.team))
        obj = session.execute(statement).all()
        return obj


def get_player_info(player_id, half, session=sessionmaker(create_connection_engine())):
    with session() as session:
        statement = (
            select(PlayerInfo)
            .where(PlayerInfo.player_id == player_id)
            .where(PlayerInfo.half == half)
        )
        obj = session.execute(statement).one()
        return obj


def get_player_team_code(
    player_id, half, session=sessionmaker(create_connection_engine())
):
    with session() as session:
        statement = (
            select(PlayerInfo.team_code)
            .where(PlayerInfo.player_id == player_id)
            .where(PlayerInfo.half == half)
        )
        obj = session.execute(statement).one()
        return obj


def create_id_table(conn, table_name="league_name"):
    """Creates a table with columns, player_id, position, team, and player_name"""
    try:
        create_table_sql = text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            player_id INTEGER PRIMARY KEY,
                            participant_entry_name VARCHAR (2000),
                            participant_player_name VARCHAR (200)
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
    pass
