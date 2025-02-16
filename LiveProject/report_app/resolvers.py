"""Ariadne's answer to views.py"""
# ruff: noqa: A002

from ariadne import (
    ObjectType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)


# from .models import (Players, Gameweek_Scores)
from src.db.db import create_cache_engine, get_gameweek_stats, get_player_gql
from src.fpl_wrap import ParticipantReport
from src.gameview import groupby
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
def resolve_season_stats(*_, use_gameweek: bool, use_position: bool, use_team: bool):
    """Retrieve season statistics for all players by either gameweek, position, or team"""
    if use_gameweek & use_position:
        return groupby(groups={"gameweek", "position"})


@query.field("player")
def resolve_player(*_, id, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return get_player_gql(id, gameweek)


@query.field("players")
def resolve_players(*_, ids, gameweek):
    """Retrieve a Player's information by ID or return None if not found."""
    return [get_player_gql(id, gameweek) for id in ids]


@functools.cache
@query.field("participantReport")
def resolve_participant(*_, entry_id, gameweek=None):
    """Retrieve a participant's league analysis"""

    if not gameweek:
        gameweek = get_curr_event()[0]

    # r = create_cache_engine()
    # output = r.get(f"participant_{entry_id}")  # Currently loading it all into memory
    output = None
    if output:
        print("Obtained from cache")
        return json.loads(output)
    else:
        participant = ParticipantReport(gw=gameweek, entry_id=entry_id)
        participant.weekly_score_transformation()
        participant.merge_league_weekly_transfer()
        participant.add_auto_sub()
        participant.prep_for_gql()

    output = participant.create_report(display=False)
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
