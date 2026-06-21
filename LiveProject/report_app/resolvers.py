"""Ariadne's answer to views.py"""
# ruff: noqa: A002

from ariadne import (
    ObjectType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)


# from .models import (Players, Gameweek_Scores)
from src.season_league_analysis import story_2
from src.db.db import get_gameweek_stats, get_player_gql
from src.fpl_wrap import ParticipantReport
from src.gameview import parse_stats
from src.report import LeagueWeeklyReport
from src.utils import get_curr_event
import functools

# from .shortcuts import get_object_or_none
import json

query = QueryType()
_document = ObjectType("Document")


@query.field("gameweekScore")
def resolve_gameweek_stats(*_, gameweek):
    """Retrieve gameweek statistics of all players"""
    return get_gameweek_stats(gameweek)


@query.field("gameViewReport")
def resolve_season_stats(*_, gameweek):
    """Retrieve season statistics for all players by either gameweek, position, or team"""
    return parse_stats(filter={"gameweek": gameweek})



@query.field("player")
def resolve_player(*_, id, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return get_player_gql(id, gameweek)


@query.field("players")
def resolve_players(*_, ids, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return [get_player_gql(id, gameweek) for id in ids]


@functools.cache
@query.field("seasonParticipantReport")
def resolve_participant(*_, season , entry_id):
    """Retrieve a participant's league analysis"""

    gameweek = get_curr_event()[0]

    output = None
    if output:
        print("Obtained from cache")
        return json.loads(output)
    else:
        season_report  = ParticipantReport(gameweek, entry_id)
        output = season_report.participant_stats()

    return output


@query.field("leagueWeeklyReport")
def resolve_league_gameweek_report(*_, league_id, gameweek):
    """Retrieve a Player's gameweek score based on player_id"""

    report = LeagueWeeklyReport(gameweek, league_id)
    report.get_data()
    report.weekly_score_transformation()
    report.merge_league_weekly_transfer()
    report.add_auto_sub()
    report.captain_minutes()
    output = report.create_report(display=False)  # replace this with caching?     

    print(output)
    print("Recomputed")
    return output


# Combine the defined schema and resolvers
type_defs = load_schema_from_path("./report_app/schema.graphql")
schema = make_executable_schema(
    type_defs,
    [query],
    convert_names_case=True,
)
