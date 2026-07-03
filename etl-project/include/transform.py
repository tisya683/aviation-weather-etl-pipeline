import pandas as pd
import datetime as dt
import numpy as np
import logging

logger=logging.getLogger(__name__)


#change name and airport 
def location_names(df):
    df["country"]=df["name"].str.extract(r"([^/]+)",expand=False)
    df["airport_name"] = (df["name"]
                          .str.extract(r"/([^,]+)",expand=False)
                          .replace({
                            "Changi Intl":"Changi",
                            "Pays":"Paya Lebar",
                            "Seletar Arpt":"Seletar"
                            }))
    return df

#change to SGT
def utc_to_sgt(df):
    df["report_time"]=pd.to_datetime(df["report_time"],utc=True).dt.tz_convert("Asia/Singapore")
    return df

#extract date and time
def date_and_time(df):
    df["date"]=df["report_time"].dt.date
    df["time"]=df["report_time"].dt.time
    return df


# change visibility from miles to km
def miles_to_km(df):
    df["visibility"]=(df["visibility"]
    .astype(str)
    .str.replace("+",' ',regex=False)
    .pipe(pd.to_numeric,errors="coerce")
    .mul(1.60934)
    .pipe(np.ceil))
    return df

#from raw obs extract weather and convert it to a col
def rawOb_to_weather(df):
    descriptors=r"(MI|PR|BC|DR|BL|SH|TS|FZ|VC)"
    phenomena=r"(RA|DZ|BR|FG|HZ|FU|VA|SA|DU|SQ|FC|PO)"
    df["weather_phenomenon"]=df["rawOb"].str.extract(phenomena)
    df["descriptors"]=df["rawOb"].str.extract(descriptors)
    return df


#seperate string and num for wind direction
def variable_wind_direction(df):
    df["wind_direction_var"]=df["wind_direction"].eq("VRB").astype(int)
    df.loc[df["wind_direction"]=="VRB","wind_direction"]=np.nan
    return df

#create unique id
def create_unique_id(df):
    df["unique_id"]=(
    df["rawOb"].str.split().str[1]
    +"_"+
    df["rawOb"].str.split().str[2].str.replace("Z"," "))
    return df

#drop name,rawOb and report_time cols
def drop_cols(df):
    return df.drop(columns=["name","rawOb","report_time"])

#main transform function:
def transform(df):
    logger.info("transformation has started")
    df=location_names(df)
    logger.info("location names successfully extracted")
    df=utc_to_sgt(df)
    logger.info("time changed")
    df=date_and_time(df)
    logger.info("date and time extracted")
    df=miles_to_km(df)
    logger.info("converted to km")
    df=rawOb_to_weather(df)
    logger.info("weather extracted")
    df=variable_wind_direction(df)
    logger.info("wind direction recorded")
    df=create_unique_id(df)
    logger.info("unique id created")
    df=drop_cols(df)
    rows,cols=df.shape
    logger.info(f"transformation complete- rows:{rows},cols:{cols}")
    return df 