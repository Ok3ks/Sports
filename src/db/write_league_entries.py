import pandas as pd


from src.db.db import create_connection_engine
from src.utils import League


if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(prog="Writing ALL league participant entries from DB into csv")
    
    parser.add_argument('-g', '--gameweek_id', type= int, required = True, help = "Gameweek you are trying to get a report of")
    parser.add_argument('-dry', '--dry_run', type=bool, help= "Dry run")
    parser.add_argument('-l', '--league_id', type= int, help = "League you are trying to get a report of")
    parser.add_argument('-t', '--thread', type = int)

    args = parser.parse_args()
    league = League(league_id= args.league_id)
    
    entries = []
    entries.append(list(league.get_all_participant_entries(args.gameweek_id)))

    df = pd.DataFrame(data =entries)
    df = df.apply(lambda x: pd.Series(x[0], dtype=object)).T
    
    connection = create_connection_engine("fpl")
    df.to_sql(f"{league.league_name}_{args.gameweek_id}", if_exists='replace', con= connection, index=False, method = 'multi')