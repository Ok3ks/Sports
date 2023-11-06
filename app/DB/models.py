from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

from sqlite3 import Error
import sqlite3

from dataclasses import dataclass

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

@dataclass
class PlayerSeasonHistory(db.Model):
    #"""Gameweek data of individual players"""
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    event: Mapped[int] = mapped_column(Integer)
    minutes: Mapped[int] = mapped_column(Integer)
    goal_scored: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)

    clean_sheets: Mapped[int] = mapped_column(Integer)
    goals_conceded: Mapped[int] = mapped_column(Integer)
    own_goals: Mapped[int] = mapped_column(Integer)
    penalties_saved: Mapped[int] = mapped_column(Integer)
    penalties_missed: Mapped[int] = mapped_column(Integer)
    
    red_cards: Mapped[int] = mapped_column(Integer)
    bonus: Mapped[int] = mapped_column(Integer)
    bps: Mapped[int] = mapped_column(Integer)
    influence: Mapped[int] = mapped_column(Integer)
    creativity: Mapped[int] = mapped_column(Integer)
    
    threat: Mapped[int] = mapped_column(Integer)
    ict_index: Mapped[int] = mapped_column(Integer)
    starts: Mapped[int] = mapped_column(Integer)
    expected_goals: Mapped[int] = mapped_column(Integer)
    
    expected_assists: Mapped[int] = mapped_column(Integer)
    expected_goal_involvements: Mapped[int] = mapped_column(Integer)
    expected_goals_conceded: Mapped[int] = mapped_column(Integer)
    total_points: Mapped[int] = mapped_column(Integer)
    in_dreamteam: Mapped[int] = mapped_column(Integer)


@dataclass
class Participants(db.Model):
    entry_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    team_name: Mapped[str] = mapped_column(String, unique=True)
    player_name: Mapped[str] = mapped_column(String)
    gw_total = Mapped[int] = mapped_column(Integer)

#@dataclass
#class EplPlayers(db.Model):
    #entry_name: Mapped[str]= entry_name
                          
#class Team(db.Model):
    #making analytics by soccer teams
    #may require fixtures too

#@dataclass
#class Week(db.Model):
    #""" Extract entries per week and store mainly referenced
    #weekly attributes."""

#@dataclass
#class League(db.Model):
    #start_year: Mapped[int] = mapped_column(Integer)
    #end_year: Mapped[int] = mapped_column(Integer)
    #winner: Mapped[int] = mapped_column(Integer)
    #h2h_winner:Mapped[int] = mapped_column(Integer)

#db.session.add(obj)
#db.session.delete(obj)
#db.session.execute()