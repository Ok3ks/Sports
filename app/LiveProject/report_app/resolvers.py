"""Ariadne's answer to views.py"""
# ruff: noqa: A002

from ariadne import (
    ObjectType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)
from django.contrib.auth.hashers import make_password
from .models import (Players, Gameweek_Scores)
from src.db.db import get_player

# Acknowledgement, Message,
from .shortcuts import get_object_or_none

query = QueryType()
_document = ObjectType("Document")


# Query resolvers
@query.field("players")
def resolve_players(*_):
    """Retrieve all Player model instances."""
    return Players.objects.all()


@query.field("player")
def resolve_player(*_, id, half):
    """Retrieve a User model instance by ID or return None if not found."""
    # player = Players.objects.filter(half=half)
    # player = Players.objects.get(half=half, player_id=id)
    return get_player(id, half)


@query.field("playerGameweekScore")
def resolve_player_gameweek_score(*_, id):
    """Retrieve a Player's gameweek score based on player_id"""
    return get_object_or_none(Gameweek_Scores, pk=id)


@query.field("gameweekScore")
def resolve_player_gameweek_scores(*_,):
    """Retrieve a Player's gameweek score based on player_id"""
    return Gameweek_Scores().objects.all

# Combine the defined schema and resolvers
type_defs = load_schema_from_path("./report_app/schema.graphql")
schema = make_executable_schema(
    type_defs,
    [query],
    convert_names_case=True,
)
