import json
import pandas as pd
from src.utils import Participant
from functools import lru_cache
import numpy as np

from src.utils import get_curr_event
from src.db.db import (
    get_player_gql,
    session,
    get_ind_player_stats_from_db,
)


class ParticipantReport(Participant):
    """Creates a report from start of a gameweek to a span gameweek"""

    def __init__(self, gw: int, entry_id: int):
        super().__init__(entry_id, gw)
        self.gw = gw
        self.entry_id = entry_id

    @lru_cache
    def weekly_score_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""

        one_df = pd.DataFrame(self.get_all_week_entries(gw=self.gw, all=True))
        self.o_df = one_df[~one_df["players"].isna()]

        self.o_df["points_breakdown"] = [
            [
                get_ind_player_stats_from_db(y, event)
                for y in self.o_df["players"][event - 1].split(",")
            ]
            for event in range(1, self.gw + 1)
        ]

        self.o_df["highest_scoring_player"] = self.o_df["points_breakdown"].apply(
            np.argmax
        )
        self.o_df["highest_scoring_player"] = [
            i.players.split(",")[i.highest_scoring_player]
            for i in self.o_df.itertuples()
        ]
        self.o_df["highest_scoring_player_points"] = self.o_df[
            "points_breakdown"
        ].apply(max)

        self.o_df["captain_points"] = [
            get_ind_player_stats_from_db(self.o_df["captain"][event - 1], event) * 2
            for event in range(1, self.gw + 1)
        ]
        self.o_df["vice_captain_points"] = [
            get_ind_player_stats_from_db(self.o_df["vice_captain"][event - 1], event)
            for event in range(1, self.gw + 1)
        ]

        print(self.o_df)
        self.o_df.rename(columns={"entry": "entry_id"}, inplace=True)
        return self.o_df

    @lru_cache
    def merge_league_weekly_transfer(self):
        """Merges Weekly score dataframe with transfers dataframe"""
        self.f = self.get_all_week_transfers()
        transfer_weeks = set(self.f.keys())
        all_weeks = set(range(1, self.gw + 1))

        # weeks transfers were not made
        diff = all_weeks.difference(transfer_weeks)

        for element in diff:
            self.f.update({element: {"element_in": [], "element_out": []}})

        self.f = pd.DataFrame(self.f)
        self.f = self.f.T
        self.f["entry_id"] = self.entry_id
        self.f.sort_index(inplace=True)

        self.f["transfer_points_in"] = [
            sum(
                [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["element_in"][event]
                ]
            )
            for event in range(1, self.gw + 1)
        ]
        # self.f['transfer_points_in'] = self.f['element_in'].map(lambda x: sum([get_player_stats_from_db(y, self.gw)[0] for y in x]))
        self.f["transfer_points_out"] = [
            sum(
                [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["element_out"][event]
                ]
            )
            for event in range(1, self.gw + 1)
        ]
        # self.f['transfer_points_out'] = self.f['element_out'].map(lambda x:sum([get_player_stats_from_db(y, self.gw)[0]for y in x]))
        self.f["transfers"] = self.f["element_out"].map(lambda x: len(x))
        self.f["delta"] = self.f["transfer_points_in"] - self.f["transfer_points_out"]
        self.f.reset_index(inplace=True, names="gw")
        self.f.drop(inplace=True, axis=1, labels="entry_id")
        self.f = self.o_df.merge(self.f, on="gw", how="right")
        return self.f

    def add_auto_sub(self):
        # self.f["auto_sub_in_player"] = self.f["auto_sub_in"]  # .map(lambda x: x["in"])
        # self.f["auto_sub_out_player"] = self.f[
        #     "auto_sub_out"
        # ]  # .map(lambda x: x["out"])
        self.f["auto_sub_in_points"] = [
            sum(
                i for i in
                [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["auto_sub_in"][event - 1].strip().split(",")
                ]
                if isinstance(i, int)
            )
            for event in range(1, self.gw + 1)
        ]
        self.f["auto_sub_out_points"] = [
            sum(
                i for i in
                [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["auto_sub_out"][event - 1].split(",")
                ]
                if isinstance(i, int)
            )
            for event in range(1, self.gw + 1)
        ]

    def prep_for_gql(self):
        self.output = self.o_df.to_dict("list")
        for key, value in self.output.items():
            if key in ["captain", "vice_captain", "highest_scoring_player"]:
                self.output[key] = [
                    get_player_gql(id=player_id, gameweek=gameweek + 1, session=session)
                    for gameweek, player_id in enumerate(value)
                ]

    def create_report(self, display=False):

        if display:
            print(self.output)
        else:
            return self.output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="FPLWRAP", description="Provider")

    parser.add_argument(
        "-g",
        "--gameweek",
        type=int,
        default=get_curr_event()[0],
        help="Gameweek you are trying to get a report of",
    )
    parser.add_argument(
        "-l",
        "--entry_id",
        type=int,
        required=True,
        help="ID of pkayer you're interested in ",
    )
    args = parser.parse_args()

    test = ParticipantReport(args.gameweek, args.entry_id)
    test.weekly_score_transformation()
    test.merge_league_weekly_transfer()
    test.add_auto_sub()

    test.create_report(display=True)
