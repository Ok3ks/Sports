from dataclasses import asdict, dataclass
import requests
from httpx_retries import Retry, RetryTransport
import httpx
from requests.adapters import HTTPAdapter
import pandas as pd
import json
import numpy as np
from google.cloud import storage
from src.db.db import get_fixtures
from functools import lru_cache



from .urls import GW_URL, TRANSFER_URL, FPL_URL, FPL_PLAYER, HISTORY_URL
from .urls import LEAGUE_URL, FPL_PLAYER

from .db.db import get_fixture_gameweek, get_player, get_player_info, get_player_season_points, get_player_stats_from_db_gql, get_player_team_code
from typing import Any, List, Union
import logging
import ssl
import polars as pl

LOGGER = logging.getLogger(__name__)

context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2

s = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[502, 503, 504],
    allowed_methods={"GET"},
)
transport = RetryTransport(retry=retries)
async_client = httpx.AsyncClient(verify=context, transport=transport)



def to_json(x: dict, fp):  ## use Path instead
    with open(fp, "w") as outs:
        json.dump(x, outs)
    LOGGER.info(f"{x.keys()} stored in Json successfully. Find here {fp}")


def get_basic_stats(total_points: List[Union[int, float]]) -> tuple | None:
    """Measures of Central Tendency for Total points"""
    Q1, average, Q3 = None, None, None
    if len(total_points) >= 1:
        average = np.mean(total_points)
        Q3 = np.percentile(total_points, 75)
        Q1 = np.percentile(total_points, 25)
    return Q1, average, Q3


def parse_transfers(item: dict, row: dict) -> dict:

    """
        Extracts transfers in and out and nests into an obj with key equivalent to item["entry"].
        - Row is modified in place, with values from item. can be empty or not

        Returns a dictionary with item["entry"] as a key
    """

    row[item["entry"]] = row.get(item["entry"], {})
    row[item["entry"]]["element_in"] = row[item["entry"]].get("element_in", [])
    row[item["entry"]]["element_out"] = row[item["entry"]].get("element_out", [])

    row[item["entry"]]["element_in"].append(item["element_in"])
    row[item["entry"]]["element_out"].append(item["element_out"])

    return row


def check_gw(gw: Union[int, List[int]]) -> tuple:
    out = []
    if isinstance(gw, list):
        for i in gw:
            if check_gw(i)[0]:
                out.append(i)
            else:
                pass
        return (True, out)
    else:
        if (1 <= gw <= 38):
            return (True, gw)
        else:
            LOGGER.error(f"{gw} is out of range")
            return (False, None)


class GameweekError(Exception):
    """Custom exception for invalid gameweek"""

    def __init__(self, message="Gameweek is not valid (Should be in range 1,38)"):
        return super().__init__(message)


async def get_gw_transfers(alist: List[int], gw: Union[int, List[int], None] = None, all=False) -> dict:
    """Input is a list of entry_id. Gw is the gameweek number.
    'all' toggles between extracting all gameweeks or not"""

    row: dict = {}
    gw = None if all else gw
    valid = False

    if gw:
        try:
            valid, gw = check_gw(gw)  # excludes invalid gameweeks here
        except TypeError:
            valid, gw = False, None

    if not (valid | all):
        return row

    for entry_id in alist:
        r = await async_client.get(TRANSFER_URL.format(entry_id))
        if r.status_code == 200:
            obj = r.json()  # provides all transfers
            # updates by gameweek
            for item in obj:
                if all:
                    row[item["event"]] = parse_transfers(item, {})
                elif valid:
                    if isinstance(gw, int) and int(item["event"]) == gw:
                        row.update(parse_transfers(item, row))
                    elif isinstance(gw, list) and int(item["event"]) in gw:
                        row[item["event"]] = parse_transfers(item, {})
        else:
            LOGGER.info(
                "{} does not exist or Transfer URL endpoint unavailable".format(
                    entry_id
                )
            )
    return row

async def get_all_gw_transfers(alist: List[int]):
    """Obtains all event transfers for a list of entry Ids"""

    row: list = []

    for entry_id in alist:
        r = await async_client.get(TRANSFER_URL.format(entry_id))
        if r.status_code == 200:
            obj = r.json()  # provides all transfers
            row.extend(obj)
        else:
            LOGGER.info(
                "{} does not exist or Transfer URL endpoint unavailable".format(
                    entry_id
                )
            )
    return row
## versioning API -- API v2

def bucket_client(bucket_name="wrapped_participants_entry"):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    return bucket


async def get_participant_entry(entry_id: int, gw: int) -> dict:
    """Calls an Endpoint to retrieve a participants entry"""
    valid, gw = check_gw(gw)
    team_list: dict[str, Any] = {
        "auto_sub_in": "",
        "auto_sub_out": "",
        "gw": None,
        "entry_id": None ,
        "active_chip": None,
        "points_on_bench": None,
        "total_points": None,
        "event_transfers_cost": None,
        "players": "",
        "bench": "",
        "vice_captain": None,
        "captain": None,
    }

    if valid:
        # optimization, imported get directly from requests
        r = await async_client.get(FPL_PLAYER.format(entry_id, gw))

        # optimization - assigning size of dictionary before hand to prevent resizing of dictionaries


        if r.status_code == 200:
            obj = r.json()
            team_list["entry_id"] = int(entry_id)
            team_list["gw"] = int(gw)
            team_list["active_chip"] = obj["active_chip"]
            team_list["points_on_bench"] = obj["entry_history"]["points_on_bench"]
            team_list["total_points"] = obj["entry_history"]["points"]
            team_list["event_transfers_cost"] = obj["entry_history"][
                "event_transfers_cost"
            ]

            if obj["automatic_subs"]:
                # optimization 1
                # team_list["auto_subs"] = [(item['element_in'],item['element_out'],) for item in obj['automatic_subs']]

                for item in obj["automatic_subs"]:
                    if len(team_list["auto_sub_in"]) < 1:
                        team_list["auto_sub_in"] = str(item["element_in"])
                    else:
                        team_list["auto_sub_in"] = (
                            team_list["auto_sub_in"] + "," + str(item["element_in"])
                        )
                    if len(team_list["auto_sub_out"]) < 1:
                        team_list["auto_sub_out"] = str(item["element_out"])
                    else:
                        team_list["auto_sub_out"] = (
                            team_list["auto_sub_out"] + "," + str(item["element_out"])
                        )

            for item in obj["picks"]:
                if item["multiplier"] != 0:
                    if len(team_list["players"]) < 1:
                        team_list["players"] = str(item["element"])
                    else:
                        team_list["players"] = (
                            team_list["players"] + "," + str(item["element"])
                        )
                else:
                    if len(team_list["bench"]) < 1:
                        team_list["bench"] = str(item["element"])
                    else:
                        team_list["bench"] = (
                            team_list["bench"] + "," + str(item["element"])
                        )
                if item["is_captain"]:
                    team_list["captain"] = int(item["element"])
                if item["is_vice_captain"]:
                    team_list["vice_captain"] = int(item["element"])     


    return team_list


def get_curr_event() -> list:
    r = requests.get(FPL_URL)
    LOGGER.info(r.status_code)

    curr_event = []
    r = r.json()
    for event in r["events"]:
        if event["is_current"]:
            curr_event.append(event["id"])
            curr_event.append((event["finished"], event["data_checked"]))
    return curr_event

async def get_gw_transfers_scrap(alist: List[int], gw: Union[int, List[int]], all=False) -> dict:
    """Input is a list of entry_id. Gw is the gameweek number.
    'all' toggles between extracting all gameweeks or not"""

    try:
        valid, gw = check_gw(gw)
    except TypeError:
        valid, gw = False, None
    row = {}
    if valid:
        for entry_id in alist:
            obj_row = {}
            r = await async_client.get(TRANSFER_URL.format(entry_id))
            if r.status_code == 200:
                obj = r.json()
                # updates by gameweek
                for item in obj:
                    if all:
                        obj_row[item["event"]] = parse_transfers(item, {})
                    else:
                        if type(gw) == int and int(item["event"]) == gw:
                            # updates each id
                            obj_row.update(parse_transfers(item, {}))
                        elif type(gw) == list:
                            if int(item["event"]) in gw:
                                obj_row[item["event"]] = parse_transfers(item, {})
            else:
                print(
                    "{} does not exist or Transfer URL endpoint unavailable".format(
                        entry_id
                    )
                )
            row[entry_id] = obj
        # yield row

    return row
class Gameweek:
    def __init__(self, gw=1):
        self.gw = gw

    async def get_payload(self):
        temp = await async_client.get(GW_URL.format(self.gw))
        temp_2 = await async_client.get(FPL_URL)

        self.json = temp.json()
        self.gw_json = temp_2.json()

    def parse_payload(self):
        out = []

        for item in self.json["elements"]:
            obj = item["stats"]
            obj["id"] = item["id"]
            obj["value"] = item["explain"][0]["stats"][0]["value"]
            obj["fixture"] = item["explain"][0]["fixture"]
            out.append(obj)

        self.week_df = pd.DataFrame(out)
        print(self.week_df)

        for item in self.gw_json["events"]:
            if int(item["id"]) == int(self.gw):
                self.status = item

    def highest_scoring_player(self):
        highest = self.week_df.sort_values(by="total_points", ascending=False).iloc[
            0, :
        ]
        print(get_player(highest["id"]).player_id)
        print(get_player(highest["id"]).team)
        del highest

    def dream_team(self):
        dream_team = self.week_df[self.week_df["in_dreamteam"] == True]
        print(dream_team)
        for i in dream_team.itertuples():
            print(i[-3], get_player(i[-3]).player_name)

    def highest_xg(self):
        highest_xg = self.week_df.sort_values(
            by="expected_goals", ascending=False
        ).iloc[0, :]
        print("\n Higest Xg")
        print(get_player(highest_xg["id"]).team)
        print(get_player(highest_xg["id"]).player_name)

    def highest_xgc(self):
        highest_xgc = self.week_df.sort_values(
            by="expected_goals_conceded", ascending=False
        ).iloc[0, :]
        print("\n Highest Xgc")
        print(get_player(highest_xgc["id"]).team)
        print(get_player(highest_xgc["id"]).player_name)

    def highest_xa(self):
        highest_xa = self.week_df.sort_values(
            by="expected_assists", ascending=False
        ).iloc[0, :]
        print("\n Highest xA")
        print(get_player(highest_xa["id"]).team)
        print(get_player(highest_xa["id"]).player_name)

    def gameweek_status(self):
        if self.status["is_current"]:
            print(self.gw, "Current Gameweek")
        else:
            if not self.status["Finished"]:
                print(f"Gameweek {self.gw} is yet to be played")
            else:
                print(self.chip_usage())
                print(self.highest_score())
                print(self.gameweek_average())

    def chip_usage(self):
        return self.status["chip_plays"]

    def highest_score(self):
        return self.status["highest_scoring_entry"]

    def gameweek_average(self):
        return self.status["average_entry_score"]


class Participant:
    def __init__(self, entry_id, gw):
        self.participant = entry_id
        self.gw = gw
        self.history = None

    async def get_history(self) -> dict:
        if not self.history: 
            r = await async_client.get(HISTORY_URL.format(self.participant))
            LOGGER.info(r.status_code)
            if r.status_code == 200:
                obj = r.json()
                self.history = obj
        return self.history

    async def get_gw_transfers(self, gw: Union[int, List[int]], all=False) -> dict:
        """Input is a list of entry_id. Gw is the gameweek number.
        'all' toggles between extracting all gameweeks or not"""

        row = {}
        try:
            valid, gw = check_gw(gw)
        except TypeError:
            valid, gw = False, None

        if all or valid:
            r = await async_client.get(TRANSFER_URL.format(self.participant))
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
                        if type(gw) == list and int(item["event"]) in gw:
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
                        elif type(gw) == int and int(item["event"]) == gw:
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

    def get_span_week_transfers(self, span: List[int]) -> dict:
        return self.get_gw_transfers(span)
    

    def get_all_week_transfers(self) -> dict:
        return get_all_gw_transfers([self.participant])

    def get_all_week_entries(self, gw: Union[int, List[int]], all=False) -> list:
        if all:
            curr_gw = get_curr_event()[0]
            gw = curr_gw

        try:
            valid, gw = check_gw(gw)
        except TypeError:
            valid, gw = False, None

        if valid:
            if type(gw) == list:
                self.all_gw_entries = [
                    get_participant_entry(self.participant, gameweek) for gameweek in gw
                ]
            elif type(gw) == int:
                self.all_gw_entries = [
                    get_participant_entry(self.participant, gameweek)
                    for gameweek in range(1, gw + 1)
                ]
            return self.all_gw_entries
        else:
            raise GameweekError


class League:
    def __init__(self, league_id):
        self.league_id = league_id
        self.participants = []
        self.res = None
        self.league_name = ""
        self.has_next = True
        self.PAGE_COUNT = 1
        self.transfers = None

    async def obtain_league_participants(self, refresh=False):
        """This function uses the league url as an endpoint to query for participants of a league at a certain date.
        Should be used to update participants table in DB"""

        if refresh or len(self.participants) == 0:
            self.has_next = True
            while self.has_next:
                r = await async_client.get(LEAGUE_URL.format(self.league_id, self.PAGE_COUNT))
                if r.status_code == 200:
                    # assert r.status_code == 200, "error connecting to the endpoint"
                    obj = r.json()
                    LOGGER.info(r.status_code)
                    LOGGER.info(r.headers)
                    del r

                    self.league_name = obj["league"]["name"]

                    self.participants.extend(obj["standings"]["results"])
                    self.has_next = obj["standings"]["has_next"]
                    self.PAGE_COUNT += 1
            
                    LOGGER.info(
                        "All participants on page {} have been extracted".format(
                            self.PAGE_COUNT
                        )
                    )
                else:
                    LOGGER.error(r.text)
                    # raise EnvironmentError(msg=r.status_code)
                self.league_name = obj["league"]["name"]
        self.entry_ids = [participant["entry"] for participant in self.participants]
        return self.participants

    def get_league_count(self):
        if len(self.participants) > 1:
            return len(self.participants)
        else:
            LOGGER.info("Obtain league participants first before getting league count")

    def get_participant_name(self, refresh=False) -> dict:
        """Creates participant id to name hash table"""
        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()
        self.participant_name = {
            str(participant["entry"]): participant["entry_name"]
            for participant in self.participants
        }
        self.id_participant = (
            [
                participant["entry"],
                participant["entry_name"],
                participant["player_name"],
            ]
            for participant in self.participants
        )
        return self.participant_name

    async def get_league_participant_mp(self, PAGE_COUNT):
        """MultiProcessing version of get league participants"""
        out = []

        r = await async_client.get(LEAGUE_URL.format(self.league_id, PAGE_COUNT))
        obj = r.json()
        if r.status_code == 200:
            out.extend(obj["standings"]["results"])

            LOGGER.info("page {} done".format(PAGE_COUNT))
            return (
                [
                    participant["entry"],
                    participant["entry_name"],
                    participant["player_name"],
                ]
                for participant in out
            )

    def batch_participant_entry(self, batch):
        for participant in batch:
            yield get_participant_entry(participant["entry"], self.gw)

    def get_all_participant_entries(self, gw, refresh=False, thread=None):
        self.gw = gw

        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()
            
        # optimization 2
        for participant in self.participants:
            yield get_participant_entry(participant["entry"], gw)

    def get_gw_transfers(self, gw, refresh=False, thread=None):
        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()
        
        result = get_gw_transfers(self.entry_ids, gw)
        self.transfers = result

        return self.transfers
    
    def get_all_gw_transfers(self, refresh=False, thread=None):
        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()

        self.transfers = get_all_gw_transfers(self.entry_ids)
        return self.transfers



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
    gw = get_curr_event()[0]
    df = []

    league = League(league_id=league_id)

    for gameweek in range(1, gw, 1):
        f = league.get_all_participant_entries(gameweek)
        temp_df = pl.DataFrame(f)
        df.append(temp_df)

    f_df = pl.concat(df, how = "vertical")
    return f_df

def get_fixture_data():
    """ Get fixture data from db """
    data = get_fixtures()
    f_df = pl.DataFrame(data)
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

    
    return t_df



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
        "-l", "--league_id", type=int, help="Gameweek you are trying to get a report of"
    )
    parser.add_argument("-t", "--thread", type=int)

    args = parser.parse_args()

