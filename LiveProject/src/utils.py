import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import json
import numpy as np
from google.cloud import storage
from src.urls import TRANSFER_URL, FPL_URL, FPL_PLAYER
from src.urls import FPL_PLAYER

from typing import List, Union, Any
import logging
import ssl

LOGGER = logging.getLogger(__name__)


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforcing TLSv1.2 or higher
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

s = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[502, 503, 504],
    allowed_methods={"GET"},
)
s.mount("https://", TLSAdapter(max_retries=3))


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
        if (1 <= gw < 38):
            return (True, gw)
        else:
            LOGGER.error(f"{gw} is out of range")
            return (False, None)


class GameweekError(Exception):
    """Custom exception for invalid gameweek"""

    def __init__(self, message="Gameweek is not valid (Should be in range 1,38)"):
        super().__init__(message)


def get_gw_transfers(alist: List[int], gw: Union[int, List[int], None] = None, all=False) -> dict:
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
        r = s.get(TRANSFER_URL.format(entry_id))
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


def bucket_client(bucket_name="wrapped_participants_entry"):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    return bucket


def get_participant_entry(entry_id: int, gw: int) -> dict:
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
        r = s.get(FPL_PLAYER.format(entry_id, gw))

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
