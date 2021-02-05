import argparse
import json
import logging
import numpy as np
import pandas as pd

import redis

from pyspark import SparkConf, SparkContext
from pyspark.sql import Row, SQLContext
from pyspark.sql.types import FloatType, TimestampType


def get_product_information(row, product_attributes):
    """Cleans event details and product information."""

    category_code = row.category_code
    details = category_code.split('.')
    row = row.asDict()

    row['category_code'] = dict(zip(product_attributes, details))
    row['category_code'] = json.dumps(row['category_code'])
    row['event_details'] = str(row['event_time']) +' | '+ row['user_id']

    return Row(**row)


def transform_data(sqlContext, user_sessions_chunk_df, product_attributes):
    """Transforms event data before inserting into Redis table."""

    # Column-level transformations quicker with Spark Dataframes than RDDs
    user_sessions_spDF = sqlContext.createDataFrame(
        user_sessions_chunk_df.astype(str))
    user_sessions_spDF.fillna(np.nan)
    user_sessions_spDF = user_sessions_spDF.withColumn(
        'event_time', user_sessions_spDF['event_time'].cast(TimestampType()))
    user_sessions_spDF = user_sessions_spDF.withColumn(
        'price', user_sessions_spDF['price'].cast(FloatType()))

    # Some element-wise or row-wise operations are better with RDDs
    user_sessions_rdd = user_sessions_spDF.rdd.map(list)
    # print(user_sessions_rdd.take(5))
    user_sessions_rdd = user_sessions_spDF.rdd.map(
        lambda row: get_product_information(row, product_attributes))

    user_sessions_spDF = user_sessions_rdd.toDF()

    return user_sessions_spDF


def write_to_redis(redis_connection, user_sessions_spDF):
    """Writes dataframe into Redis table."""

    user_sessions = user_sessions_spDF.toPandas()
    
    for index, row in user_sessions.iterrows():
        # print(row['category_code'])
        
        hash_name = row['event_details'] + ' | ' + str(index+1)        

        redis_connection.hset(hash_name, 'event_time', str(row['event_time']))
        redis_connection.hset(hash_name, 'event_type', row['event_type'])
        redis_connection.hset(hash_name, 'product_id', row['product_id'])
        redis_connection.hset(hash_name, 'category_id', row['category_id'])
        redis_connection.hset(hash_name, 'category_code', row['category_code'])
        redis_connection.hset(hash_name, 'brand', row['brand'])
        redis_connection.hset(hash_name, 'price', row['price'])
        redis_connection.hset(hash_name, 'user_id', row['user_id'])
        redis_connection.hset(hash_name, 'user_session', row['user_session'])


def clear_redis_database(redis_connection):
    """Deletes Redis Table."""

    redis_connection.flushdb()


def main():
    """Executes Batch pipeline to store dataset into Redis table."""

    parser = argparse.ArgumentParser(
        description='Perform Batch processing to send session data to Redis')

    parser.add_argument(
        '--input',
        help='Path to local file. Example: --input C:/Path/To/File/File.csv',
        required=True)

    parser.add_argument(
        '--port',
        help='Port to listen to Redis. Example: --port 6379',
        type=int,
        required=True)

    args = parser.parse_args()

    logging.info('Reading Dataset')
    user_sessions_chunks_df = pd.read_csv(args.input,
                                    encoding='utf-8', chunksize=int(10**5))

    conf = SparkConf().setAppName(
        "Batch Processing with Spark").setMaster("local")
     
    sc = SparkContext(conf = conf)
    sqlContext = SQLContext(sc)

    logging.info('Initializing Redis Connection')
    redis_connection = redis.Redis(host='127.0.0.1', port=args.port, db=0)

    clear_redis_database(redis_connection)

    product_attributes = ['category', 'sub_category',
    'product','product_details']

    for user_sessions_chunk_df in user_sessions_chunks_df:

        logging.info('Transforming data from the Batch')
        # print(user_sessions_chunk_df.count())
        user_sessions_spDF = transform_data(
            sqlContext, user_sessions_chunk_df, product_attributes)
        # print(user_sessions_spDF.show(n=5))
        # print(column_names)

        logging.info('Loading DF Data from the Batch into Redis Database')
        write_to_redis(redis_connection, user_sessions_spDF)
    
    logging.info(
        'Finished Loading DF Data from all Batches into Redis Database')
    
    # Deletes Redis Database
    # clear_redis_database(redis_connection)


if __name__ == '__main__':
    main()