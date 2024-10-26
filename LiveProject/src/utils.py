import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import get as wget
import pandas as pd
import json
import numpy as np

from src.urls import GW_URL, FIXTURE_URL, TRANSFER_URL, HISTORY_URL, FPL_URL
from src.urls import H2H_LEAGUE, LEAGUE_URL, FPL_PLAYER
from functools import lru_cache

from src.paths import APP_DIR, MOCK_DIR
from src.db.db import get_player,  get_player_fixture, get_player_team_code
from src.db.db import team_short_name_mapping, team_name_to_code
from typing import List, Union
import logging

s = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[502, 503, 504],
    allowed_methods={'GET', 'POST'},
)
r = s.mount("https://fantasy.premierleague.com/api/", HTTPAdapter(max_retries=retries))
LOGGER = logging.getLogger(__name__)


def to_json(x: dict, fp):
    with open(fp, "w") as outs:
        json.dump(x, outs)
    print(f"{x.keys()} stored in Json successfully. Find here {fp}")


def get_basic_stats(total_points: List[Union[int, float]]):
    """Measures of Central Tendency for Total points"""
    average = np.mean(total_points)
    Q3 = np.percentile(total_points, 75)
    Q1 = np.percentile(total_points, 25)
    return Q1, average, Q3


def parse_transfers(item: dict) -> dict:
    row = {}
    """
        row[item['entry']] = {'element_in': [], 'element_out': []}
        row[item['entry']] = row.get(item['entry'], {})

        row[item['entry']]['element_in'] = [item['element_in']]
        row[item['entry']]['element_out'] = [item['element_out']]
    """

    row[item["entry"]] = row.get(item["entry"], {})
    row[item["entry"]]["element_in"] = row[item["entry"]].get("element_in", [])
    row[item["entry"]]["element_out"] = row[item["entry"]].get("element_out", [])

    row[item["entry"]]["element_in"].append(item["element_in"])
    row[item["entry"]]["element_out"].append(item["element_out"])

    return row


def check_gw(gw: Union[int, List[int]]) -> tuple:
    out = []
    if type(gw) == int and gw >= 1 and gw <= 38:
        return (True, gw)

    elif type(gw) == list:
        for i in gw:
            if check_gw(i)[0]:
                out.append(i)
        return (True, out)
    else:
        print("Gameweek has to be in the range 1 to 38")
        pass


class GameweekError(Exception):
    """Custom exception for invalid gameweek"""

    def __init__(self, message="Gameweek is not valid (Should be in range 1,38)"):
        super().__init__(message)


def get_gw_transfers(alist: List[int], gw: Union[int, List[int]], all=False) -> dict:
    """Input is a list of entry_id. Gw is the gameweek number.
    'all' toggles between extracting all gameweeks or not"""

    try:
        valid, gw = check_gw(gw)
    except TypeError:
        valid, gw = False, None
    row = {}
    if valid:
        for entry_id in alist:
            r = wget(TRANSFER_URL.format(entry_id))
            if r.status_code == 200:
                obj = r.json()
                # updates by gameweek
                for item in obj:
                    if all:
                        row[item["event"]] = parse_transfers(item)
                    else:
                        if type(gw) == int and int(item["event"]) == gw:
                            # updates each id
                            row.update(parse_transfers(item))
                        elif type(gw) == list:
                            if int(item["event"]) in gw:
                                row[item["event"]] = parse_transfers(item)
            else:
                print("{} does not exist or Transfer URL endpoint unavailable".format(entry_id))

    return row


def get_participant_entry(entry_id: int, gw: int) -> dict:
    """Calls an Endpoint to retrieve a participants entry"""
    try:
        valid, gw = check_gw(gw)
    except TypeError:
        valid, gw = False, None

    if valid:
        # optimization, imported get directly from requests, but changed name to wget for easy reference
        r = wget(FPL_PLAYER.format(entry_id, gw))

        # optimization - assigning size of dictionary before hand to prevent resizing of dictionaries
        team_list = {
            "auto_sub_in": "",
            "auto_sub_out": "",
            "gw": gw,
            "entry_id": entry_id,
            "active_chip": None,
            "points_on_bench": None,
            "total_points": None,
            "event_transfers_cost": None,
            "players": "",
            "bench": "",
            "vice_captain": None,
            "captain": None,
        }

        if r.status_code == 200:
            print("Retrieving results, participant {} for event = {}".format(entry_id, gw))
            obj = r.json()

            team_list["active_chip"] = obj["active_chip"]
            team_list["points_on_bench"] = obj["entry_history"]["points_on_bench"]
            team_list["total_points"] = obj["entry_history"]["points"]
            team_list["event_transfers_cost"] = obj["entry_history"]["event_transfers_cost"]

            if obj["automatic_subs"]:
                # optimization 1
                # team_list["auto_subs"] = [(item['element_in'],item['element_out'],) for item in obj['automatic_subs']]

                for item in obj["automatic_subs"]:
                    if len(team_list["auto_sub_in"]) < 1:
                        team_list["auto_sub_in"] = str(item["element_in"])
                    else:
                        team_list["auto_sub_in"] = team_list["auto_sub_in"] + "," + str(item["element_in"])
                    if len(team_list["auto_sub_out"]) < 1:
                        team_list["auto_sub_out"] = str(item["element_out"])
                    else:
                        team_list["auto_sub_out"] = team_list["auto_sub_out"] + "," + str(item["element_out"])

            for item in obj["picks"]:
                if item["multiplier"] != 0:
                    if len(team_list["players"]) < 1:
                        team_list["players"] = str(item["element"])
                    else:
                        team_list["players"] = team_list["players"] + "," + str(item["element"])
                else:
                    if len(team_list["bench"]) < 1:
                        team_list["bench"] = str(item["element"])
                    else:
                        team_list["bench"] = team_list["bench"] + "," + str(item["element"])
                if item["is_captain"]:
                    team_list["captain"] = int(item["element"])
                if item["is_vice_captain"]:
                    team_list["vice_captain"] = int(item["element"])
        else:
            print(f"{r.status_code}")
            print("{} does not exist".format(entry_id))

    return team_list


def get_curr_event():
    r = wget(FPL_URL)

    curr_event = []
    r = r.json()
    for event in r["events"]:
        if event["is_current"]:
            curr_event.append(event["id"])
            curr_event.append((event["finished"], event["data_checked"]))
    return curr_event


class Gameweek:
    def __init__(self, gw=1):
        self.gw = gw

    def get_payload(self):
        temp = wget(GW_URL.format(self.gw))
        temp_2 = wget(FPL_URL)

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
        highest = self.week_df.sort_values(by="total_points", ascending=False).iloc[0, :]
        print(get_player(highest["id"]).player_id)
        print(get_player(highest["id"]).team)
        del highest

    def dream_team(self):
        dream_team = self.week_df[self.week_df["in_dreamteam"] == True]
        print(dream_team)
        for i in dream_team.itertuples():
            print(i[-3], get_player(i[-3]).player_name)

    def highest_xg(self):
        highest_xg = self.week_df.sort_values(by="expected_goals", ascending=False).iloc[0, :]
        print("\n Higest Xg")
        print(get_player(highest_xg["id"]).team)
        print(get_player(highest_xg["id"]).player_name)

    def highest_xgc(self):
        highest_xgc = self.week_df.sort_values(by="expected_goals_conceded", ascending=False).iloc[0, :]
        print("\n Highest Xgc")
        print(get_player(highest_xgc["id"]).team)
        print(get_player(highest_xgc["id"]).player_name)

    def highest_xa(self):
        highest_xa = self.week_df.sort_values(by="expected_assists", ascending=False).iloc[0, :]
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
    def __init__(self, entry_id):
        self.participant = entry_id

    def get_gw_transfers(self, gw: Union[int, List[int]], all=False) -> dict:
        """Input is a list of entry_id. Gw is the gameweek number.
        'all' toggles between extracting all gameweeks or not"""

        row = {}
        try:
            valid, gw = check_gw(gw)
        except TypeError:
            valid, gw = False, None

        if all or valid:
            r = wget(TRANSFER_URL.format(self.participant))
            LOGGER.info(r.status_code)
            if r.status_code == 200:
                obj = r.json()
                for item in obj:
                    if all:
                        row[item["event"]] = row.get(item["event"], {})
                        row[item["event"]]["element_in"] = row[item["event"]].get("element_in", [])
                        row[item["event"]]["element_out"] = row[item["event"]].get("element_out", [])
                        row[item["event"]]["element_in"].append(item["element_in"])
                        row[item["event"]]["element_out"].append(item["element_out"])
                    else:
                        if type(gw) == list and int(item["event"]) in gw:
                            row[item["event"]] = row.get(item["event"], {})
                            row[item["event"]]["element_in"] = row[item["event"]].get("element_in", [])
                            row[item["event"]]["element_out"] = row[item["event"]].get("element_out", [])
                            row[item["event"]]["element_in"].append(item["element_in"])
                            row[item["event"]]["element_out"].append(item["element_out"])
                        elif type(gw) == int and int(item["event"]) == gw:
                            row[item["event"]] = row.get(item["event"], {})
                            row[item["event"]]["element_in"] = row[item["event"]].get("element_in", [])
                            row[item["event"]]["element_out"] = row[item["event"]].get("element_out", [])
                            row[item["event"]]["element_in"].append(item["element_in"])
                            row[item["event"]]["element_out"].append(item["element_out"])
            else:
                print("{} does not exist or Transfer URL endpoint unavailable".format(self.participant))
        return row

    def get_span_week_transfers(self, span: List[int]) -> dict:
        return self.get_gw_transfers(span)

    def get_all_week_transfers(self) -> dict:
        curr_gw = get_curr_event()[0]
        print("getting all entries up to {}".format(curr_gw))
        return self.get_gw_transfers(curr_gw, all=True)

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
                self.all_gw_entries = [get_participant_entry(self.participant, gameweek) for gameweek in gw]
            elif type(gw) == int:
                self.all_gw_entries = [
                    get_participant_entry(self.participant, gameweek) for gameweek in range(1, gw + 1)
                ]
            return self.all_gw_entries
        else:
            raise GameweekError

# class Teams:


class Player:
    def __init__(self, player_id, half):
        self.player_id = player_id
        self.half = half

    def get_fixures(self):
        team_code = get_player_team_code(self.player_id, self.half)[0]
        obj = get_player_fixture(team_code, gameweek=5)
        return obj


class League:
    def __init__(self, league_id):
        self.league_id = league_id
        self.participants = []
        self.res = None
        self.league_name = ""

    def obtain_league_participants(self, refresh=False):
        """This function uses the league url as an endpoint to query for participants of a league at a certain date.
        Should be used to update participants table in DB"""

        if refresh or len(self.participants) == 0:
            has_next = True
            PAGE_COUNT = 1
            while has_next:
                r = s.get(LEAGUE_URL.format(self.league_id, PAGE_COUNT))
                obj = r.json()
                LOGGER.info(r.status_code)
                LOGGER.info(r.headers)
                assert r.status_code == 200, "error connecting to the endpoint"
                del r
            
                self.league_name = obj["league"]["name"]
            
                self.participants.extend(obj["standings"]["results"])
                has_next = obj["standings"]["has_next"]
                print("All participants on page {} have been extracted".format(PAGE_COUNT))
                PAGE_COUNT += 1

                self.league_name = obj["league"]["name"]
        self.entry_ids = [participant["entry"] for participant in self.participants]
        return self.participants

    def get_league_count(self):
        if len(self.participants > 1): 
            return len(self.participants)
        else:
            print("Obtain league participants first before getting league count")
            
    
    def get_participant_name(self, refresh=False) -> dict:
        """Creates participant id to name hash table"""
        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()
        self.participant_name = {str(participant['entry']) : participant['entry_name'] for participant in self.participants}
        self.id_participant = (
            [
                participant["entry"],
                participant["entry_name"],
                participant["player_name"],
            ]
            for participant in self.participants
        )
        return self.participant_name

    def get_league_participant_mp(self, PAGE_COUNT):
        has_next = True
        out = []

        r = wget(LEAGUE_URL.format(self.league_id, PAGE_COUNT))
        obj = r.json()
        assert r.status_code == 200, "error connecting to the endpoint"
        del r
        out.extend(obj["standings"]["results"])
        has_next = obj["standings"]["has_next"]
        PAGE_COUNT += 1
        print("page {} done".format(PAGE_COUNT))

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
        self.transfers = []
        if refresh or len(self.participants) == 0:
            self.obtain_league_participants()

        self.transfers = get_gw_transfers(self.entry_ids, gw)
        return self.transfers


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="weeklyreport", description="Provide Gameweek ID and League ID")
    parser.add_argument(
        "-g",
        "--gameweek_id",
        type=int,
        help="Gameweek you are trying to get a report of",
    )
    parser.add_argument("-dry", "--dry_run", type=bool, help="Dry run")
    parser.add_argument("-l", "--league_id", type=int, help="Gameweek you are trying to get a report of")
    parser.add_argument("-t", "--thread", type=int)

    args = parser.parse_args()
    if args.dry_run:
        test_gw = Gameweek(args.gameweek_id)
        with open(f"{MOCK_DIR}/endpoints/gameweek_endpoint.json", "r") as ins:
            test_gw.json = json.load(ins)

        with open(f"{MOCK_DIR}/endpoints/fpl_url_endpoint.json", "r") as ins_2:
            test_gw.gw_json = json.load(ins_2)

        test_gw.parse_payload()
        # test_gw.highest_scoring_player()
        # test_gw.dream_team()
        # test_gw.highest_xg()
        # test_gw.highest_xgc()
        # test_gw.highest_xa()
        # test_gw.gameweek_status()
    else:
        print(get_participant_entry(entry_id=98120, gw=1))
        # test = League(args.league_id)
        # test.get_participant_name()
        # connection = create_connection_engine("fpl")
        # create_id_table(table_name= test.league_name)
        # df = pd.DataFrame(test.id_participant)
        # df.columns = ['id', 'participant_entry_name', 'participant_player_name']

        # df.to_sql(test.league_name,connection, if_exists='append', chunksize=1000, method="multi")
        # test.get_all_participant_entries(args.gameweek_id, thread=args.thread)
