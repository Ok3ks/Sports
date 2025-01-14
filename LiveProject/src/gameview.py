import json
from typing import List
import pandas as pd

from src.db.db import (
    get_player_position_map,
    get_player_team_map,
    get_season_stats,
    get_teams_id,
    get_fixtures,
)


def parse_fixture():
    """Parse Fixtures from DB."""
    fixture = get_fixtures()
    team_id_to_name = get_teams_id()

    fixture_df = pd.DataFrame(fixture)
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

    fixture_df["home"] = fixture_df["home"].map(lambda x: team_id_to_name[x])
    fixture_df["away"] = fixture_df["away"].map(
        lambda x: team_id_to_name[x]
    )  # different from full_df

    fixture_df["code"] = (
        fixture_df["code"].astype(int).map(lambda x: x - 2444470)
    )  # to match full_df

    fixture_df.rename({"code": "fixtures"}, axis=1, inplace=True)

    fixture_df["homewin"] = fixture_df["homegoals"] > fixture_df["awaygoals"]
    fixture_df["draw"] = fixture_df["homegoals"] == fixture_df["awaygoals"]
    fixture_df["awaywin"] = fixture_df["homegoals"] < fixture_df["awaygoals"]

    fixture_df["homewin"] = fixture_df["homewin"].astype(int)
    fixture_df["draw"] = fixture_df["draw"].astype(int)
    fixture_df["awaywin"] = fixture_df["awaywin"].astype(int)

    return fixture_df


def parse_stats():
    """Combine Season stats from DB, and map appropriately."""

    stats = get_season_stats()
    player_team_mapping = get_player_team_map()
    player_position_mapping = get_player_position_map()
    full_df = pd.DataFrame(stats)

    full_df["team"] = full_df["player_id"].map(lambda x: player_team_mapping[x])
    full_df["position"] = full_df["player_id"].map(lambda x: player_position_mapping[x])
    return full_df


# ToDo : add kwargs to function to customise groupbys
def groupby(groups: set[str] = {"gameweek", "position"}):
    """Calculate aggregates groupby."""
    all_groups = {"gameweek", "position", "team"}
    stats = parse_stats()
    obj = stats.groupby(list(groups)).aggregate(
        {
            "goals_scored": "sum",
            "total_points": ["sum"],
            "assists": "sum",
        }
    )
    ref = obj.reset_index().to_dict("list")
    out = {}
    for key, value in ref.items():
        if key[1] != "":
            value.append(key[1])
        out.update(
            {key[0]: [str(v) for v in value]}
        )  # casting to string for graphql compatibility, not mixing types
    del ref
    last_key = list(all_groups.difference(groups))[0]
    out.update({last_key: [""]})
    print(out)
    return [out]


# def fixture_plots(fixture_df):
# """ """
# return fixture_df.groupby(["homedifficulty", "awaydifficulty"]).aggregate(
# {"homewin": "sum", "draw": "sum", "awaywin": "sum"}
# ).plot(kind="bar")


if __name__ == "__main__":
    print(groupby())
