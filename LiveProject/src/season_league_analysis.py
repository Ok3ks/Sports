from dataclasses import dataclass, asdict
import requests
from src.urls import TRANSFER_URL
from src.utils import League, get_curr_event
import polars as pl
from functools import lru_cache
from src.db.update_season_fixture import update_season_fixture
from src.db.db import get_fixture_gameweek, get_player_stats_from_db_gql, get_player, get_player_gql, get_player_info, get_player_team_map, get_fixtures, get_teams

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


#individual -- you missed deadline
#optimum formation for individuals by gameweek - your favored 4-4-2 formation
#midweek deadline - how did you fare
#longest serving player contrasted with shortest stint
#what could have beem - points pre use of chips


@dataclass(frozen=True, order=True)
class Fixture:
    home_difficulty: int
    away_difficulty: int
    home: str 
    away: str
    home_goals: float
    away_goals: float
    code: int
    gameweek: int
    finished: bool
    date: str



class Player:
    """This class represents a premier league player"""

    def __init__(self, player_id, gw):
        self.gw = gw
        self.player_id = player_id
        self._team = None
        self._position = None
        self._player_name = None
        self._gameweek_score = None

    def _player_score(self):
        obj = get_player_stats_from_db_gql(self.player_id, self.gw)
        return obj

    def _fixture(self) -> Fixture:
        if not self.team:
            self._player_info()
        return get_fixture_gameweek(self._team, self.gw)  # can return Fixture dataclass

    def _player_info(self):
        half = 1
        if self.gw > 18:
            half = 2
        obj = get_player_info(self.player_id, half) # can return Team dataclass
        
        self._team = obj[0].team
        self._position = obj[0].position
        self._player_name = obj[0].player_name    
        return obj

    @property
    def gameweek_score(self):
        return self._player_score()
    
    @property
    def fixture(self):
        return Fixture(
            *self._fixture()[0]
        )
    
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


def expand_date(df: pl.DataFrame):
        """Takes in a polars Dataframe with a str col - date
        
        and expands into month,day,weekday,time,year.
        
        """
        df = df.with_columns(
            pl.col("date").cast(pl.Datetime).dt.month().alias("month"),
            pl.col("date").cast(pl.Datetime).dt.day().alias("day"),
            pl.col("date").cast(pl.Datetime).dt.weekday().alias("weekday"),
            pl.col("date").cast(pl.Datetime).dt.time().alias("time"),
            pl.col("date").cast(pl.Datetime).dt.year().alias("year")
        )
        return df


def analyse(league_id: int):
    df = get_league_data(league_id=league_id)
    # transfer_df = get_transfer_data(league_id=league_id)

            # fixture_df = get_fixture_data()
            # fixture_df = fixture_df.filter(pl.col("date").is_not_null()).with_columns(
            #     pl.col("gameweek").cast(pl.Int64)
            #     ).rename({"gameweek": "gw"})


            # gw_deadline_time = fixture_df.select("gw", "date").unique("gw",keep="first")
            # gw_end_time = fixture_df.select("gw", "date").unique("gw",keep="last")

            # df = df.join(gw_deadline_time, on="gw", how="left")
            # df = expand_date(df)


    # in addition to data present in FPL for each league
    # in addition to data present in FPL for each player

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

    # fixture df 

    print(df.show(5))

    # df.join().select(pl.col("gameweek").alias("gw")), on="gw")

    #using player information for analysis

    print(highest)

    # which position is the most benched apart from goalkeepers?
    # ties into the preferred formation

    # Your preferred formation of xxx means you bench yyy, and zzz is your first sub
    # this made you lose vwx compared to, and gain yza compared to .

    df = df.with_columns(
        pl.col("players").str.split(",").
        list.to_struct(fields=[
            "player_1", "player_2", "player_3", "player_4",
            "player_5", "player_6", "player_7", "player_8",
            "player_9", "player_10", "player_11"
            ])
    ).unnest("players").drop_nulls()

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
    ]).alias("player_positions")
    )

    df = df.with_columns(
        pl.col("player_positions").list.eval(pl.element().value_counts()).alias("formation")
    )

    # bench = df.select(pl.col("bench", "gw", "entry_id"))
    # bench = bench.with_columns(
    #     pl.col("bench").str.split(",")
    #     .list.to_struct(fields=["bench_1", "bench_2", "bench_3", "bench_4"])  # modularize
    #     ).unnest("bench").drop_nulls()
    
    # bench_cols = ["bench_1", "bench_2", "bench_3", "bench_4"]

    # bench = bench.with_columns([
    #     pl.struct(col, "gw")
    #     .map_elements(
    #         lambda row, c=col: Player(row[c], row["gw"]).team,
    #         return_dtype=pl.String
    #     )
    #     .alias(f"{col}_team")
    #     for col in bench_cols
    # ])

    # bench = bench.with_columns([
    #     pl.struct(col, "gw")
    #     .map_elements(
    #         lambda row, c=col: asdict(Player(row[c], row["gw"]).fixture),
    #         return_dtype=pl.Struct({
    #             "home_difficulty": pl.Int64,
    #             "away_difficulty": pl.Int64,
    #             "home": pl.String, 
    #             "away": pl.String,
    #             "home_goals": pl.Float64,
    #             "away_goals": pl.Float64,
    #             "code": pl.Int64,
    #             "gameweek": pl.Float64,
    #             "finished": pl.Int64,
    #             "date": pl.String
    #         })
    #     )
    #     .alias(f"{col}_fixture")
    #     for col in bench_cols
    # ])

    # bench = bench.with_columns([
    #     pl.struct(col, "gw")
    #     .map_elements(
    #         lambda row, c=col: Player(row[c], row["gw"]).player_name,
    #         return_dtype=pl.String
    #     )
    #     .alias(f"{col}_name")
    #     for col in bench_cols
    # ])

    # bench = bench.with_columns([
    #     pl.struct(col, "gw")
    #     .map_elements(
    #         lambda row, c=col: Player(row[c], row["gw"]).position,
    #         return_dtype=pl.String
    #     )
    #     .alias(f"{col}_position")
    #     for col in bench_cols
    # ])

    # bench = bench.with_columns([
    #     pl.struct(col, "gw")
    #     .map_elements(
    #         lambda row, c=col: Player(row[c], row["gw"]).gameweek_score.total_points,
    #         return_dtype=pl.Int64
    #     )
    #     .alias(f"{col}_points")
    #     for col in bench_cols
    # ])

    print(df)
    print(df.select("formation"))
    # print(df.schema["player_positions"])

    
    
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

    ## unable to map into another data type with polars , you need to do in the rust side
    ## strong discourages doing anything in python, especially lambdas, there are idiomatic expressions for this

        # f = highest.with_columns(
        #     pl.struct(["players", "gw"])
        #         .map_elements(
        #             lambda row: classize(row["players"], row["gw"]),
        #             )
        # )

        # def classize(obj, gw: int):
        #     new_obj = []

        #     for i in obj[0].split(","):
        #         new_obj.append(Player(i,gw))
            
        #     return new_obj