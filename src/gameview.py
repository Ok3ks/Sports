import json
import requests
import pandas as pd
import os
from os.path import join, realpath

from src.urls import HISTORY_URL
from src.paths import FPL_WRAP_DIR
import seaborn.objects as so

from src.utils import Participant, to_json

def parse_fixture(fixture_db):
    fixture_df = pd.DataFrame(fixture_db)

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
    # pd.set_option()
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

    fixture_df.head(10)

    fixture_df["homewin"] = fixture_df["homegoals"] > fixture_df["awaygoals"]
    fixture_df["draw"] = fixture_df["homegoals"] == fixture_df["awaygoals"]
    fixture_df["awaywin"] = fixture_df["homegoals"] < fixture_df["awaygoals"]

    fixture_df["homewin"] = fixture_df["homewin"].astype(int)
    fixture_df["draw"] = fixture_df["draw"].astype(int)
    fixture_df["awaywin"] = fixture_df["awaywin"].astype(int)

    fixture_df.head(10)


def full_df():
    """"""
    dfs = []
    for i in range(1, 10):
        home = requests.get(gw_url.format(i))
        home = home.json()
        temp_df = pd.DataFrame(home["elements"])

        # manual way
        # interest_keys = list(temp_df['stats'][1].keys())
        # for key in interest_keys:
        #     temp_df[key] = temp_df['stats'].map(lambda x:x[key])

        # better way
        stats_df = pd.json_normalize(temp_df["stats"])
        temp_df["fixtures"] = temp_df["explain"].map(lambda x: x[0]["fixture"])
        temp_df.drop(["stats", "explain"], axis=1, inplace=True)

        dfs.append(pd.concat([temp_df, stats_df], axis=1))
        dfs

        full_df = pd.concat(dfs, axis=0)
        full_df["team"] = full_df["id"].map(lambda x: player_team_mapping[x])
        full_df["position"] = full_df["id"].map(lambda x: player_position_mapping[x])

    return full_df

def fixture_plots(fixture_df):

    """ """
    return fixture_df.groupby(["homedifficulty", "awaydifficulty"]).aggregate(
    {"homewin": "sum", "draw": "sum", "awaywin": "sum"}
    ).plot(kind="bar")