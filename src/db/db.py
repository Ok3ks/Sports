# from utils import Gameweek, Player, League
import pymysql  # type: ignore
import psycopg2  # type: ignore
import redis

from sqlite3 import Error  # type: ignore


import redis.connection
from sqlalchemy import Integer, String, create_engine, select, text, distinct
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import URL
import os
import math
# from update_gameweek_score import PlayerGameweekScores #decide which to remove on refactor


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "EPL_2024_PLAYER_INFO"

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team: Mapped[str] = mapped_column(String)
    team_id: Mapped[str] = mapped_column(String)
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
    total_points: Mapped[String] = mapped_column(String)
    in_dreamteam: Mapped[int] = mapped_column(Integer)
    gameweek: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"GameweekScore(player_id={self.player_id}, goals_scored={self.goals_scored}, total_points={self.total_points}, gameweek={self.gameweek}, dreamteam={self.in_dreamteam})"


def create_connection(db, db_type="postgres"):
    """Use either postgresql or mysql"""
    conn = None

    if db_type == "postgres":
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_DATABASE"),
                user=os.getenv("DB_DATABASE"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            return conn
        except Error as e:
            print(e)
        return conn
    else:
        try:
            conn = pymysql.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USERNAME"),  # confirm? May lead to bug
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            return conn
        except Error as e:
            print(e)
        return conn


def create_connection_engine():
    """Creates a SQLAlchemy engine with a mysql database"""

    url_object = URL.create(
        drivername=os.getenv("DB_DRIVER_NAME"),
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE"),
    )

    return create_engine(url_object)


def create_cache_engine():
    """Ensure Redis Instance is running, either docker image or cloud"""

    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
        db=0,
    ).from_pool(redis.connection.ConnectionPool())


session = sessionmaker(create_connection_engine())


def get_player_gql(id, gameweek, session=session):
    out = []
    half = 1 if gameweek < 19 else 2
    with session() as session:
        if isinstance(id, list):
            for item in id:
                stmt = select(Player).where(Player.player_id == int(item))
                player_info = session.scalars(stmt).all()
                out.append(player_info[0])
            return out
        else:
            stmt = (
                select(Player)
                .where(Player.player_id == int(id))
                .where(Player.half == int(half))
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
                stmt = select(Player.player_name).where(Player.player_id == int(item))
                obj = session.scalars(stmt).all()
                out.append(obj[0])
            return out
        else:
            stmt = select(Player.player_name).where(Player.player_id == int(id))
            obj = session.scalars(stmt).one()
            return obj


def get_teams(session=session):
    with session() as session:
        statement = select(distinct(Player.team))
        obj = session.execute(statement).all()
        return obj
    

def get_teams_id(session=session) -> dict:
    """Return a mapping of team id to teams"""
    with session() as session:
        statement_1 = text(
            'SELECT team_id,team FROM public."EPL_2024_PLAYER_INFO"')
        obj = session.execute(statement_1) .all()
        obj = {i[0]: i[1] for i in obj}
        return obj
# raw sql queries make it hard to switch databases
# tests are good


def get_entry_ids(session=sessionmaker(create_connection_engine()), table_name=""):
    with session() as session:
        statement_1 = text(f"""SELECT id FROM public.'{table_name}'""")
        statement_2 = text(f"""SELECT count(id) FROM public.'{table_name}'""")
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
        f'SELECT player_id, total_points FROM public."Player_gameweek_score" WHERE gameweek = {gw}'
    )
    # stmt = select(PlayerGameweekScores.total_points).where((PlayerGameweekScores.player_id == id)&(PlayerGameweekScores.gameweek == gw))
    with session() as session:
        c = session.execute(stmt).all()
        # c = session.scalars(stmt).all()
    return {i.player_id: i.total_points for i in c}


def get_ind_player_stats_from_db(id, gw, session=session):
    stmt = text(
        f'SELECT total_points FROM public."Player_gameweek_score" WHERE gameweek = {gw} and player_id = {id}'
    )
    with session() as session:
        c = session.execute(stmt).one()
    return c


def get_gameweek_stats(id, gw, session=session):
    stmt = text(
        f'SELECT * FROM public."Player_gameweek_score" WHERE gameweek = {gw}'
    )
    with session() as session:
        c = session.execute(stmt).all()
    return c


def get_fixtures(session=session):
    
    stmt = text(
        f'SELECT  * FROM public."2024_2025_FIXTURES"'
    )
    with session() as session:
        c = session.execute(stmt).all()
    return c


def get_season_stats(id, gw, session=session):
    stmt = text(
        f'SELECT * FROM public."Player_gameweek_score"'
    )
    with session() as session:
        c = session.execute(stmt).all()
    return c


def check_minutes(id, gw, session=session):
    """Checks DB for captain's minutes"""

    if not math.isnan(id):
        stmt = text(
            f'SELECT minutes FROM public."Player_gameweek_score" WHERE player_id={id} and gameweek = {gw}'
        )
        with session() as session:
            c = session.execute(stmt)
        return c.fetchone()
    else:
        return [0]


def get_available_gameweek_scores(
    session=sessionmaker(create_connection_engine()),
):
    # can be refactored to get_distinct of any column
    stmt = text('SELECT distinct(gameweek) FROM public."Player_gameweek_score"')
    with session() as session:
        c = session.execute(stmt)
    return c.fetchall()


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
