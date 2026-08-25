import json
import os
from typing import List, Any
import pandas as pd
import pathlib
import anyio
from src.db.db import (
    get_player_name_map,
    get_player_position_map,
    get_player_team_map,
    get_season_stats,
    get_teams_id,
    get_fixtures,
    SEASON
)

def parse_fixture(to_dict=True, upload=False, path: str = ""):
    """Parse Fixtures from DB."""
    fixture = get_fixtures(season=SEASON)

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


    for gameweek in range(1, 38):
        temp_df = fixture_df[fixture_df["gameweek"] == gameweek]
        temp_df.fillna(0, inplace=True)
        if to_dict:
            obj = temp_df.to_dict("records")

        output_path = pathlib.Path(path) if path else pathlib.Path(f"data/gameview/")
        output_path.mkdir(parents=True, exist_ok=True)
        filename = f"{gameweek}_fixture.json"

        with open(output_path / filename, "w") as outs:
            json.dump(obj, outs)

        if upload:
            from src.utils import bucket_client

            bucket = bucket_client(bucket_name=SEASON)  # parameter
            blob = bucket.blob(filename)
            blob.upload_from_filename(output_path / filename)

    return fixture_df


def parse_stats(
    filter={"gameweek": 38}, to_dict=True, path: str = "", upload=False
) -> dict[str, Any] | pd.DataFrame:
    """Combine Season stats from DB, and map appropriately."""

    stats = get_season_stats()
    player_team_mapping = get_player_team_map()
    player_position_mapping = get_player_position_map()
    player_name_mapping = get_player_name_map()

    full_df: pd.DataFrame = pd.DataFrame(stats)
    full_df = full_df[full_df["gameweek"] == filter["gameweek"]]

    full_df["player_name"] = full_df["player_id"].map(lambda x: player_name_mapping[x])
    full_df["team"] = full_df["player_id"].map(lambda x: player_team_mapping[x])
    full_df["position"] = full_df["player_id"].map(lambda x: player_position_mapping[x])

    if to_dict:
        obj = full_df.to_dict("records")
    output_path = pathlib.Path(path) if path else pathlib.Path(f"data/gameview/")
    output_path.mkdir(parents=True, exist_ok=True)
    filename = f"{filter['gameweek']}.json"

    with open(output_path / filename, "w") as outs:
        json.dump(obj, outs)

    if upload:
        from src.utils import bucket_client

        bucket = bucket_client(bucket_name=SEASON)  # parameter
        blob = bucket.blob(filename)
        blob.upload_from_filename(output_path / filename)

    return obj


# ToDo : add kwargs to function to customise groupbys
def groupby(groups: set[str] = {"gameweek", "position"}):
    """Calculate aggregates groupby."""
    all_groups = {"gameweek", "position", "team"}
    stats = parse_stats(filter={"gameweek": 38}, to_dict=False)
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


async def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-p", "--path", type=str, help="Path to save json")
    parser.add_argument("-u", "--upload", type=bool, help="Boolean: Upload/Not")
    parser.add_argument(
        "-f", "--fixture", type=bool, help="Process Fixtures Only", default=False
    )

    args = parser.parse_args()

    if args.fixture:
        parse_fixture(to_dict=True, upload=args.upload)
    else:
        parse_stats(
            filter={"gameweek": args.gameweek_id},
            to_dict=True,
            path=args.path,
            upload=args.upload,
        )


if __name__ == "__main__":
    anyio.run(main)
