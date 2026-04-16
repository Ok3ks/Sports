from dataclasses import dataclass, asdict
import requests
from src.urls import TRANSFER_URL
from src.utils import League, get_curr_event
import polars as pl
from functools import lru_cache
from src.db.update_season_fixture import update_season_fixture
from src.db.db import get_fixture_gameweek, get_player_stats_from_db_gql, get_player, get_player_gql, get_player_info, get_player_team_map, get_fixtures, get_teams
import pprint

# --- Individual
# stories : 

## Transfers 
# we noticed you never saved a transfer which means you were unable to 
# fully pivot your team to take advantage of fixture swings.
# immediate points lost to transfers
# future points lost to transfers

# Midweek deadlines are rife with sudden benching/rotations, and the unexpected
# how did you fare?

# If you prioritised players who earned bonus points, and defCons like steady eddies
# your season could have been better, it's more bank for your buck


## Trends in transfers
# Overall you maintained the same {pool} of players, chopping and changing, you lost points
# due to this, you could have held on to certain players, and you would have had a better season
# longest serving player contrasted with shortest stint 


## Your use of chips 
#  Yes, using chips. Is it luck or is it skill. If it's luck, better luck next season


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


@dataclass(frozen=True, order=True)
class Fixture:
    home_difficulty: int | None
    away_difficulty: int | None
    home: str | None
    away: str | None
    home_goals: float | None
    away_goals: float | None
    code: int | None
    gameweek: int | None
    finished: bool | None
    date: str | None



class Player:
    """This class represents a premier league player"""

    def __init__(self, player_id, gw):
        self.gw = gw
        self.player_id: str = player_id
        self._team = None
        self._position = None
        self._player_name = None

    def _gameweek_score(self):
        obj = get_player_stats_from_db_gql(self.player_id, self.gw)
        return obj


    def _fixture(self):
        if not self.team:
            self._player_info()
        return get_fixture_gameweek(self._team, self.gw)  # can return Fixture dataclass


    def _player_info(self):
        half = 1
        if self.gw >= 19:
            half = 2
        obj = get_player_info(self.player_id, half) # can return Team dataclass
        
        self._team = obj[0].team
        self._position = obj[0].position
        self._player_name = obj[0].player_name    
        return obj

    @property
    def gameweek_score(self):
        return self._gameweek_score()
    
    @property
    def fixture(self):
        fixtures = self._fixture()
        return [Fixture(*fixture) for fixture in fixtures] if fixtures else None
    
    @property
    def team(self):
        if not self._team: 
            self._player_info()        
        return self._team
    
    @property
    def position(self):
        if not self._position: 
            self._player_info()
        return self._position
    
    @property
    def player_name(self):
        if not self._player_name: 
            self._player_info()
        return self._player_name


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
    f = league.get_all_gw_transfers() ## TODO: update to use all_
    
    df = pl.DataFrame(f, infer_schema_length=True)
    df = df.rename({
        "entry": "entry_id",
        "event": "gw",
        "time": "transfer_time"
    })
    df = expand_date(df, date_col="transfer_time")

    print("--transfer df---")
    df_details(df)
    
    return df

def expand_date(df: pl.DataFrame, date_col: str):
        """
        
        Takes in a polars Dataframe with a str col - date
        and expands into month,day,weekday,time,year.
        
        """
        df = df.with_columns(
            pl.col(date_col).cast(pl.Datetime).dt.month().alias("month"),
            pl.col(date_col).cast(pl.Datetime).dt.day().alias("day"),
            pl.col(date_col).cast(pl.Datetime).dt.weekday().alias("weekday"),
            pl.col(date_col).cast(pl.Datetime).dt.time().alias("time"),
            pl.col(date_col).cast(pl.Datetime).dt.year().alias("year")
        )
        return df

def fixture_mapping(player, gw):
    fixtures = Player(player, gw).fixture
    return [asdict(f) for f in fixtures] if fixtures else []


def story_1(entry_id: int, df: pl.DataFrame):
    """
    Input is an entry, temporarily using an input of dataframes which will be removed

    Your preferred formation of xxx means you bench yyy, and zzz is your first sub
    (Maybe It's not your preferred formation, it's your worry of ownership,
    who is being started despite poor performance not formation)
    this made you lose vwx compared to, and gain yza compared to .

    """

    df = df.filter(pl.col("entry_id") == 1313244)
    df = df.with_columns(
        pl.col("players").str.split(",").
        list.to_struct(fields=[
            "player_1", "player_2", "player_3", "player_4",
            "player_5", "player_6", "player_7", "player_8",
            "player_9", "player_10", "player_11"
            ])
    ).unnest("players")

    player_cols = [
            "player_1", "player_2", "player_3", "player_4",
            "player_5", "player_6", "player_7", "player_8",
            "player_9", "player_10", "player_11"
        ]

    df = df.with_columns(
        pl.concat_list([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).position,
            return_dtype=pl.String
        )
        for col in player_cols
    ]).alias("player_positions"))


    df = df.with_columns(
        pl.col("bench").str.split(",")
        .list.to_struct(fields=["bench_1", "bench_2", "bench_3", "bench_4"])  # modularize
        ).unnest("bench")
    
    df = df.with_columns(pl.col("active_chip").fill_null("reg"))

    bench_cols = ["bench_1", "bench_2", "bench_3", "bench_4"]
    df = df.filter(pl.col("active_chip") != "bboost").with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).team,
            return_dtype=pl.String
        )
        .alias(f"{col}_team")
        for col in bench_cols
    ])

    df = df.with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: fixture_mapping(row[c], row["gw"]),
            return_dtype=pl.Struct({
                "home_difficulty": pl.Int64,
                "away_difficulty": pl.Int64,
                "home": pl.String, 
                "away": pl.String,
                "home_goals": pl.Float64,
                "away_goals": pl.Float64,
                "code": pl.Int64,
                "gameweek": pl.Float64,
                "finished": pl.Int64,
                "date": pl.String
            })
        )
        .alias(f"{col}_fixture")
        for col in bench_cols
    ])

    return df

def enrich_player_cols(df: pl.DataFrame, interested_cols: list[str]):
    """

        Function to enrich player columns with information from the Player 
        object. Including player_name, team, fixture, gameweek_score

        df: Original dataframe,
        interested_cols: A list of column names to transfer

        First filters null objects then transforms the column.
    
    """

    if len(interested_cols) < 1:
        raise ValueError("Add an interested column to get started")


    if not all(col in df.columns for col in interested_cols):
        missing = [col for col in interested_cols if col not in df.columns]
        raise ValueError(f"Missing columns: {missing}")


    t_df = df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).team,
            return_dtype=pl.String
        )
        .alias(f"{col}_team")
        for col in interested_cols
    ])

    t_df = t_df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).position,
            return_dtype=pl.String
        )
        .alias(f"{col}_position")
        for col in interested_cols
    ])

    t_df = t_df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).player_name,
            return_dtype=pl.String
        )
        .alias(f"{col}_player_name")
        for col in interested_cols
    ])

    t_df = t_df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).gameweek_score.total_points,
            return_dtype=pl.Int64
        )
        .alias(f"{col}_gameweek_score")
        for col in interested_cols
    ])

    t_df = t_df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw")
        .map_elements(
            lambda row, c=col: Player(row[c], row["gw"]).gameweek_score.minutes,
            return_dtype=pl.Int64
        )
        .alias(f"{col}_minutes")
        for col in interested_cols
    ])
    
    t_df = t_df.filter(pl.col(interested_cols[0]).is_not_null()).with_columns([
        pl.struct(col, "gw").map_elements(
            lambda row, c=col: fixture_mapping(row[c], row["gw"]),
            return_dtype=pl.List(pl.Struct({
                "home_difficulty": pl.Int64,
                "away_difficulty": pl.Int64,
                "home": pl.String, 
                "away": pl.String,
                "home_goals": pl.Float64,
                "away_goals": pl.Float64,
                "code": pl.Int64,
                "gameweek": pl.Float64,
                "finished": pl.Int64,
                "date": pl.String
            }))
        ).alias(f"{col}_fixture")
        for col in interested_cols])
    
    print(df_details(t_df))
    
    return t_df

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

    transfer_df, df, _ = analyse(1491605) # entry is league id
    transfer_df = transfer_df.with_columns(
        pl.col("entry_id").cast(pl.Int32)
    )
    df = df.with_columns(
        pl.col("entry_id").cast(pl.Int32)
        )
    df = df.join(transfer_df, how="left", on=["entry_id", "gw"])

    #TODO: spot deadteams DEAD_TEAM_THRESHOLD = 12
    #find early transfers -- use deadline time

    df = df.filter(pl.col("entry_id") == entry_id)

    # print(df.select("active_chip").unique())
    # print("----")

    # enrich transfer objs with results from transfers
    t_df = enrich_player_cols(df, ["element_in", "element_out"]) # element_in, element_out are a pair
    t_df = t_df.with_columns(
        transfer_point_delta = pl.col("element_in_gameweek_score") - pl.col("element_out_gameweek_score")
    )

    # enrich captain objs with results from transfers
    c_df = enrich_player_cols(df, ["captain", "vice_captain"]) # order matters because captain can be null when absent from a gameweek

    # factor in triple captain
    c_df = c_df.with_columns(
        pl.when(
            pl.col("captain_minutes") == 0
        ).then(
            pl.col("vice_captain_gameweek_score")*2
            ).otherwise(pl.col("captain_gameweek_score")*2).alias(
                "final_captain_gameweek_score"
            ))


    metrics = {
        "n_transfers": t_df.count().select("element_in").item(), # no chips included
        "transfer_points_gained": t_df.select("transfer_point_delta").sum().item(), # including wildcard,freehit
            #dive deeper, you gained max --- points with this transfer
        "points_gained_with_wildcard": t_df.filter(pl.col("active_chip") == "wildcard").select(["transfer_point_delta", "gw"]).group_by("gw").sum().to_dicts(),
        "points_gained_with_freehit": t_df.filter(pl.col("active_chip") == "freehit").select(["transfer_point_delta", "gw"]).group_by("gw").sum().to_dicts(), #freehit one or two
        "transfer_activity": {
            # aggregate sum, count
            "negative_transfer": t_df.filter(pl.col("transfer_point_delta") < 0).select(["element_out", "element_in", "element_in_player_name", "element_in_fixture",  "element_out_player_name", "element_out_team", "transfer_point_delta", "element_out_fixture"]).to_dicts(), # transfers that should have been delayed
            "positive_transfer": t_df.filter(pl.col("transfer_point_delta") > 0).select(["element_out", "element_in", "element_in_player_name", "element_in_fixture",  "element_out_player_name", "element_out_team", "transfer_point_delta", "element_out_fixture"]).to_dicts()
        },
        "points_gained_from_captains": c_df.filter(
                                                    (pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null())).select(
                                                    ["gw", "final_captain_gameweek_score", "active_chip", "captain_player_name", "vice_captain_player_name", "captain_minutes", "vice_captain_minutes"]).unique(
                                                        "gw"), # group by players,
        "points_gained_from_3xc": c_df.filter(
                                                        pl.col("active_chip") == "3xc").select(
                                                            ["gw", "final_captain_gameweek_score", "captain_player_name", "vice_captain_player_name", "captain_minutes", "vice_captain_minutes"]).unique(
                                                                "gw"),
    }

    print("----")
    print(metrics)

    # print("------")
    # print(df_details(t_df))

    return metrics



def df_details(df):
    print(f"shape: {df.shape}")
    print(f"columns: {df.collect_schema()}")

def analyse(league_id: int):
    """ League analysis. """
    df = get_league_data(league_id=league_id)
    transfer_df = get_transfer_data(league_id=league_id)
    fixture_df = get_fixture_data()

    fixture_df = fixture_df.filter(pl.col("date").is_not_null()).with_columns(
        pl.col("gameweek").cast(pl.Int64)
        ).rename({"gameweek": "gw"})
    

    gw_deadline_time = fixture_df.select("gw", "date").unique("gw",keep="first")
    gw_end_time = fixture_df.select("gw", "date").unique("gw",keep="last")

    df = df.join(gw_deadline_time, on="gw", how="left")
    df = expand_date(df, date_col="date")

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

    # print(transfer_df)
    # This league is a Utd/City league based on the number of transfers? and players 

    # df.join().select(pl.col("gameweek").alias("gw")), on="gw")
    # using player information for analysis

    # which position is the most benched apart from goalkeepers?
    # ties into the preferred formation

    return transfer_df, df, fixture_df
    
    
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
        story_2(args.entry_id)

    ## unable to map into another data type with polars , you need to do in the rust side
    ## strongly discourages doing anything in python, especially lambdas, there are idiomatic expressions for this
    ## you can get away with this by returning dictionaries and the return types.
    ## unable to save structs into json from polars..

    #learning prefering iter_slices #difference between to_dict and to_dicts
    # different behaviour when != value in list, it excludes nulls except one uses _ne 
    #       #i.e pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null()) is the same as  pl.col("active_chip").ne_missing("3xc")
    # data tests are important