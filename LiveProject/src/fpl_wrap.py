import pandas as pd
from src.utils import GameweekError, Participant
from functools import lru_cache
import numpy as np
from typing import Union

from src.utils import get_curr_event, get_participant_entry, check_gw, s, LOGGER
from src.urls import TRANSFER_URL
from src.db.db import (
    get_player_gql,
    session,
    get_ind_player_stats_from_db,
)


class Participant:
    def __init__(self, entry_id, gw):
        self.participant = entry_id
        self.gw = gw

    def get_gw_transfers(self, gw: Union[int, list[int]], all=False) -> dict:
        """Input is a list of entry_id. Gw is the gameweek number.
        'all' toggles between extracting all gameweeks or not"""

        row = {}
        try:
            valid, gw = check_gw(gw)
        except TypeError:
            valid, gw = False, None

        if all or valid:
            r = s.get(TRANSFER_URL.format(self.participant))
            LOGGER.info(r.status_code)
            if r.status_code == 200:
                obj = r.json()
                for item in obj:
                    if all:
                        row[item["event"]] = row.get(item["event"], {})
                        row[item["event"]]["element_in"] = row[item["event"]].get(
                            "element_in", []
                        )
                        row[item["event"]]["element_out"] = row[item["event"]].get(
                            "element_out", []
                        )
                        row[item["event"]]["element_in"].append(item["element_in"])
                        row[item["event"]]["element_out"].append(item["element_out"])
                    else:
                        if isinstance(gw, list) and int(item["event"]) in gw:
                            row[item["event"]] = row.get(item["event"], {})
                            row[item["event"]]["element_in"] = row[item["event"]].get(
                                "element_in", []
                            )
                            row[item["event"]]["element_out"] = row[item["event"]].get(
                                "element_out", []
                            )
                            row[item["event"]]["element_in"].append(item["element_in"])
                            row[item["event"]]["element_out"].append(
                                item["element_out"]
                            )
                        elif isinstance(gw, int) and int(item["event"]) == gw:
                            row[item["event"]] = row.get(item["event"], {})
                            row[item["event"]]["element_in"] = row[item["event"]].get(
                                "element_in", []
                            )
                            row[item["event"]]["element_out"] = row[item["event"]].get(
                                "element_out", []
                            )
                            row[item["event"]]["element_in"].append(item["element_in"])
                            row[item["event"]]["element_out"].append(
                                item["element_out"]
                            )
            else:
                print(
                    "{} does not exist or Transfer URL endpoint unavailable".format(
                        self.participant
                    )
                )
        return row

    def get_span_week_transfers(self, span: list[int]) -> dict:
        return self.get_gw_transfers(span)

    def get_all_week_transfers(self) -> dict:
        curr_gw = get_curr_event()[0]
        print("getting all entries up to {}".format(curr_gw))
        return self.get_gw_transfers(curr_gw, all=True)

    def get_all_week_entries(self, gw: Union[int, list[int]], all=False) -> list:
        if all:
            curr_gw = get_curr_event()[0]
            gw = curr_gw

        try:
            valid, gw = check_gw(gw)
        except TypeError:
            valid, gw = False, None

        if valid:
            if isinstance(gw, list):
                self.all_gw_entries = [
                    get_participant_entry(self.participant, gameweek) for gameweek in gw
                ]
            elif isinstance(gw, int):
                self.all_gw_entries = [
                    get_participant_entry(self.participant, gameweek)
                    for gameweek in range(1, gw + 1)
                ]
            return self.all_gw_entries
        else:
            raise GameweekError


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
        # output = self.output.to_dict("list")
        # r = create_cache_engine()  # save to cache
        # r.set(
        #     name=f"participant_{self.entry_id}",
        #     value=json.dumps(self.output),
        #     nx=600
        #     )

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
