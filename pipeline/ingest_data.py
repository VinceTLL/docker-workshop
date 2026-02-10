#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm # monitor progress of wrting data into POSTERDB
import click

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


###########################################################
### Needed to pass parameters to script from command line
#########################################################

@click.command()
@click.option('--user',default = 'root',help ='PostgreSQL user')
@click.option("--password", default = 'root',help = 'PostgreSQL password')
@click.option("--host", default = 'localhost',help = 'PostgreSQL host')
@click.option("--db", default  = 'ny_taxi',help = 'PostgreSQL db')
@click.option("--port", default = 5432,type = int,help = 'PostgreSQL port')
@click.option("--year",  default= 2021,type=int, help = "Year of the data")
@click.option("--month", default= 1,type=int, help = "Month of the data")
@click.option("--target_table",default = "yellow_taxi_data_012021", help = "Target table name")
@click.option("--chunksize",default =100000,type=int, help = "Number of rows of each chunk")


######################################################
### writing data in batch sizes in to postgres DB
#####################################################

def run(
    user, 
    password, 
    host, 
    db,  
    port,
    year,    
    month,
    target_table,
    chunksize):


    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
    url = f"{prefix}yellow_tripdata_{year}-{month:02d}.csv.gz"

    df = pd.read_csv(url,dtype=dtype,parse_dates=parse_dates)

    ##########################################################
    ###  CREATE ENGINE TO INTRACT WITH POSTGRES DB
    #######################################################
    engine  = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    ##########
    #SCHEMA
    #########

    print(pd.io.sql.get_schema(df,name = target_table,con =engine))
 

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

