"""Multiprocessing script to write weekly entries to database"""

from src.utils import League, bucket_client
import logging
from src.db.participant_info_table import league_participant_info
import pandas as pd

LOGGER = logging.getLogger(__name__)
bucket = bucket_client()

def league_participants( league_id : int, to_json=False, upload=True):
    """Downloads weekly entry for a list of entry Id"""

    new_directory = f"data/league/{args.league_id}"
    league = League(league_id=league_id)

    if not os.path.exists(new_directory):
        os.makedirs(new_directory)


    res = league.obtain_league_participants(),
    filename = "participant.json"
    destination_path = os.path.join(new_directory, filename)

    df = pd.DataFrame(res)
    if to_json:
        df.to_json(destination_path)
        print(f"{filename} saved to json")

    if upload:
        print(bucket.exists())
        blob = bucket.blob(f"{args.league_id}/{filename}")
        blob.upload_from_filename(destination_path)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-l", "--league_id", type=int, help="Gameweek entry", required=True)
    args = parser.parse_args()

    league_participants(league_id= args.league_id, to_json=True, upload=False)


