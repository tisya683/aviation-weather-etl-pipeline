import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os
import logging 


logger=logging.getLogger(__name__)

user=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")
host=os.getenv("DB_HOST")
port=os.getenv("DB_PORT")
database=os.getenv("DB_DATABASE")

#create engine

def get_connection():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=database,#cos password contains @ and im too lazy to change
    )
    return create_engine(url)

# load dataframe
def load_dataframe(df,engine):
   try:
       
      df.to_sql(
         name='weather_hourly',
         con=engine,
         if_exists='append',
         index=False
   )
      logger.info(f"no.of rows added:{len(df)}")
   
   except Exception:
      logger.exception("Failed to load data into PostgreSQL")
      raise

   return df

'''if __name__=='__main__':
    try:
      engine=get_connection()
      print("connection is successful")
    except Exception as ex:
       print(f"type error:{ex}")'''





