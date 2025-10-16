import json
import os
from typing import List, Any
import pandas as pd

from LiveProject.src.utils import bucket_client
from src.db.db import (
    get_player_name_map,
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


def parse_stats(filter={"gameweek": 38}, to_dict=True, path: str = "" , upload=False) -> dict[str, Any] | pd.DataFrame:
    """Combine Season stats from DB, and map appropriately."""

    stats = get_season_stats()
    player_team_mapping = get_player_team_map()
    player_position_mapping = get_player_position_map()
    player_name_mapping = get_player_name_map()

    full_df: pd.DataFrame = pd.DataFrame(stats)
    full_df = full_df[full_df['gameweek'] == filter['gameweek']]

    full_df["player_name"] = full_df["player_id"].map(lambda x: player_name_mapping[x])
    full_df["team"] = full_df["player_id"].map(lambda x: player_team_mapping[x])
    full_df["position"] = full_df["player_id"].map(lambda x: player_position_mapping[x])

    if to_dict:
        obj = full_df.to_dict("records") 
    
    output_path = f"{args.path}.json" if args.path else f"data/gameview/{args.gameweek_id}.json"
    with open(output_path, "w") as outs:
        json.dump(obj, outs)

    if upload:
        bucket=bucket_client(bucket_name="2025_2026")
        blob = bucket.blob(f"{output_path}")
        blob.upload_from_filename(output_path)

    return obj


# ToDo : add kwargs to function to customise groupbys
def groupby(groups: set[str] = {"gameweek", "position"}):
    """Calculate aggregates groupby."""
    all_groups = {"gameweek", "position", "team"}
    stats = parse_stats(filter={"gameweek": 38},to_dict=False)
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
    return [out]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-p", "--path", type=str, help="Path to save json")
    parser.add_argument("u", "--upload", type=bool, help="Boolean: Upload/Not")
    args = parser.parse_args()

    parse_stats(
            filter={
                "gameweek": args.gameweek_id
                }, to_dict=True,
                path=args.path,
                upload=args.upload)
    
    
