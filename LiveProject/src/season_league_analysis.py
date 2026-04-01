import requests
from src.urls import TRANSFER_URL
from src.utils import League, get_curr_event, LEAGUE_URL
import polars as pl
from functools import lru_cache
from src.db.update_season_fixture import update_season_fixture

# << Stratification by month >>
# << Most impressive rise >>

# Start with league average plot over 38 game weeks, like a simple line plot. ability to scrub through the season

# Most Impressive drop>>

# Who started well?
# Who ended well?
# Who is the steady eddy?

# Highest gameweek point ever,
# Lowest gameweek point
# Who took most hits?
# Who got more points from chips excluding Wildcard?

# Most captained in the league
# Participant with most captain points
# Participant with most blank captain points
# Participant with lucky/bench points

# Patterns in players transferred in (teams esp)

# Represent(some of these) with badges and explain the badges like a legend

@lru_cache(maxsize=10)
def get_league_data(league_id: int):
    try:
        f_df = pl.read_csv("test_data.csv")
    except :
        gw = get_curr_event()[0]
        df = []

        league = League(league_id=league_id)

        for gameweek in range(1, gw, 1):
            f = league.get_all_participant_entries(gameweek)
            temp_df = pl.DataFrame(f)
            df.append(temp_df)

        f_df = pl.concat(df, how = "vertical")
        f_df.write_csv("test_data.csv")
    return f_df

def get_fixture_data():
    """ Get fixture data """
    try:
        f_df = pl.read_csv("test_fixture_data.csv")
    except :
        f_df = update_season_fixture()
        f_df.to_csv("test_fixture_data.csv")

    return f_df
    

def get_transfer_data(league_id: int):
    """ Transfer data """

    gw = get_curr_event()[0]
    df = []

    league = League(league_id=league_id)
    league.obtain_league_participants()

    for i in range(2, gw, 1): # no transfers from gameweek one 
        f = league.get_gw_transfers(i)
        f = {str(key): value for key,value in f.items()}
        temp_df = pl.DataFrame(f, infer_schema_length=2).unpivot(variable_name="entry_id", value_name="transfers_in_out")
        
        temp_df = temp_df.with_columns(gameweek=gw)
        temp_df = temp_df.with_columns(element_in=pl.col("transfers_in_out").struct.field("element_in"))
        temp_df = temp_df.with_columns(element_out=pl.col("transfers_in_out").struct.field("element_out"))
        
        df.append(temp_df)
        f_df = pl.concat(df, how = "vertical")
        break
    
    return f_df

def analyse(league_id: int):
    df = get_league_data(league_id=league_id)
    # fixture_df = get_fixture_data()
    # transfer_df = get_transfer_data(league_id=league_id)

    # measures of dispersion
    # -- identifies difficult gameweeks and creates a mask
    test_df = df.group_by(pl.col("gw")).agg(pl.col("total_points").quantile(0.80)).sort("total_points")

    # best use of chips
    used_chip = df.select(pl.col("entry_id", "active_chip")).filter(pl.col("active_chip") != '')
    captain_chip = df.select(pl.col("entry_id", "captain", "vice_captain"))

    # starting 11 analysis
    start_df = df.select(pl.col("entry_id", "players"))

    # super sub
    sub_df = df.select(pl.col("entry_id", "auto_sub_in"))

    # total points df
    tp_df = df.select(pl.col("gw", "entry_id", "total_points")).filter(pl.col("total_points") == pl.col("total_points").max().over("gw"))

    # least transfer points cost
    hits_df = df.select("entry_id", "event_transfers_cost").group_by("entry_id").agg(pl.col("event_transfers_cost").sum())
    # calculate measures of dispersion over this

    # highest
    highest = df.filter(pl.col("total_points") == pl.col("total_points").max())

    # lowest
    lowest = df.filter(pl.col("total_points") == pl.col("total_points").min())

    # print(fixture_df)
    print(transfer_df)
    # This league is a Utd/City league based on the number of transfers? and players 



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="Season Report", description="Provider")

    parser.add_argument(
        "-l",
        "--league_id",
        type=int,
        required=True,
        help="ID of league you're interested in ",
    )
    args = parser.parse_args()
    analyse(args.league_id)