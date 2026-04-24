from dataclasses import dataclass, asdict
import requests
from src.urls import TRANSFER_URL
from src.utils import League, get_curr_event
import polars as pl
from functools import lru_cache
from src.db.update_season_fixture import update_season_fixture
from src.db.db import get_fixture_gameweek, get_player_season_points, get_player_stats_from_db_gql, get_player, get_player_gql, get_player_info, get_player_team_map, get_fixtures, get_season_stats, get_teams
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
        if isinstance(self.gw, list):
            # obj = get_player_stats_from_db_gql(self.player_id, self.gw)
            obj = [get_player_stats_from_db_gql(self.player_id, f) for f in self.gw]
        else:
            obj = get_player_stats_from_db_gql(self.player_id, self.gw)
        
        return obj

    def _fixture(self):

        if not self.team:
            self._player_info()
        
        def _select_team(gw:int):
            return  self._team[0] if gw < 18 else self._team[1]
            
        if isinstance(self.gw, list):
            return [get_fixture_gameweek(_select_team(gw), gw) for gw in self.gw]
        
        return get_fixture_gameweek(_select_team(self.gw), self.gw)  # can return Fixture dataclass


    def _player_info(self):
        """Player Info"""
        
        obj = get_player_info(self.player_id) # can return Team dataclass
        
        self._team = [r[0].team for r in obj]
        self._position = obj[0][0].position
        self._player_name = obj[0][0].player_name    
        return obj
    

    def _season_score(self):
        obj = get_player_season_points(self.player_id)
        return obj


    @property
    def gameweek_score(self):
        return self._gameweek_score()
    
    @property
    def total_points(self):
        if isinstance(self.gw, list):
            return [obj.total_points for obj in self._gameweek_score()]
        else:
            return self._gameweek_score().total_points
    
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
    
    @property
    def season_score(self):
        return self._season_score()


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


def player_transform(df: pl.DataFrame, vertical=False):
    """

    """

    player_cols = [f"player_{i}" for i in range(1, 11)]

    if vertical:
        df =  df.with_columns(
        pl.col("players").str.split(",")
        ).explode("players")
    else: 
        df = df.with_columns(
            pl.col("players").str.split(",").
            list.to_struct(fields=player_cols)
        ).unnest("players")

    return df

def bench_transform(df: pl.DataFrame):

    bench_cols = [f"player_{i}" for i in range(1, 4)]

    df = df.with_columns(
        pl.col("bench").str.split(",")
        .list.to_struct(fields=bench_cols)  # modularize
        ).unnest("bench")

    b_df = df.filter(pl.col("active_chip") != "bboost")

    # b_df = enrich_player_cols(b_df, bench_cols)


    return b_df

def enrich_player_cols(df: pl.DataFrame, interested_cols: list[str], attributes:list| None=None):
    """

        Function to enrich player columns with information from the Player 
        object. Including player_name, team, fixture, gameweek_score

        df: Original dataframe,
        interested_cols: A list of column names to transfer

        First filters null objects then transforms the column.
        Returns filtered dataframe, and df contains nulls for selected columns
    
    """

    if not attributes:
        attributes = [ "team", "position", "player_name", "gameweek_score", "minutes", "fixture"]
    if len(interested_cols) < 1:
        raise ValueError("Add an interested column to get started")


    if not all(col in df.columns for col in interested_cols):
        missing = [col for col in interested_cols if col not in df.columns]
        raise ValueError(f"Missing columns: {missing}")

    # Replaces empty string with None

    t_df =  df.with_columns(
            pl.when(pl.col(pl.String) == "")
            .then(pl.lit(None))
            .otherwise(pl.col(pl.String))
            .name.keep()
            )

    if "team" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw")
            .map_elements(
                lambda row, c=col: Player(row[c], row["gw"]).team,
                return_dtype=pl.List(pl.String)
            )
            .alias(f"{col}_team")
            for col in interested_cols
        ])

    if "position" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw")
            .map_elements(
                lambda row, c=col: Player(row[c], row["gw"]).position,
                return_dtype=pl.String
            )
            .alias(f"{col}_position")
            for col in interested_cols
        ])

    if "player_name" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw")
            .map_elements(
                lambda row, c=col: Player(row[c], row["gw"]).player_name,
                return_dtype=pl.String
            )
            .alias(f"{col}_player_name")
            for col in interested_cols
        ])

    if "gameweek_score" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw")
            .map_elements(
                lambda row, c=col: Player(row[c], row["gw"]).gameweek_score.total_points,
                return_dtype=pl.Int64,
            )
            .alias(f"{col}_gameweek_score")
            for col in interested_cols
        ])

    if "minutes" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw")
            .map_elements(
                lambda row, c=col: Player(row[c], row["gw"]).gameweek_score.minutes,
                return_dtype=pl.Int64,
            )
            .alias(f"{col}_minutes")
            for col in interested_cols
        ])
    
    if "fixture" in attributes:
        t_df = t_df.with_columns([
            pl.struct(col, "gw").map_elements(
                lambda row, c=col: fixture_mapping(row[c], row["gw"]),
                return_dtype=pl.List(pl.Struct({
                    "home_difficulty": pl.Int64,
                    "away_difficulty": pl.Int64,
                    "home": pl.String, 
                    "away": pl.String,
                    "home_goals": pl.Int64,
                    "away_goals": pl.Int64,
                    "code": pl.Int64,
                    "gameweek": pl.Int64,
                    "finished": pl.Boolean,
                    "date": pl.Datetime
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
    
    # fills null active_chip with a value which corresponds to a normal gameweek
    #chips are '3xc', 'freehit', 'wildcard', 'bboost'
    df = df.with_columns(pl.col("active_chip").fill_null("norm"))

    # enrich transfer objs with results from transfers
    t_df = df.filter(pl.col("element_in").is_not_null())
    n_t_df = df.filter(pl.col("element_in").is_null())

    t_df = enrich_player_cols(t_df, ["element_in", "element_out"]) # element_in, element_out are a pair
    t_df = t_df.with_columns(
        transfer_point_delta = pl.col("element_in_gameweek_score") - pl.col("element_out_gameweek_score")
    )

    # recombines df after transformation
    df = pl.concat([t_df, n_t_df], how="diagonal")
    assert t_df.shape[0] + n_t_df.shape[0] == df.shape[0]

    # enrich_auto_sub
    b_df = bench_transform(df)

    # captain results
    # enrich captain objs with results from transfers
    c_df = enrich_player_cols(df, ["captain", "vice_captain"]) # order matters because captain can be null when absent from a gameweek

    c_df = c_df.with_columns(
        ## filters for rows without triple captain
        pl.when(
            (pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null())).then(
            pl.when(
                pl.col("captain_minutes") == 0
            ).then(
                pl.col("vice_captain_gameweek_score")*2
                ).otherwise(pl.col("captain_gameweek_score")*2).alias(
                    "final_captain_gameweek_score"
                )
            )
        .otherwise(
            ## filters for rows with triple captain
                    pl.when(
                        pl.col("captain_minutes") == 0
                    ).then(
                        pl.col("vice_captain_gameweek_score")*3
                        ).otherwise(pl.col("captain_gameweek_score")*3).alias(
                            "final_captain_gameweek_score"
                        )
                ))


    # weeks of saved transfers
    print(df.select(pl.col("auto_sub_in").value_counts()))

    # weeks where individual took hits
    print(df.filter(pl.col("event_transfers_cost") > 0).select("gw").to_dict(as_series=False))

    # you could have # exclude gameweek 1
    print(df.filter(pl.col("element_in").is_null()).select("gw").to_dict(as_series=False))
    # analyse df§

    # weeks of chip usage which excludes transfers    
    print(df.filter(pl.col("active_chip").is_in(["freehit", "wildcard"])).unique("gw").select("gw").to_dict(as_series=False))

    # weeks of unsaved transfers
    print(df.filter(pl.col("element_in").is_not_null()).select("gw").unique("gw").to_dict(as_series=False))
    
    # 100-point gameweek
    print(df.filter(pl.col("total_points") > 100))

    #lucky weeks
    # your 13th player 

    metrics = {
        "n_transfers": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).filter(pl.col("transfer_point_delta").is_not_null()).count().select("element_in").item(), # no chips included
        "transfer_points_gained": {
                "freehit": df.filter(pl.col("active_chip") == "freehit").select("transfer_point_delta", "gw").group_by("gw").sum().to_dicts(),
                "transfers": t_df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).select("gw", "transfer_point_delta"),
                "wildcard": df.filter(pl.col("active_chip")== "wildcard").select("transfer_point_delta",  "gw").group_by("gw").sum().to_dicts(),
                "bboost": df.filter(pl.col("active_chip")== "bboost").select("transfer_point_delta",  "gw").group_by("gw").sum().to_dicts(),
                "3xc": df.filter(pl.col("active_chip")== "3xc").select("transfer_point_delta",  "gw").group_by("gw").sum().to_dict(),
           },
        "best_transfers_no_chips": {
            "good": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).filter(pl.col("transfer_point_delta").is_not_null()).sort(by="transfer_point_delta",descending=True),
            "max": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).max()
        },
        
        # # allow users to view the exact week on fpl web, construct path
        "bad_transfers_no_chips": {
            "bad": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).filter(pl.col("transfer_point_delta").is_not_null()).sort(by="transfer_point_delta",descending=True),
            "min": df.filter(~pl.col("active_chip").is_in(["wildcard", "freehit"])).min()
        },

        "points_gained_with_wildcard": t_df.filter(pl.col("active_chip") == "wildcard").select(["transfer_point_delta", "gw"]).group_by("gw").sum().to_dicts(),
        "points_gained_with_freehit": t_df.filter(pl.col("active_chip") == "freehit").select(["transfer_point_delta", "gw"]).group_by("gw").sum().to_dicts(), #freehit one or two
        "transfer_activity": {
            # aggregate sum, count
            "negative_transfer": t_df.filter(pl.col("transfer_point_delta") < 0).select(["element_out", "element_in", "element_in_player_name", "element_in_fixture",  "element_out_player_name", "element_out_team", "transfer_point_delta", "element_out_fixture"]).to_dicts(), # transfers that should have been delayed
            "positive_transfer": t_df.filter(pl.col("transfer_point_delta") > 0).select(["element_out", "element_in", "element_in_player_name", "element_in_fixture",  "element_out_player_name", "element_out_team", "transfer_point_delta", "element_out_fixture"]).to_dicts()
        },
        "points_gained_from_captains": c_df.filter(
                                                    (pl.col("active_chip") != "3xc") | (pl.col("active_chip").is_null())).select(
                                                    [
                                                        "gw", "final_captain_gameweek_score", "captain_fixture", "vice_captain_fixture", "active_chip", "captain_player_name", "vice_captain_player_name", "captain_gameweek_score", "vice_captain_gameweek_score", "captain_minutes", "vice_captain_minutes",
                                                        ]).unique(
                                                        "gw"), # group by players,
        "points_gained_from_3xc": c_df.filter(
                                                pl.col("active_chip") == "3xc").select(
                                                    ["gw", "final_captain_gameweek_score", "captain_gameweek_score", "captain_fixture", "vice_captain_fixture", "captain_player_name", "vice_captain_player_name", "vice_captain_gameweek_score", "captain_minutes", "vice_captain_minutes"]).unique(
                                                        "gw"),
        }

    # print("----")
    # print(metrics)

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
        pl.col("gameweek").cast(pl.Int64,)
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


def story_1(entry_id):
    """
    Key Outputs, a vertical p_df and u_p_df which is grouped by gameweek into a list
    """

    # troll of the season
    #relies on the number of occurence, when as vice-captain , point-delta > captain
    # when as captain point-delta < vice-captain
    # when on the bench, scores points, when starting 

    # missing out hauls on players you owned for long periods (at least 10 weeks) ? 
    # hauls of highest scoring players? and which you owned for which periods

    # like a grid map [1, 2, 3, 4, 5 ]

    # list of players
    # list players and their season points 
    # players and points individual gained from them 
    # find trolls, find solid buys, infer patterns

    transfer_df, df, _ = analyse(1491605) # entry is league id

    df = df.filter(pl.col("entry_id") == entry_id)

    p_df = df.select(["players", "gw", "captain", "vice_captain"])
    p_df = player_transform(p_df, vertical=True)
    p_df = enrich_player_cols(p_df, ["captain", "vice_captain"], attributes=["minutes"])

    p_df = p_df.with_columns(
        ## filters for rows without triple captain
            pl.when(
                pl.col("captain_minutes") == 0
            ).then(pl.col("vice_captain")).otherwise(pl.col("captain"))
                .alias("final_captain"))
    
    p_df = enrich_player_cols(p_df, interested_cols=["players"], attributes=["fixture"]) 
    # p_df contains players in vertical format

    u_p_df = p_df.select(["players", "gw"]).cast({"players": pl.Int64}).group_by("players").agg(pl.col("gw"))
    c_p_df = p_df.select(["final_captain", "gw"]).unique(["final_captain", "gw"]).unique(["final_captain", "gw"]).group_by("final_captain").agg(pl.col("gw")).rename({"gw": "captain_gw"})
    u_p_df = u_p_df.join(c_p_df, left_on="players", right_on="final_captain", how="left")

    del c_p_df

    ei_transfer_df = transfer_df.select(["element_in", "gw"]).sort(by="gw").group_by("element_in").agg(pl.col("gw")).rename({"gw": "element_in_gw"})
    eo_transfer_df = transfer_df.select(["element_out", "gw"]).sort(by="gw").group_by("element_out").agg(pl.col("gw")).rename({"gw": "element_out_gw"})
    
    u_p_df = u_p_df.join(ei_transfer_df, left_on="players", right_on="element_in", how="left")
    u_p_df = u_p_df.join(eo_transfer_df, left_on="players", right_on="element_out", how="left")

    # populates with u_p_df with points across season
    u_p_df = u_p_df.with_columns(
        pl.struct("players", "gw")
        .map_elements(
            lambda row: Player(row["players"], row["gw"]).total_points,
            pl.List(pl.Int64)
        )
        .alias("player_points"))
    
    u_p_df = u_p_df.with_columns(
        pl.struct("players", "gw")
        .map_elements(
            lambda row: Player(row["players"], row["gw"]).season_score,
            pl.List(pl.Int64)
        )
        .alias("season_points"))
    
    u_p_df = enrich_player_cols(u_p_df, interested_cols=["players"], attributes=["player_name", "team", "position"])

    print(df_details(u_p_df))
    print(u_p_df.to_dict(as_series=False))

    # I used LLMs to analyse the JSON, find a way to display the table, then textbox to enable questions to LLMs
    # Requires a prompt template/ prompt structure

    return u_p_df

    
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

    # issues with map_elements and nulls, not skipping nulls as defined
    # SQLAlchemy caching working against me because of the same specified is, player_id.
    #  it returns the same value despite different gameweek - diagnosed to be due to sqlalchemy data mapper
    # resorted to default sql statement