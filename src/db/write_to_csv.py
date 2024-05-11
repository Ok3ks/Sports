"""
Dumps a DB table into CSV using pandas

"""

import gevent
import pandas as pd
import time
import os


from src.db.db import create_connection_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def get_table_content(session = sessionmaker(create_connection_engine('fpl')), table_name = '', rows = 10000):
    with session() as session:
        
        statement_1 = text(f"""SELECT * FROM {table_name} """ )
        # statement_2 = text(f"""SELECT count(id) FROM {table_name}""" )
        obj = session.execute(statement_1).all()
    
    df = pd.DataFrame(obj)
    print(df.head())
    return df 
    

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog="Writing ALL participant entries into DB")
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-ho', '--host', type = str, default= None, help="Database host")
    parser.add_argument('-t', '--table_name', type=str, help="Table Name")

    args = parser.parse_args()

    if not args.host:
        args.host = 'localhost'
    
    engine = create_connection_engine(args.db_name, host=args.host, user=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD"))
    
    #STORAGE PATH AND FILENAME -- Modify appropriately
    HARD_DRIVE = "/Volumes/T7/DB"
    FILE_NAME = f'{args.table_name}.csv'

    df = get_table_content(table_name=args.table_name)

    df.to_csv(os.path.join(HARD_DRIVE, FILE_NAME), header=True)
    print(f"saved {FILE_NAME} to {HARD_DRIVE}")