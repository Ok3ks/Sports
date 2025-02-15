from src.db.db import create_connection_engine
from src.utils import League
import argparse
import pandas as pd
from itertools import chain
import time
import gevent
import logging

LOGGER = logging.getLogger(__name__)

def league_participant_info(league_id: int, connection, PAGE_COUNT=1):
    """Extracts Participants of a league """
    test = League(league_id)
    while test.has_next:
        # spawning 100 threads at once
        req = [
            gevent.spawn(test.get_league_participant_mp, i)
            for i in range(PAGE_COUNT, PAGE_COUNT + 100, 1)
        ]
        PAGE_COUNT += 100
        res = [response.value for response in gevent.iwait(req)]
        count = sum(1 for _ in res)

        df = pd.DataFrame(chain.from_iterable(res))

        if df.shape[1] == 3:
            df.columns = ["id", "participant_entry_name", "participant_player_name"]
            df.to_sql(
                f"League_{str(test.league_id)}",
                connection,
                if_exists="append",
                chunksize=1000,
                method="multi",
            )

            if (PAGE_COUNT) % 40_000 == 0:
                time.sleep(5)

            LOGGER.info(f"PAGE 1 to {PAGE_COUNT} done")
        else:
            test.has_next = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Update Participant information")

    parser.add_argument(
        "-l",
        "--league_id",
        type=int,
        required=True,
        help="Gameweek you are trying to get a report of",
    )
    args = parser.parse_args()
    connection = create_connection_engine()

    # dividing by apriori knowledge of number of pages
    league_participant_info(args.league_id, connection)
