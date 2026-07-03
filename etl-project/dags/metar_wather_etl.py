from airflow.decorators import dag, task
from pendulum import datetime 

from include.extract import extract_from_api, extract_from_xml
from include.transform import transform
from include.load import get_connection, load_dataframe

@dag(
    dag_id="weather_etl",
    start_date=datetime(2026,6,30),
    schedule="@hourly",
    catchup=False,
)
def weather_etl():

    @task
    def extract_task():
        responses= extract_from_api()
        return extract_from_xml(responses)

    @task
    def transform_task(df):
        return transform(df)

    @task
    def load_task(df):
        engine = get_connection()
        load_dataframe(df, engine)
        return "Data loaded successfully"

    raw=extract_task()
    clean=transform_task(raw)
    load_task(clean)


weather_etl()