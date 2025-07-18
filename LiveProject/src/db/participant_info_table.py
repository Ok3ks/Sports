from src.db.db import create_connection_engine
from src.utils import League
import argparse
import pandas as pd
from itertools import chain
import time
import gevent
import logging

LOGGER = logging.getLogger(__name__)


def league_participant_info(league_id: int, connection=None, PAGE_COUNT=207700, to_json=False):
    """Extracts Participants of a league """
    test = League(league_id)
    while test.has_next:

        # occasional breaks to not overwhelm the server
        if (PAGE_COUNT) % 40_000 == 0:
            time.sleep(5)
            LOGGER.info(f"PAGE 1 to {PAGE_COUNT} done")

        # spawning 100 threads at once with gevent for faster IO
        try:
            req = [
                gevent.spawn(test.get_league_participant_mp, i)
                for i in range(PAGE_COUNT, PAGE_COUNT + 100, 1)
            ]
            res = [response.value for response in gevent.iwait(req)]
            count = sum(1 for _ in res)
            assert count == 100

            df = pd.DataFrame(chain.from_iterable(res))
            print(df.head())
            df.columns = [
                "id",
                "participant_entry_name",
                "participant_player_name"
                ]
        except TypeError or ValueError as e:
            if e is TypeError:
                time.sleep(50)
            else:
                print("End of loop")
                break

        finally:
            PAGE_COUNT += 100

        if to_json:
            path = f"data/names/general_{PAGE_COUNT}.json"
            df.to_json(path)
            LOGGER.info(f"Json Saved to {path}")
            print(f"Json Saved to {path}")


        if df.shape[1] == 3 and connection is not None:
            df.to_sql(
                f"League_{str(test.league_id)}",
                connection,
                if_exists="append",
                chunksize=1000,
                method="multi",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Update Participant information")

    parser.add_argument(
        "-l",
        "--league_id",
        type=int,
        required=True,
        help="Gameweek you are trying to get a report of",
    )
    parser.add_argument(
        "-db",
        "--use-db",
        type=bool,
        required=False,
        default=False,
        help="Save to DB"
    )
    args = parser.parse_args()

    # dividing by apriori knowledge of number of pages
    league_participant_info(args.league_id, to_json=True)
