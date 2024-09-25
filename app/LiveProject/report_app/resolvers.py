"""Ariadne's answer to views.py"""
# ruff: noqa: A002

from ariadne import (
    ObjectType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)

from django.contrib.auth.hashers import make_password
# from .models import (Players, Gameweek_Scores)
from src.db.db import get_player_gql, get_player_stats_from_db_gql
from src.report import LeagueWeeklyReport
from src.utils import get_curr_event
# from .shortcuts import get_object_or_none

query = QueryType()
_document = ObjectType("Document")

#For GameView
# @query.field("gameweekScore")
# def resolve_player_gameweek_scores(*_,):
#     """Retrieve a Player's gameweek score based on player_id"""
#     return Gameweek_Scores().objects.all

# Query resolvers
# @query.field("players")
# def resolve_players(*_):
#     """Retrieve all Player model instances."""
#     return get_players

# @query.field("playerGameweekScore")
# def resolve_player_gameweek_score(*_, id, gameweek):
#     """Retrieve a Player's gameweek score based on player_id"""
#     return get_player_stats_from_db_gql(id, gameweek)

# query get leagueReport - plug into function
# if indexed, retrieve, others create and save

@query.field("player")
def resolve_player(*_, id, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return get_player_gql(id, gameweek)

@query.field("players")
def resolve_players(*_, ids, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return [get_player_gql(id, gameweek) for id in ids]


@query.field("leagueWeeklyReport")
def resolve_league_gameweek_report(*_, league_id, gameweek):
    """Retrieve a Player's gameweek score based on player_id"""
    # return get_player_stats_from_db(id, gameweek)
    report = LeagueWeeklyReport(gameweek, league_id)
    report.get_data()
    report.weekly_score_transformation()
    report.merge_league_weekly_transfer()
    report.add_auto_sub()
    report.captain_minutes()
    output = report.create_report(display=False) #replace this with caching? 
    print(output)
    return output

# Combine the defined schema and resolvers
type_defs = load_schema_from_path("./report_app/schema.graphql")
schema = make_executable_schema(
    type_defs,
    [query],
    convert_names_case=True,
)
