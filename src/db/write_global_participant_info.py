from src.utils import get_participant_info
import os


from src.db.db import create_connection_engine,session
import gevent
import pandas as pd
import time

from sqlalchemy import Integer, String, create_engine, select,text,distinct,insert
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session,DeclarativeBase,sessionmaker

from pymysql import Error

class Base(DeclarativeBase):
    pass


class ParticipantInfo(Base):
    __tablename__ = "Participant_info"

    participant_id: Mapped[int] = mapped_column(Integer,primary_key = True)
    participant_first_name: Mapped[str] = mapped_column(String)
    participant_last_name: Mapped[str] = mapped_column(String)

def create_table(conn, table_name = "Participant_info"):

    """ """
    try:
        create_table_sql=text(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            participant_id INTEGER PRIMARY KEY,
                            participant_first_name VARCHAR (255),
                            participant_last_name VARCHAR (200)
                        );
                        """)
        session = sessionmaker(conn)
        with session() as session:
            session.execute(create_table_sql)
        print("Table Created")
    except Error as e:
        print(e)
    return conn

if __name__ == "__main__":

    """
    """
    import argparse

    parser = argparse.ArgumentParser(prog="Writing ALL participant entries into DB")
    parser.add_argument('-db', '--db_name', type = str, help= "Database name", required= True)
    parser.add_argument('-ho', '--host', type = str, default= None, help="Database host")
    parser.add_argument('-s', '--start', type= int, help="Beginning of a range")
    parser.add_argument('-e', '--end', type= int, help= "End of a range")

    args = parser.parse_args()
    if not args.host:
        args.host = 'localhost'
    
    engine = create_connection_engine(args.db_name, host=args.host, user=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD"))
    create_table(engine)

    for n in range(args.start ,args.end,100):
        try:
        #optimum number of spawned threads to 100
            req = [gevent.spawn(get_participant_info, entry_id = i) for i in range(n, n+100, 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
            print(df)
            df.to_sql("Participant_info", engine, if_exists='append',method='multi', index = False)
        except AttributeError:
            time.sleep(10)
            req = [gevent.spawn(get_participant_info, entry_id = i) for i in range(n, n+100, 1)]
            res = [response.value for response in gevent.iwait(req)]
            df = pd.DataFrame(res)
            print(df)
            df.to_sql("Participant_info", engine, if_exists='append',method='multi', index = False)
