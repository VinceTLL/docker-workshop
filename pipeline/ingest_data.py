#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm # monitor progress of wrting data into POSTERDB


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]




######################################################
### writing data in batch sizes in to postgres DB
#####################################################

def run():

    
    pg_user = 'root'
    pg_password = 'root'
    pg_host = 'localhost'
    pg_db  = 'ny_taxi'
    pg_port = 5432

    year = 2021
    month = 1

    target_table = "yellow_taxi_data"


    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
    url = f"{prefix}yellow_tripdata_{year}-{month:02d}.csv.gz"

    df = pd.read_csv(url,dtype=dtype,parse_dates=parse_dates)

    ##########################################################
    ###  CREATE ENGINE TO INTRACT WITH POSTGRES DB
    #######################################################
    engine  = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    
    ##########
    #SCHEMA
    #########

    print(pd.io.sql.get_schema(df,name = target_table,con =engine))
 
    
    chunksize = 100000

    #create chuncks iterator
    df_iter  = pd.read_csv(url, dtype=dtype, parse_dates=parse_dates,iterator=True,chunksize = chunksize)
    
    first = True

    for chunk in tqdm(df_iter):

        if first:
             
             ##CREATE TABLE IN POSTGRES SQL IF DOES NOT EXISTS
             #if the table with the below name exists we replaces it by using if_exists  = 'replace'

            chunk.head(0).to_sql(name= target_table, con=engine, if_exists='replace')
            first = False
        chunk.to_sql(name=target_table, con=engine, if_exists='append')


if __name__== '__main__':

    run()

