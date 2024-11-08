from src.db.db import create_connection_engine
from src.utils import League



if __name__ == "__main__":
    import argparse
    import pandas as pd
    from itertools import chain

    import time
    import gevent

    parser = argparse.ArgumentParser(
        "Update Player information, this happens twice a year"
    )

    parser.add_argument(
        "-db", "--db_name", type=str, help="Database name", required=True
    )
    parser.add_argument(
        "-l",
        "--league_id",
        type=int,
        required=True,
        help="Gameweek you are trying to get a report of",
    )

    args = parser.parse_args()
    connection = create_connection_engine(
        args.db_name
    )  # Add database directory as constant
    test = League(args.league_id)
    # dividing by apriori knowledge of number of pages
    for n in range(0, 220_000):
        # optimum number of spawned threads to 100
        req = [
            gevent.spawn(test.get_league_participant_mp, i)
            for i in range(n, n + 100, 1)
        ]
        res = [response.value for response in gevent.iwait(req)]
        count = sum(1 for _ in res)

        # print(count)
        df = pd.DataFrame(chain.from_iterable(res))
        df.columns = ["id", "participant_entry_name", "participant_player_name"]
        df.to_sql(
            f"League_{str(test.league_id),connection}",
            if_exists="append",
            chunksize=1000,
            method="multi",
        )

        if (n - 175_999) % 40_000 == 0:
            time.sleep(5)

        if ValueError:
            break

        print(f"round {n} done")
