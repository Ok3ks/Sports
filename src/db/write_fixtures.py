from utils import get_fixtures
import os
from src.db.db import create_connection_engine

if __name__ == "__main__":
    """Dataframe contains all 380 fixtures for a premier league season
    column which checks if game has been completed is finished
    """
    import argparse

    parser = argparse.ArgumentParser(prog="Writing ALL participant entries into DB")
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-ho', '--host', type = str, default= None, help="Database host")
    
    args = parser.parse_args()

    if not args.host:
        args.host = 'localhost'
    
    engine = create_connection_engine(args.db_name, host=args.host, user=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD"))

    fixtures = get_fixtures()
    fixtures.to_sql(name = "Fixtures_table",con=engine,  if_exists="replace")
