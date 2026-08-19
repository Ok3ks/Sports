import json
import pandas as pd
from src.utils import (
    Participant,
    bench_transform,
    enrich_player_cols,
    expand_date,
    get_fixture_data,
)
from functools import lru_cache
import numpy as np
import polars as pl
from src.db.update_season_fixture import update_season_fixture
from src.db.db import (
    get_player_gql,
)

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
    async def weekly_score_transformation(self):
        """Transforms weekly score into Dataframe, and returns weekly dataframe"""

        one_df = pd.DataFrame(await self.get_all_week_entries(gw=self.gw, all=True))
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
        ].apply(np.argmax)

        self.o_df["captain_points"] = [
            get_ind_player_stats_from_db(self.o_df["captain"][event - 1], event) * 2
            for event in range(1, self.gw + 1)
        ]
        self.o_df["vice_captain_points"] = [
            get_ind_player_stats_from_db(self.o_df["vice_captain"][event - 1], event)
            for event in range(1, self.gw + 1)
        ]

        self.o_df.rename(columns={"entry": "entry_id"}, inplace=True)
        return self.o_df

    @lru_cache
    async def merge_league_weekly_transfer(self):
        """Merges Weekly score dataframe with transfers dataframe"""
        self.transfers = self.get_all_week_transfers()
        transfer_weeks = set(self.transfers.keys())
        all_weeks = set(range(1, self.gw + 1))

        # weeks transfers were not made
        diff = all_weeks.difference(transfer_weeks)

        for element in diff:
            self.transfers.update({element: {"element_in": [], "element_out": []}})

        self.f = pd.DataFrame(self.transfers)
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
        self.f["auto_sub_in_points"] = [
            sum(
                i
                for i in [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["auto_sub_in"][event - 1].strip().split(",")
                ]
                if isinstance(i, int)
            )
            for event in range(1, self.gw + 1)
        ]
        self.f["auto_sub_out_points"] = [
            sum(
                i
                for i in [
                    get_ind_player_stats_from_db(y, event)
                    for y in self.f["auto_sub_out"][event - 1].split(",")
                ]
                if isinstance(i, int)
            )
            for event in range(1, self.gw + 1)
        ]

    def prep_for_gql(self):
        """Utility function which modifies entry for GraphQL"""
        self.output = self.o_df.to_dict("list")
        for key, value in self.output.items():
            if key in ["captain", "vice_captain", "highest_scoring_player"]:
                self.output[key] = [
                    get_player_gql(id=player_id, gameweek=gameweek + 1, session=session)
                    for gameweek, player_id in enumerate(value)
                ]

    async def participant_stats(self):
        """Season Statistics for a participant"""

        metrics = {}
        self.transfers = (
            await self.get_all_week_transfers()
            if self.transfers is None
            else self.transfers
        )
        entries = await self.get_all_week_entries(1, all=True)

        df = pl.DataFrame(entries)
        df = df.with_columns(pl.col("entry_id").cast(pl.Int32))

        transfer_df = pl.DataFrame(self.transfers)
        transfer_df = transfer_df.with_columns(pl.lit(self.entry_id).alias("entry_id"))
        transfer_df = transfer_df.rename({"event": "gw", "time": "transfer_time"})
        transfer_df = expand_date(transfer_df, date_col="transfer_time")
        transfer_df = transfer_df.with_columns(pl.col("entry_id").cast(pl.Int32))

        fixture_df = get_fixture_data()
        fixture_df = (
            fixture_df.filter(pl.col("date").is_not_null())
            .with_columns(
                pl.col("gameweek").cast(
                    pl.Int64,
                )
            )
            .rename({"gameweek": "gw"})
        )

        df = df.join(transfer_df, how="left", on=["entry_id", "gw"])

        gw_deadline_time = fixture_df.select("gw", "date").unique("gw", keep="first")
        df = df.join(gw_deadline_time, on="gw", how="left")
        df = expand_date(df, date_col="date")

        gw_deadline_time = fixture_df.select("gw", "date").unique("gw", keep="first")
        df = df.join(gw_deadline_time, on="gw", how="left")

        # TODO: spot deadteams DEAD_TEAM_THRESHOLD = 12
        # find early transfers -- use deadline time

        # fills null active_chip with a value which corresponds to a normal gameweek
        # chips are '3xc', 'freehit', 'wildcard', 'bboost'
        df = df.with_columns(pl.col("active_chip").fill_null("norm"))

        # enrich transfer objs with results from transfers
        t_df = df.filter(pl.col("element_in").is_not_null())
        n_t_df = df.filter(pl.col("element_in").is_null())

        t_df = enrich_player_cols(
            t_df,
            ["element_in", "element_out"],
            attributes=["gameweek_score", "team", "fixture", "player_name"],
        )  # element_in, element_out are a pair
        t_df = t_df.with_columns(
            transfer_point_delta=pl.col("element_in_gameweek_score")
            - pl.col("element_out_gameweek_score")
        )

        # recombines df after transformation
        df = pl.concat([t_df, n_t_df], how="diagonal")
        assert t_df.shape[0] + n_t_df.shape[0] == df.shape[0]

        # enrich_auto_sub
        b_df = bench_transform(df)

        # captain results
        # enrich captain objs with results from transfers
        c_df = enrich_player_cols(
            df, ["captain", "vice_captain"]
        )  # order matters because captain can be null when absent from a gameweek

        c_df = c_df.with_columns(
            ## filters for rows without triple captain
            pl.when(
                (pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null())
            )
            .then(
                pl.when(pl.col("captain_minutes") == 0)
                .then(pl.col("vice_captain_gameweek_score") * 2)
                .otherwise(pl.col("captain_gameweek_score") * 2)
                .alias("final_captain_gameweek_score")
            )
            .otherwise(
                ## filters for rows with triple captain
                pl.when(pl.col("captain_minutes") == 0)
                .then(pl.col("vice_captain_gameweek_score") * 3)
                .otherwise(pl.col("captain_gameweek_score") * 3)
                .alias("final_captain_gameweek_score")
            )
        )
        history = self.get_history()
        metrics = {
            "rank": history["current"],
            "total_points_gained": df.unique("gw")
            .select(["total_points", "gw"])
            .to_dicts(),
            "n_transfers": df.filter(
                ~pl.col("active_chip").is_in(["wildcard", "freehit"])
            )
            .filter(pl.col("transfer_point_delta").is_not_null())
            .count()
            .select("element_in")
            .item(),  # no chips included
            "transfer_points_gained": {
                "freehit": df.filter(pl.col("active_chip") == "freehit")
                .select("transfer_point_delta", "gw")
                .group_by("gw")
                .sum()
                .to_dicts(),
                "transfers": t_df.filter(
                    ~pl.col("active_chip").is_in(["wildcard", "freehit"])
                )
                .select("gw", "transfer_point_delta")
                .to_dicts(),
                "wildcard": df.filter(pl.col("active_chip") == "wildcard")
                .select("transfer_point_delta", "gw")
                .group_by("gw")
                .sum()
                .to_dicts(),
                "bboost": df.filter(pl.col("active_chip") == "bboost")
                .select("transfer_point_delta", "gw")
                .group_by("gw")
                .sum()
                .to_dicts(),
                "max": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"]))
                .select(pl.col("transfer_point_delta", "gw"))
                .max()
                .to_dicts(),
                "min": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"]))
                .select(pl.col("transfer_point_delta", "gw"))
                .min()
                .to_dicts(),
                "triple_cap": c_df.filter(pl.col("active_chip") == "3xc")
                .select(
                    [
                        "transfer_point_delta",
                        "gw",
                        "final_captain_gameweek_score",
                        "captain_gameweek_score",
                        "captain_fixture",
                        "vice_captain_fixture",
                        "captain_player_name",
                        "vice_captain_player_name",
                        "vice_captain_gameweek_score",
                        "captain_minutes",
                        "vice_captain_minutes",
                    ]
                )
                .to_dicts(),
            },
            "captain_points": c_df.filter(
                (pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null())
            )
            .select(
                [
                    "gw",
                    "final_captain_gameweek_score",
                    "captain_fixture",
                    "vice_captain_fixture",
                    "active_chip",
                    "captain_player_name",
                    "vice_captain_player_name",
                    "captain_gameweek_score",
                    "vice_captain_gameweek_score",
                    "captain_minutes",
                    "vice_captain_minutes",
                ]
            )
            .unique("gw")
            .to_dicts(),  # group by players,
        }
        return metrics

    def create_report(self, display=False):

        if display:
            print(self.output)
        else:
            return self.output


async def main():
    import argparse

    curr_gw = await get_curr_event()
    parser = argparse.ArgumentParser(prog="FplWrap", description="Provider")
    parser.add_argument(
        "-g",
        "--gameweek",
        type=int,
        default=curr_gw[0] if curr_gw else 2,
        help="Gameweek you are trying to get a report of",
    )
    parser.add_argument(
        "-e",
        "--entry_id",
        type=int,
        required=True,
        help="ID of player you're interested in ",
    )
    args = parser.parse_args()
    if args:
        test = ParticipantReport(args.gameweek, args.entry_id)
        await test.weekly_score_transformation()
        await test.merge_league_weekly_transfer()
        test.add_auto_sub()
        await test.participant_stats()


if __name__ == "__main__":
    import anyio

    anyio.run(main)
