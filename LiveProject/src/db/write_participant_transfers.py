"""Multiprocessing script to write weekly entries to database"""

from typing import List, Union
from LiveProject.src.urls import TRANSFER_URL
from src.utils import check_gw, parse_transfers
import logging
import gevent
import pandas as pd
from requests import Session

LOGGER = logging.getLogger(__name__)


def get_gw_transfers_scrap(
    alist: List[int], gw: Union[int, List[int]], s: Session, all=False
) -> dict:
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
            r = s.get(TRANSFER_URL.format(entry_id))
            if r.status_code == 200:
                obj = r.json()
                # updates by gameweek
                for item in obj:
                    if all:
                        obj_row[item["event"]] = parse_transfers(item, {})
                    else:
                        if isinstance(gw, int) and int(item["event"]) == gw:
                            # updates each id
                            obj_row.update(parse_transfers(item, {}))
                        elif isinstance(gw, list):
                            if int(item["event"]) in gw:
                                obj_row[item["event"]] = parse_transfers(item, {})
            else:
                print(
                    "{} does not exist or Transfer URL endpoint unavailable".format(
                        entry_id
                    )
                )
            row[entry_id] = obj_row
    return row


def participant_transfers(
    entry_id: list[int] | int, gw: int, to_json=False
) -> pd.DataFrame:
    """Downloads weekly entry for a list of entry Id"""
    new_directory = "data/participant/"
    if type(entry_id) is list:
        entry_id = entry_id[0].split(",")
        for n in range(0, len(entry_id), 100):
            # optimum number of spawned threads to 100
            req = [
                gevent.spawn(
                    get_gw_transfers_scrap,
                    gw=args.gameweek_id,
                    alist=entry_id,
                    all=True,
                )
            ]
            res = [response.value for response in gevent.iwait(req)]
            filename = f"{entry_id[n]}_transfers.pqt"
            if not os.path.exists(new_directory):
                os.makedirs(new_directory)
            df = pd.DataFrame(res)

            if to_json:
                df.to_parquet(
                    os.path.join(new_directory, filename), compression="brotli"
                )
                print(f"done {filename}")
    return df


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-t", "--processes", type=int, help="Number of processes")
    parser.add_argument("-p", "--participant_id", nargs="+")

    args = parser.parse_args()
    # TABLE_NAME = f"Entries_League_{args.participant_id}_Gameweek_{args.gameweek_id}"
    # engine = create_connection_engine()
    participant_transfers(args.participant_id, args.gameweek_id)
