"""Multiprocessing script to write weekly entries to database"""

from src.utils import League
import logging
import json
from src.db.participant_info_table import league_participant_info
import pandas as pd

LOGGER = logging.getLogger(__name__)

def league_participant_weekly_entry( league_id : int, gameweek: list[int] | int | None = None, to_json=False, upload=True):
    """Downloads weekly entry for a list of entry Id"""

    new_directory = f"data/league/{args.league_id}"
    league = League(league_id=league_id)

    if not os.path.exists(new_directory):
        os.makedirs(new_directory)

    if gameweek is None:
        gameweek = [i for i in range(1, 39)]

    if type(gameweek) is list:
        for gw in gameweek: 
            res = league.get_all_participant_entries(gw),
            res = [*res]
            filename = f"{gw}_entries.pqt"
            destination_path = os.path.join(new_directory, filename)

            df = pd.DataFrame(res)
            if to_json:
                df.to_parquet(destination_path, compression="brotli")
                print(f"{filename} saved")

            if gw % (len(gameweek)//4) == 0:
                time.sleep(5)

    else :
        res = league.get_all_participant_entries(gw=gameweek)
        if to_json:
            res = [*res]
            filename = f"{gameweek}_entries.pqt"
            destination_path = os.path.join(new_directory, filename)
            df = pd.DataFrame(res)
            if to_json:
                df.to_parquet(destination_path, compression="brotli")
                print(f"{filename} saved to json")


if __name__ == "__main__":
    import argparse
    import os
    import time

    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-l", "--league_id", type=int, help="league_id", required=True)
    parser.add_argument("-g", "--gameweek_id", type=int, help="gameweek entry")
    args = parser.parse_args()

    if args.gameweek_id:
        league_participant_weekly_entry(gameweek= args.gameweek_id, league_id= args.league_id, to_json=True, upload=False)
    else:
        league_participant_weekly_entry(league_id= args.league_id, to_json=True, upload=False)


