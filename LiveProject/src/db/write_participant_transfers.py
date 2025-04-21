"""Multiprocessing script to write weekly entries to database"""

from src.utils import get_gw_transfers, get_gw_transfers_scrap, get_participant_entry
from sqlalchemy.orm import sessionmaker
import logging
import gevent
import pandas as pd


LOGGER = logging.getLogger(__name__)

def participant_transfers(entry_id: list[int] | int, gw: int, to_json=False) ->  pd.DataFrame:
    """Downloads weekly entry for a list of entry Id"""
    new_directory = "data/participant/"
    if type(entry_id) is list:
        entry_id = entry_id[0].split(",")
        for n in range(0, len(entry_id)):
            # optimum number of spawned threads to 100
            req = [
                gevent.spawn(
                    get_gw_transfers_scrap,
                    gw=args.gameweek_id,
                    alist=entry_id,
                    all=True)
                ]
            res = [response.value for response in gevent.iwait(req)]
            filename = f"{entry_id[n]}_transfers.json"
            if not os.path.exists(new_directory):
                os.makedirs(new_directory)
            df = pd.DataFrame(res)
            print(df.to_json())

            if to_json:
                df.to_json(os.path.join(new_directory, filename))
                print(f"done {filename}")
    return df



if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser("Writing participant entries into DB")
    parser.add_argument("-g", "--gameweek_id", type=int, help="Gameweek entry")
    parser.add_argument("-t", "--processes", type=int, help="Number of processes")
    parser.add_argument("-p", "--participant_id", nargs='+')

    args = parser.parse_args()
    # TABLE_NAME = f"Entries_League_{args.participant_id}_Gameweek_{args.gameweek_id}"
    # engine = create_connection_engine()
    participant_transfers(args.participant_id, args.gameweek_id)
