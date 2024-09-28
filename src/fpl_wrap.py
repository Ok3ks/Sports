import operator
import requests
import pandas as pd
import os
from os.path import join, realpath

from src.urls import FPL_PLAYER, HISTORY_URL
from src.paths import FPL_WRAP_DIR
import seaborn.objects as so

from src.utils import Participant, to_json
from src.paths import WEEKLY_REPORT_DIR
from functools import lru_cache
import operator

import os
import pandas as pd
from src.utils import get_basic_stats, get_curr_event
from src.db.db import get_player, get_player_stats_from_db, check_minutes


class ParticipantReport(Participant):
    """Creates a report from start of a gameweek to a span gameweek"""

    def __init__(self, gw: int, entry_id: int):
        super().__init__(entry_id, gw)
        self.gw = gw
        self.entry_id = entry_id

    @lru_cache
    def weekly_score_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""

        one_df = pd.DataFrame(self.get_all_week_entries())
        self.o_df = one_df[~one_df["players"].isna()]

        self.o_df["points_breakdown"] = [
            [get_player_stats_from_db(y, event)[0] for y in self.o_df["players"][event - 1].split(",")]
            for event in range(1, self.gw + 1)
        ]
        self.o_df["captain_points"] = [
            get_player_stats_from_db(self.o_df["captain"][event - 1], event)[0] * 2
            for event in range(1, self.gw + 1)
        ]
        self.o_df["vice_captain_points"] = [
            get_player_stats_from_db(self.o_df["vice_captain"][event - 1], event)[0]
            for event in range(1, self.gw + 1)
        ]

        self.o_df["rank"] = self.o_df["total_points"].rank(ascending=False)
        self.o_df.rename(columns={"entry": "entry_id"}, inplace=True)
        self.o_df["rank"] = self.o_df["rank"].map(int)
        print(self.o_df)
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
            sum([get_player_stats_from_db(y, event)[0] for y in self.f["element_in"][event]])
            for event in range(1, self.gw + 1)
        ]
        # self.f['transfer_points_in'] = self.f['element_in'].map(lambda x: sum([get_player_stats_from_db(y, self.gw)[0] for y in x]))
        self.f["transfer_points_out"] = [
            sum([get_player_stats_from_db(y, event)[0] for y in self.f["element_out"][event]])
            for event in range(1, self.gw + 1)
        ]
        # self.f['transfer_points_out'] = self.f['element_out'].map(lambda x:sum([get_player_stats_from_db(y, self.gw)[0]for y in x]))
        self.f["transfers"] = self.f["element_out"].map(lambda x: len(x))
        self.f["delta"] = self.f["transfer_points_in"] - self.f["transfer_points_out"]
        self.f.reset_index(inplace=True, names="gw")
        self.f.drop(inplace=True, axis=1, labels="entry_id")
        self.f = self.o_df.merge(self.f, on="gw", how="right")
        print(self.f)
        return self.f

    def add_auto_sub(self):
        self.f["auto_sub_in_player"] = self.f["auto_subs"].map(lambda x: x["in"])
        self.f["auto_sub_out_player"] = self.f["auto_subs"].map(lambda x: x["out"])
        self.f["auto_sub_in_points"] = [
            sum([get_player_stats_from_db(y, event)[0] for y in self.f["auto_sub_in_player"][event - 1]])
            for event in range(1, self.gw + 1)
        ]
        self.f["auto_sub_out_points"] = [
            sum([get_player_stats_from_db(y, event)[0] for y in self.f["auto_sub_out_player"][event - 1]])
            for event in range(1, self.gw + 1)
        ]

    def plots_1(self):
        self.f["captain"] = self.f["captain"].map(lambda x: get_player(x))
        captain_bar_chart = (
            so.Plot(self.f, x="captain")
            .add(so.Bars(), so.Count())
            .scale(y=so.Continuous().tick(every=1))
            .label(y="Count")
        )

        os.makedirs(realpath(join(FPL_WRAP_DIR, str(args.player_id))), exist_ok=True)
        captain_bar_chart.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), "captain_bar_chart.png")))

        points_on_bench = (
            so.Plot(self.f, y="points_on_bench", x="gw")
            .add(so.Lines())
            .add(so.Dots(color="C2"))
            .scale(y=so.Continuous().tick(every=2), x=so.Continuous().tick(every=1))
        )

        points_on_bench.save(realpath(join(FPL_WRAP_DIR, str(args.player_id), "points_on_bench.png")))

    def plots_2(self):
        r = requests.get(HISTORY_URL.format(self.entry_id))
        r = r.json()

        history = r["current"]
        history = pd.DataFrame(history)
        history["value"] = history["value"] / 10
        history["bank"] = history["bank"] / 10

        history.rename(columns={"event": "gameweek"}, inplace=True)
        history.set_index("gameweek", inplace=True)

        line_plot = (
            so.Plot(history, x="gameweek", y="points")
            .add(so.Lines(color="C1"))
            .add(so.Dots(color="C2"), so.Agg("min"))
            .add(so.Dots(color="C2"), so.Agg("max"))
            .scale(
                x=so.Continuous().tick(every=1),
                color=so.Continuous().tick(at=history.index),
            )
        )
        line_plot.save(realpath(join(FPL_WRAP_DIR, str(self.entry_id), "line_plot.png")))

        rank_plot = (
            so.Plot(history, x="gameweek", y="overall_rank")
            .add(so.Lines(color="C1"))
            .scale(
                x=so.Continuous().tick(every=1),
                y=so.Continuous().label(like="{x:,}"),
                color=so.Continuous().tick(at=history.index),
            )
            .limit(y=(2_000_000, 0))
            .label(
                title="Overall rank versus gameweek",
            )
        )
        rank_plot.save(realpath(join(FPL_WRAP_DIR, str(self.entry_id), "rank_plot.png")))

    def create_report(self, fp, gw):
        self.captain = self.o_df["captain"].value_counts().to_dict()
        # self.chips = self.o_df['active_chip'].value_counts().to_dict()
        self.used_chips = self.f["active_chip"]

        def captain():
            self.captain = [(get_player(id=key), value) for key, value in self.captain.items()]
            # try to add total points gained, average per game
            # self.captain = sorted(self.captain, key = operator.itemgetter(2), reverse=True)
            return self.captain

        def promoted_vice():
            self.vice_to_cap = {}
            ben = {get_player(item): [] for item in set(self.o_df["vice_captain"])}

            for row in self.o_df.itertuples():
                if check_minutes(int(row.captain), row.gw)[0] == 0:
                    self.vice_to_cap[get_player(row.vice_captain)] = [get_player(row.captain)]
                    self.vice_to_cap[get_player(row.vice_captain)].append(
                        get_player_stats_from_db(row.vice_captain, row.gw)[0] * 2
                    )
                    ben[get_player(row.vice_captain)].append(gw)

            for key, values in ben.items():
                if key in self.vice_to_cap.keys():
                    self.vice_to_cap[key].append(len(values))

            self.vice_to_cap = [[key, values[1], values[2]] for key, values in self.vice_to_cap.items()]
            self.vice_to_cap = sorted(self.vice_to_cap, key=operator.itemgetter(1))
            return self.vice_to_cap

        def outliers():
            Q1, season_average, Q3 = get_basic_stats(self.o_df["total_points"])
            IQR = Q3 - Q1
            exceptional_df = self.o_df[self.o_df["total_points"] > Q3 + 1.5 * IQR]
            abysmal_df = self.o_df[self.o_df["total_points"] < Q1 - 1.5 * IQR]

            exceptional = []
            abysmal = []

            for i, j in zip(exceptional_df["gw"], exceptional_df["total_points"]):
                exceptional.append((i, j))

            for i, j in zip(abysmal_df["gw"], abysmal_df["total_points"]):
                abysmal.append((i, j))

            return {
                "exceptional": exceptional,
                "abysmal": abysmal,
                "season_average": season_average,
            }

        #
        def out_transfer_stats():
            counts = self.f["element_out"].value_counts().reset_index().to_dict("list")
            most_transf_out = [(counts["element_out"][i], get_player(counts["index"][i])) for i in range(3)]
            least_transf_out = [
                (counts["element_out"][-i], get_player(counts["index"][-i])) for i in range(1, 4)
            ]
            return {
                "most_transferred_out": most_transf_out,
                "least_transferred_out": least_transf_out,
            }

        def in_transfer_stats():
            """Output = {"most_transferred_in" : [], "least_transferred_in": []}"""

            counts = self.f["element_in"].value_counts().reset_index().to_dict("list")
            most_transf_in = [(counts["element_in"][i], get_player(counts["index"][i])) for i in range(3)]
            least_transf_in = [
                (counts["element_in"][-i], get_player(counts["index"][-i])) for i in range(1, 4)
            ]  # because -0 == 0
            return {
                "most_transferred_in": most_transf_in,
                "least_transferred_in": least_transf_in,
            }

        #
        def worst_transfer_in_week():
            """Output = {"worst_transfer_in":[()]}"""
            worst_transfer_in = []

            self.f = self.f.sort_values(by="delta", ascending=False)
            for i in range(1, 3):
                player_in = self.f.iloc[-i, :]["element_in"]
                player_out = self.f.iloc[-i, :]["element_out"]
                points_lost = int(self.f.iloc[-i, :]["delta"])
                gw = str(self.f.iloc[-i, :]["gw"])

                worst_transfer_in.append(
                    (
                        gw,
                        get_player(id=player_in),
                        get_player(id=player_out),
                        points_lost,
                    )
                )
            return {"worst_transfer_in": worst_transfer_in}

        def best_transfer_in_week():
            """Best Transfer of the week"""
            best_transfer_in = []

            self.f = self.f.sort_values(by="delta", ascending=False)
            print(self.f)
            for i in range(0, 3):
                player_in = self.f.iloc[i, :]["element_in"]
                player_out = self.f.iloc[i, :]["element_out"]
                points_gained = int(self.f.iloc[i, :]["delta"])
                gw = str(self.f.iloc[i, :]["gw"])

                best_transfer_in.append(
                    (
                        gw,
                        get_player(id=player_in),
                        get_player(id=player_out),
                        points_gained,
                    )
                )
            return {"best_transfer_in": best_transfer_in}

        def luckiest_week():
            """Points obtained from the bench"""
            lucky_week = []
            self.f = self.f.sort_values(by="auto_sub_in_points", ascending=False)
            for i in range(3):
                gw = str(self.f.iloc[i, :]["gw"])
                auto_sub_in = self.f.iloc[i, :]["auto_sub_in_player"]
                auto_sub_out = self.f.iloc[i, :]["auto_sub_out_player"]
                auto_sub_points = int(self.f.iloc[i, :]["auto_sub_in_points"])
                lucky_week.append(
                    (
                        gw,
                        get_player(id=auto_sub_in),
                        get_player(id=auto_sub_out),
                        auto_sub_points,
                    )
                )
            return {"lucky_week": lucky_week}

        def most_points_on_bench():
            """Most points on the bench"""
            self.f["points_on_bench"] = self.f["points_on_bench"].astype(int)
            self.f = self.f.sort_values(by="points_on_bench", ascending=False)
            most_points = []
            for i in range(3):
                gw = str(self.f.iloc[i, :]["gw"])
                player_on_bench = self.f.iloc[i, :]["bench"].split(",")
                point_player = {
                    get_player(id=i): get_player_stats_from_db(int(i), gw)[0] for i in player_on_bench
                }
                points_on_bench = int(self.f.iloc[i, :]["points_on_bench"])
                most_points.append((gw, point_player, points_on_bench))
            return {"most_points_on_bench": most_points}

        def highest_point() -> list:
            highest_point = self.f[self.f["total_points"] == max(self.f["total_points"])]
            highest_point = [
                (highest_point["gw"].tolist()[0]),
                highest_point["total_points"].tolist()[0],
            ]
            return {"highest_point": highest_point}

        def lowest_point() -> list:
            lowest_point = self.f[self.f["total_points"] == min(self.f["total_points"])]
            lowest_point = [
                (lowest_point["gw"].tolist()[0]),
                lowest_point["total_points"].tolist()[0],
            ]
            return {"lowest_point": lowest_point}

        self.captain = captain()
        self.vice_to_cap = promoted_vice()
        output = {
            "captain": self.captain,
            "promoted_vice": self.vice_to_cap,
            "used_chips": [x for x in self.used_chips.tolist() if x != None],
        }

        output.update(outliers())

        output.update(out_transfer_stats())
        output.update(in_transfer_stats())

        output.update(worst_transfer_in_week())  # does not consider hits
        output.update(best_transfer_in_week())

        output.update(most_points_on_bench())
        output.update(luckiest_week())

        output.update(highest_point())
        output.update(lowest_point())

        to_json(output, fp)


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

    test.create_report(
        f"{FPL_WRAP_DIR}/{str(args.entry_id)}/{str(args.entry_id)}_{str(args.gameweek)}.json",
        args.entry_id,
    )  # Move to S3
    test.plots_2()

    # all_gw_entries = [get_participant_entry(args.player_id, i) for i in range(args.gameweek)]
    # all_df = pd.DataFrame(all_gw_entries[1:])
    # all_df.fillna(value = 0, inplace= True)
    # all_df['gw'] = all_df['gw'].astype(int)
    # all_df['points_on_bench'] = all_df['points_on_bench'].astype(int)
    # all_df.fillna(value = 0, inplace= True)
    # all_df['gw'] = all_df['gw'].astype(int)
    # all_df['points_on_bench'] = all_df['points_on_bench'].astype(int)
