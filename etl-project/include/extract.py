import pandas as pd
import requests
from requests import Response
import datetime as dt
import numpy as np
from typing import Dict,Optional
import logging

logger=logging.getLogger(__name__)

BASE_URL="https://aviationweather.gov/api/data/metar?"

ICAO_CODES=["WSSS","WSAP","WSSL"]

DEFAULT_PARAMS={
    "format": 'json',
    "taf": 'false',
    'hour': 1
}

#helper function 1
def get_api_response(base_url: str , params: dict, code: str)->Optional[Response]:
    params['ids'] = code
    try:
        return requests.get(base_url, params=params,timeout=10)
    except Exception as e:
        logger.error(f"error due to: {e}")
        return None

#helper function 2
def response_to_json(response: Optional[Response], code:str):
    if response and response.status_code == 200:  
        logger.info(f"Data successfully retrieved for {code}")
        return response.json()
    else:
        logger.error(f"Error in retrieving data for {code}")
        return None  

#main function
def extract_from_api()-> list:
    responses= []   
    for code in ICAO_CODES:
        response = get_api_response(BASE_URL, DEFAULT_PARAMS.copy(), code)   # use .copy() to avoid mutation
        data = response_to_json(response, code)
        if data is not None:
            responses.extend(data)   
    logger.info(f"Total extracted responses: {len(responses)}")
    return responses

#transform function
def extract_from_xml(responses: list)-> pd.DataFrame:
    '''converting json to a format that is parsable by pandas'''
    records = []   # must be defined before append
    for val in responses:   
        records.append({
            "icao_id": val['icaoId'],
            "name": val["name"],
            'report_time': val['reportTime'],
            "temperature": val["temp"],
            "dew_point": val.get('dewp'),
            "wind_direction": val.get("wdir"),
            "wind_speed": val.get("wspd"),
            'visibility': val.get('visib', 0),
            "rawOb": val.get("rawOb"),
            "flight_category": val.get("fltCat"),
            "overall_cover": val.get("cover"),
        })

    df = pd.DataFrame(records) 
    logger.info(df["visibility"].unique())
    df=normalize_cols(df)
    return df


def normalize_cols(df: pd.DataFrame)-> pd.DataFrame: #pyarrow needs each column to have uniform types 
    df["visibility"]=df["visibility"].astype(str).str.strip().str.replace("+","",regex=False) #convert everything to string first and remove + char
    df['wind_variable']=df['wind_direction'] == 'VRB' # wind_direction can be 'VRB' (variable) instead of a number since wind direction has numeric tpes

   #precautionary measure for the rest of the cols

    numeric_cols =["temperature", "dew_point", "wind_direction", "wind_speed", "visibility"]
    for col in numeric_cols:
        df[col]=pd.to_numeric(df[col], errors="coerce")
        coerced=df[col].isna().sum()
        if coerced:
            logger.info(f"{coerced} '{col}' values could not be parsed and were set to NaN")

    # datetime
    df["report_time"]=pd.to_datetime(df["report_time"], errors="coerce")


    string_cols=["icao_id", "name", "rawOb", "flight_category", "overall_cover"]
    for col in string_cols:
        df[col]=df[col].fillna("").astype(str)

    return df



    