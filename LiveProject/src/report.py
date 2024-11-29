from paths import WEEKLY_REPORT_DIR, MOCK_DIR
from functools import lru_cache
import operator

import pandas as pd
import json

from .utils import get_basic_stats, League, to_json
from .db.db import (
    get_player_stats_from_db,
    check_minutes,
    create_cache_engine,
)
import math


if "line_profiler" not in dir() and "profile" not in dir():

    def profile(func):
        return func


class LeagueWeeklyReport(League):
    #
    @profile
    def __init__(self, gw: int, league_id: int):
        super().__init__(league_id)
        self.gw = gw
        # self.participants = self.obtain_league_participants()

    @lru_cache()
    @profile
    def get_data(self):
        self.one_df = pd.DataFrame(self.get_all_participant_entries(self.gw))
        self.f = pd.DataFrame(self.get_gw_transfers(self.gw))
        self.f = self.f.T
        print(self.f.columns)

    @lru_cache(10)
    @profile
    def weekly_score_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""

        self.o_df = self.one_df[~self.one_df["players"].isna()]

        # optimization 4 - loaded all player rows into memory at once
        self.player_points = get_player_stats_from_db(self.gw)
        # del player_set

        self.o_df["points_breakdown"] = self.o_df["players"].map(
            lambda x: [
                self.player_points[int(y)] for y in x.split(",") if len(y.strip()) >= 1
            ]
        )

        # print(self.o_df['captain'].isna())
        self.o_df["captain_points"] = self.o_df["captain"].map(
            lambda x: self.player_points[int(x)] * 2 if math.isnan(x) != True else 0
        )
        self.o_df["vice_captain_points"] = self.o_df["vice_captain"].map(
            lambda x: self.player_points[x] if math.isnan(x) != True else 0
        )

        # optimization 3
        self.o_df = self.o_df.sort_values(
            by="total_points", ascending=False
        ).reset_index(drop=True)
        self.o_df["rank"] = [i + 1 for i in self.o_df.index.to_list()]
        return self.o_df

    @lru_cache(10)
    @profile
    def merge_league_weekly_transfer(self):
        """Merges Weekly score dataframe with transfers dataframe"""

        if "element_in" in self.f.columns.to_list():
            print("In merge league weekly")
            self.f["transfer_points_in"] = self.f["element_in"].map(
                lambda x: sum([self.player_points[int(y)] for y in x])
            )
            self.f["transfer_points_out"] = self.f["element_out"].map(
                lambda x: sum([self.player_points[y] for y in x])
            )
            self.f["transfers"] = self.f["element_out"].map(lambda x: len(x))
            self.f["delta"] = (
                self.f["transfer_points_in"] - self.f["transfer_points_out"]
            )

            self.f.reset_index(inplace=True)
            self.f.rename(columns={"index": "entry_id"}, inplace=True)
            self.f["entry_id"] = self.f["entry_id"].astype(int)
            self.f = self.o_df.merge(self.f, on="entry_id", how="right")

        else:
            self.f = self.o_df
            self.f["delta"] = 0

        return self.f

    def captain_minutes(self):
        self.o_df["cap_minutes"] = [
            check_minutes(x, self.gw)[0] for x in self.o_df["captain"]
        ]

    @profile
    def add_auto_sub(self):
        if "auto_sub_in" in self.f.columns:
            print(self.f["auto_sub_in"].tolist())

            # optimization 1 - switching dictionaries to tuples
            self.f["auto_sub_in_player"] = self.f["auto_sub_in"].map(
                lambda x: [y for y in x.split(",") if len(x) > 3]
            )
            self.f["auto_sub_out_player"] = self.f["auto_sub_out"].map(
                lambda x: [y for y in x.split(",") if len(x) > 3]
            )

            self.f["auto_sub_in_points"] = self.f["auto_sub_in_player"].map(
                lambda x: sum([self.player_points[int(y)] for y in x])
            )

    @profile
    def create_report(self, display=True):
        self.captain = self.o_df["captain"].value_counts().to_dict()

        self.captain = [{"player": k, "count": v} for k, v in self.captain.items()]
        self.chips = {}
        self.no_chips = pd.DataFrame([])

        if "active_chip" in self.f.columns:
            self.chips = (
                self.f["active_chip"].value_counts().to_dict()
            )  # More report based on this
            self.no_chips = self.f[self.f["active_chip"].isna()]

        self.participants = self.obtain_league_participants()
        self.participants_name = self.get_participant_name()

        def get_league_name():
            return {"league_name": self.league_name}

        @profile
        def rise_and_fall():
            """Outputs the rise of the week and falls of the week"""

            rise = []
            fall = []

            df = pd.DataFrame(self.participants)
            df["rank"] = df["rank"].astype(int)
            df["last_rank"] = df["last_rank"].astype(int)
            df["rank_delta"] = df["last_rank"] - df["rank"]

            rise_df = df[df["rank_delta"] > 0].sort_values(
                by="rank_delta", ascending=False
            )
            fall_df = df[df["rank_delta"] < 0].sort_values(
                by="rank_delta", ascending=True
            )

            n = min(len(rise_df), 3)
            for i in range(0, n):
                temp = {}
                cur_rank = int(rise_df.iloc[i, :]["rank"])
                last_rank = int(rise_df.iloc[i, :]["last_rank"])
                participant_name = str(rise_df.iloc[i, :]["player_name"])

                temp["current_rank"] = cur_rank
                temp["prev_rank"] = last_rank
                temp["participant_name"] = participant_name
                rise.append(temp)

            n = min(len(fall_df), 3)

            for i in range(0, n):
                temp = {}
                cur_rank = int(fall_df.iloc[i, :]["rank"])
                last_rank = int(fall_df.iloc[i, :]["last_rank"])
                participant_name = str(fall_df.iloc[i, :]["player_name"])

                temp["current_rank"] = cur_rank
                temp["prev_rank"] = last_rank
                temp["participant_name"] = participant_name
                fall.append(temp)
            return {"rise": rise, "fall": fall}

        # @profile
        # def promoted_vice():
        #     self.o_df["promoted_vice"] = self.o_df["cap_minutes"].map(lambda x: True if x == 0 else False)
        #     promoted_vice = (
        #         self.o_df[self.o_df["promoted_vice"] == True]
        #         .sort_values(by="vice_captain_points", ascending=False)
        #         .reset_index(drop=True)
        #         .iloc[:3, :]
        #     )

        #     return [
        #         {
        #             'promoted_vice_points': i.vice_captain_points * 2,
        #             'participants_name': self.participants_name[str(i.entry_id)],
        #             'captain_name': i.captain,
        #             'vice_captain_name': i.vice_captain,
        #         }
        #         for i in promoted_vice.itertuples()
        #     ]

        @profile
        def outliers():
            Q1, league_average, Q3 = get_basic_stats(self.o_df["total_points"])
            IQR = Q3 - Q1
            # exceptional_df = self.o_df[self.o_df['total_points'] > Q3 +1.5*IQR]
            max_df = self.o_df[
                self.o_df["total_points"] == self.o_df["total_points"].max()
            ]
            abysmal_df = self.o_df[self.o_df["total_points"] < Q1 - 1.5 * IQR]

            exceptional = {}
            abysmal = {}

            for i, j in zip(max_df["entry_id"], max_df["total_points"]):
                exceptional["team_name"] = self.participants_name[str(i)]
                exceptional["score"] = j

            for i, j in zip(abysmal_df["entry_id"], abysmal_df["total_points"]):
                abysmal["team_name"] = self.participants_name[str(i)]
                abysmal["score"] = j

            return {
                "exceptional": exceptional,
                "abysmal": abysmal,
                "league_average": league_average,
            }

        #
        @profile
        def out_transfer_stats():
            """ """
            most_transf_out = []

            if "element_out" in self.f.keys().to_list():
                n = min(len(self.f), 3)
                counts = self.f["element_out"].value_counts().reset_index().to_dict()
                most_transf_out = [
                    {
                        "out": counts["count"][i],
                        "player": counts["element_out"][i][0],
                    }
                    for i in range(n)
                ]

            return {
                "most_transferred_out": most_transf_out,
                # "least_transferred_out": least_transf_out,
            }

        @profile
        def in_transfer_stats():
            """Output = {"most_transferred_in" : [], "least_transferred_in": []}"""

            most_transf_in = []
            # least_transf_in = []
            if "element_in" in self.f.keys().to_list():
                n = min(len(self.f), 3)

                counts = (
                    self.f["element_in"].value_counts().reset_index().to_dict("list")
                )

                most_transf_in = [
                    {
                        "in": counts["count"][i],
                        "player": counts["element_in"][i][0],
                    }
                    for i in range(n)
                ]

                # least_transf_in = [
                #     (counts["element_in"][-i], get_player(counts["index"][-i])) for i in range(-1, -1 - n)
                # ]  # because -0 == 0

            return {
                "most_transferred_in": most_transf_in,
                # "least_transferred_in": least_transf_in,
            }

        #
        @profile
        def worst_transfer_in():
            """Output = {"worst_transfer_in":[()]}"""
            worst_transfer_in = []

            if len(self.no_chips) > 2:
                n = min(len(self.f), 3)

                if "element_in" in self.f.keys() and "element_out" in self.f.keys():
                    self.no_chips = self.no_chips.sort_values(
                        by="delta", ascending=False
                    )
                    for i in range(1, n):
                        player_in = self.no_chips.iloc[-i, :]["element_in"][0]
                        player_out = self.no_chips.iloc[-i, :]["element_out"][0]
                        points_lost = int(self.no_chips.iloc[-i, :]["delta"])
                        participant_id = str(self.no_chips.iloc[-i, :]["entry_id"])

                        worst_transfer_in.append(
                            {
                                "team_name": self.participants_name[participant_id],
                                "player_in": int(player_in),
                                "player_out": int(player_out),
                                "points_delta": points_lost,
                            }
                        )
            return {"worst_transfer_in": worst_transfer_in}

        @profile
        def best_transfer_in():
            best_transfer_in = []
            if len(self.no_chips) > 2:
                self.no_chips = self.no_chips.sort_values(by="delta", ascending=False)
                print(self.no_chips["delta"])
                n = min(len(self.f), 3)

                if "element_in" in self.f.keys() and "element_out" in self.f.keys():
                    self.no_chips.head(3).to_json(path_or_buf="../temp.json")
                    for i in range(0, n):
                        player_in = self.no_chips.iloc[i, :]["element_in"][0]
                        player_out = self.no_chips.iloc[i, :]["element_out"][0]
                        points_gained = int(self.no_chips.iloc[i, :]["delta"])
                        participant_id = str(self.no_chips.iloc[i, :]["entry_id"])

                        best_transfer_in.append(
                            {
                                "team_name": self.participants_name[participant_id],
                                "player_in": int(player_in),
                                "player_out": int(player_out),
                                "points_delta": points_gained,
                            }
                        )

            return {"best_transfer_in": best_transfer_in}

        @profile
        def jammy_points():
            """Points obtained from the bench"""

            jammy_points = []
            self.f = self.f.sort_values(by="auto_sub_in_points", ascending=False)

            n = min(len(self.f), 3)
            for i in range(n):
                auto_sub_in = self.f.iloc[i, :]["auto_sub_in_player"]
                auto_sub_out = self.f.iloc[i, :]["auto_sub_out_player"]
                auto_sub_points = int(self.f.iloc[i, :]["auto_sub_in_points"])
                participant_id = str(self.f.iloc[i, :]["entry_id"])

                jammy_points.append(
                    {
                        "team_name": self.participants_name[participant_id],
                        "sub_in": auto_sub_in,
                        "sub_out": auto_sub_out,
                        "points": auto_sub_points,
                    }
                )
            return {"jammy_points": jammy_points}

        def most_benched():
            player_on_bench = self.f["bench"].to_list()
            player_on_bench = ",".join(player_on_bench)
            player_on_bench = player_on_bench.split(",")
            print(player_on_bench)

            resultDict = {}
            for i in player_on_bench:
                if len(i.strip()) >= 1:
                    resultDict[i] = resultDict.get(i, 0) + 1
            print(resultDict)

            # resultDict = dict(sorted(resultDict.items(), key=operator.itemgetter(1), reverse=True))
            pointsDict = {
                player: self.player_points[int(player)]
                for player, _ in resultDict.items()
            }
            pointsDict = dict(
                sorted(pointsDict.items(), key=operator.itemgetter(1), reverse=True)
            )

            resultDictGraph = {}

            resultDictGraph["player"] = [player for player in pointsDict.keys()]
            resultDictGraph["count"] = [
                resultDict[player] for player in resultDictGraph["player"]
            ]
            resultDictGraph["points"] = [points for points in pointsDict.values()]

            # resultDict = dict(sorted(resultDictGraph.items(), key=operator.itemgetter('points'), reverse=True))
            # most scoring bench player?
            return {"most_benched": resultDictGraph}

        @profile
        def most_points_on_bench():
            self.f = self.f.sort_values(by="points_on_bench", ascending=False)
            most_points = []

            n = min(len(self.f), 3)
            for i in range(n):
                player_on_bench = self.f.iloc[i, :]["bench"].split(",")
                # point_player = {i: self.player_points[int(i)] for i in player_on_bench}
                points_on_bench = int(self.f.iloc[i, :]["points_on_bench"])
                participant_id = str(self.f.iloc[i, :]["entry_id"])
                most_points.append(
                    {
                        "team_name": self.participants_name[participant_id],
                        "players": player_on_bench,
                        "point_on_bench": points_on_bench,
                    },
                )
            return {"most_points_on_bench": most_points}

        # self.vice_to_cap = promoted_vice()

        output = {
            "captain": self.captain,
            "chips": self.chips,
        }

        output.update(outliers())
        output.update(rise_and_fall())

        output.update(out_transfer_stats())
        output.update(in_transfer_stats())

        output.update(best_transfer_in())  # does not consider hits
        output.update(worst_transfer_in())

        output.update(most_points_on_bench())
        output.update(jammy_points())
        output.update(most_benched())

        output.update(get_league_name())

        # Save to redis
        r = create_cache_engine()  # save to cache
        r.set(f"league_{self.league_id}_{self.gw}", json.dumps(output))

        if display:
            print(output)
            to_json(
                output, f"{WEEKLY_REPORT_DIR}/{str(self.league_id)}_{str(self.gw)}.json"
            )

        return output


# Output of report page should be a json for a django template
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="weeklyreport", description="Provide Gameweek ID and League ID"
    )

    parser.add_argument(
        "-g",
        "--gameweek_id",
        type=int,
        help="Gameweek you are trying to get a report of",
    )
    parser.add_argument(
        "-l", "--league_id", type=int, help="League_ID you are interested in"
    )
    parser.add_argument(
        "-t", "--thread", type=int, help="Number of threads to run program on"
    )
    parser.add_argument("-dry", "--dry_run", type=bool, help="Dry run")

    args = parser.parse_args()

    if args.dry_run:
        test = LeagueWeeklyReport(args.gameweek_id, args.league_id)
        with open(f"{MOCK_DIR}/leagues/weekly_score_transformation.json", "r") as ins:
            test.o_df = json.load(ins)

        with open(f"{MOCK_DIR}/leagues/add_auto_sub.json", "r") as ins:
            test.f = json.load(ins)

        with open(f"{MOCK_DIR}/leagues/participants.json", "r") as ins:
            test.participants = json.load(ins)

        test.o_df = pd.DataFrame(test.o_df)
        test.f = pd.DataFrame(test.f)
        test.participants = test.participants["participants"]
        output = test.create_report(display=True)

    else:
        test = LeagueWeeklyReport(args.gameweek_id, args.league_id)
        test.get_data()
        # test.get_all_participant_entries(args.gameweek_id, thread = args.thread)
        # print(test.get_all_participant_entries(args.gameweek_id))
        # print(test.res)

        test.weekly_score_transformation()
        test.merge_league_weekly_transfer()
        test.add_auto_sub()
        test.captain_minutes()
        output = test.create_report(display=True)
