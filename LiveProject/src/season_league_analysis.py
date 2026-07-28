from dataclasses import dataclass, asdict
from src.urls import TRANSFER_URL
from src.utils import (
    bench_transform,
    enrich_player_cols,
    expand_date,
    get_curr_event,
    get_fixture_data,
    get_league_data,
    get_transfer_data,
    player_transform,
)
import polars as pl
from functools import lru_cache
import pprint

# --- Individual
# Also analyse season as a whole

# stories :

## Your use of chips
#  Yes, using chips. Is it luck or is it skill. If it's luck, better luck next season

# Midweek deadlines are rife with sudden benching/rotations, and the unexpected
# how did you fare? -- # use fixture df


## Transfers
# we noticed you never saved a transfer which means you were unable to
# fully pivot your team to take advantage of fixture swings.
# immediate points lost to transfers
# future points lost to transfers

## Trends in transfers/formation

# If you prioritised players who earned bonus points, and defCons like steady eddies
# your season could have been better, it's more bank for your buck or position wise

# Overall you maintained the same {pool} of players, chopping and changing, you lost points
# due to this, you could have held on to certain players, and you would have had a better season
# longest serving player contrasted with shortest stint


# Represent(some of these) with badges and explain the badges like a legend?


# ---- For me to share with the league

# --- visible on a plot
# Who started well?
# Who ended well?
# Who is the steady eddy?

# Highest gameweek point ever, ( league average )
# Lowest gameweek point
# Who took most hits?
# Who got more points from chips excluding Wildcard?

# Most captained in the league
# Participant with most captain points
# Participant with most blank captain points
# Participant with lucky/bench points

# << Stratification by month >>
# << Most impressive rise >>

# Start with league average plot over 38 game weeks, like a simple line plot. ability to scrub through the season
# Most Impressive drop>>


def story_2(entry_id: int):
    """

    ## Transfers
    # we noticed you never saved a transfer which means you were unable to
    # fully pivot your team to take advantage of fixture swings.
    # immediate points lost to transfers
    # future points lost to transfers

    args:
        - entry id to assess with.

    """

    metrics = {}

    transfer_df, df, _ = analyse(1491605)  # entry is league id
    transfer_df = transfer_df.with_columns(pl.col("entry_id").cast(pl.Int32))
    df = df.with_columns(pl.col("entry_id").cast(pl.Int32))
    df = df.join(transfer_df, how="left", on=["entry_id", "gw"])

    # TODO: spot deadteams DEAD_TEAM_THRESHOLD = 12
    # find early transfers -- use deadline time

    # point of difference with fpl wrap
    df = df.filter(pl.col("entry_id") == entry_id)

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
        pl.when((pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null()))
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

    # # weeks of saved transfers
    # print(df.select(pl.col("auto_sub_in").value_counts()))

    # # weeks where individual took hits
    # print(df.filter(pl.col("event_transfers_cost") > 0).select("gw").to_dict(as_series=False))

    # # you could have # exclude gameweek 1
    # print(df.filter(pl.col("element_in").is_null()).select("gw").to_dict(as_series=False))
    # # analyse df§

    # # weeks of chip usage which excludes transfers
    # print(df.filter(pl.col("active_chip").is_in(["freehit", "wildcard"])).unique("gw").select("gw").to_dict(as_series=False))

    # # weeks of unsaved transfers
    # print(df.filter(pl.col("element_in").is_not_null()).select("gw").unique("gw").to_dict(as_series=False))

    # # 100-point gameweek
    # print(df.filter(pl.col("total_points") > 100))

    # lucky weeks
    # your 13th player
    #

    metrics = {
        "total_points_gained": df.unique("gw")
        .select(["total_points", "gw"])
        .to_dicts(),
        "n_transfers": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"]))
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


def df_details(df):
    print(f"shape: {df.shape}")
    print(f"columns: {df.collect_schema()}")


def analyse(league_id: int):
    """League analysis."""
    df = get_league_data(league_id=1491605)
    transfer_df = get_transfer_data(league_id=1491605)
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

    gw_deadline_time = fixture_df.select("gw", "date").unique("gw", keep="first")

    df = df.join(gw_deadline_time, on="gw", how="left")
    df = expand_date(df, date_col="date")

    # measures of dispersion
    # -- identifies difficult gameweeks and creates a mask
    # test_df = df.group_by(pl.col("gw")).agg(pl.col("total_points").quantile(0.80)).sort("total_points")

    # # best use of chips
    # used_chip = df.select(pl.col("entry_id", "active_chip")).filter(pl.col("active_chip") != '')
    # captain_chip = df.select(pl.col("entry_id", "captain", "vice_captain"))

    # # starting 11 analysis
    # start_df = df.select(pl.col("entry_id", "players"))

    # # super sub
    # sub_df = df.select(pl.col("entry_id", "auto_sub_in"))

    # # total points df
    # tp_df = df.select(pl.col("gw", "entry_id", "total_points")).filter(pl.col("total_points") == pl.col("total_points").max().over("gw"))

    # # least transfer points cost
    # hits_df = df.select("entry_id", "event_transfers_cost").group_by("entry_id").agg(pl.col("event_transfers_cost").sum())
    # # calculate measures of dispersion over this

    # # highest
    # highest = df.filter(pl.col("total_points") == pl.col("total_points").max())

    # # lowest
    # lowest = df.filter(pl.col("total_points") == pl.col("total_points").min())

    # This league is a Utd/City league based on the number of transfers? and players

    # df.join().select(pl.col("gameweek").alias("gw")), on="gw")
    # using player information for analysis

    # which position is the most benched apart from goalkeepers?
    # ties into the preferred formation

    return transfer_df, df, fixture_df


def story_1(entry_id):
    """
    Key Outputs, a vertical p_df and u_p_df which is grouped by gameweek into a list
    """

    # troll of the season
    # relies on the number of occurence, when as vice-captain , point-delta > captain
    # when as captain point-delta < vice-captain
    # when on the bench, scores points, when starting

    # missing out hauls on players you owned for long periods (at least 10 weeks) ?
    # hauls of highest scoring players? and which you owned for which periods

    # like a grid map [1, 2, 3, 4, 5 ]

    # list of players
    # list players and their season points
    # players and points individual gained from them
    # find trolls, find solid buys, infer patterns

    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="Season Report", description="Provider")
    parser.add_argument(
        "-l",
        "--league_id",
        type=int,
        required=False,
        help="ID of league you're interested in ",
    )

    parser.add_argument(
        "-e",
        "--entry_id",
        type=int,
        required=True,
        help="ID of individual you're interested in ",
    )

    args = parser.parse_args()
    if args.entry_id:
        metrics = story_2(args.entry_id)
        print(metrics)

    ## unable to map into another data type with polars , you need to do in the rust side
    ## strongly discourages doing anything in python, especially lambdas, there are idiomatic expressions for this
    ## you can get away with this by returning dictionaries and the return types.
    ## unable to save structs into json from polars..

    # learning prefering iter_slices #difference between to_dict and to_dicts
    # different behaviour when != value in list, it excludes nulls except one uses _ne
    #       #i.e pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null()) is the same as  pl.col("active_chip").ne_missing("3xc")
    # data tests are important

    # issues with map_elements and nulls, not skipping nulls as defined
    # SQLAlchemy caching working against me because of the same specified is, player_id.
    #  it returns the same value despite different gameweek - diagnosed to be due to sqlalchemy data mapper
    # resorted to default sql statement
