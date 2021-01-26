import argparse
import json
import logging
import numpy as np
import pandas as pd

import mysql.connector

from pyspark import SparkConf, SparkContext
from pyspark.sql import Row, SQLContext
from pyspark.sql.types import FloatType, TimestampType


def get_product_information(row, product_attributes):
    """Cleans event details and product information"""

    category_code = row.category_code
    details = category_code.split('.')
    row = row.asDict()
    row['category_code'] = dict(zip(product_attributes, details))
    row['category_code'] = json.dumps(row['category_code'])

    return Row(**row)


def transform_data(sqlContext, user_sessions_chunk_df, product_attributes):
    """Transforms event data before inserting into MySQL table."""

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


def mysql_connection(mysql_database, mysql_user, mysql_user_password):
    """Sets up MySQL connection."""

    mysqlConnection = mysql.connector.connect(
        host="localhost",
        user='{0}'.format(mysql_user),
        password='{0}'.format(mysql_user_password),
        database='{0}'.format(mysql_database)
        # auth_plugin='mysql_native_password'
    )

    return mysqlConnection


def create_table(myCursor, table_name):
    """Creates MySQL table"""

    if table_name=='batch_data':

        drop_if_exists = 'DROP TABLE IF EXISTS {0}'.format(table_name)

        myCursor.execute(drop_if_exists)

        create_batch_data = """
                    
                    CREATE TABLE batch_data ( 
                        record_id INT NOT NULL AUTO_INCREMENT, 
                        event_time DATETIME NOT NULL, 
                        event_type VARCHAR(20) NOT NULL, 
                        product_id VARCHAR(30) NOT NULL, 
                        category_id VARCHAR(30) NOT NULL, 
                        category_code VARCHAR(200) NOT NULL, 
                        brand VARCHAR(30) NOT NULL, 
                        price FLOAT NOT NULL, 
                        user_id VARCHAR(200) NOT NULL, 
                        user_session VARCHAR(200) NOT NULL, 
                        
                        PRIMARY KEY (record_id), 
                        INDEX name (event_time, user_id) 
                    ); 
                """

    myCursor.execute(create_batch_data)


def drop_table(myCursor, table_name):
    """Deletes MySQL table."""

    drop_table = 'DROP TABLE {0}'.format(table_name)

    myCursor.execute(drop_table)


def write_spDF_to_mysql(mysqlConnection, user_sessions_spDF, mysql_database,
                        mysql_table, mysql_user, mysql_user_password):
    """Writes dataframe into MySQL table."""

    # user_sessions_spDF.write.format('jdbc').options(
    #                     url='jdbc:mysql://localhost/{0}'.format(mysql_database),
    #                     driver='com.mysql.jdbc.Driver',
    #                     dbtable='{0}'.format(mysql_table),
    #                     user='{0}'.format(mysql_user),
    #                     password='{0}'.format(mysql_user_password)).mode('overwrite').save()

    user_sessions_spDF.write.format('jdbc').jdbc(
                        url='jdbc:mysql://localhost/{0}'.format(mysql_database),
                        table='{0}'.format(mysql_table),
                        mode = 'overwrite',
                        properties = {
                            'user':'{0}'.format(mysql_user),
                            'password':'{0}'.format(mysql_user_password)}#,
                            # 'driver':'com.mysql.jdbc.Driver'}
                        ).save()


def main():
    """Executes Batch pipeline to store dataset into MySQL table."""

    parser = argparse.ArgumentParser(
        description='Perform Batch processing to send session data to Redis')

    parser.add_argument(
        '--input',
        help='Path to local file. Example: --input C:/Path/To/File/File.csv',
        required=True)

    parser.add_argument(
        '--mysql_database',
        help='MySQL Database Name; Example: --mysql_database batch_processing',
        required=True)

    parser.add_argument(
        '--mysql_table',
        help='MySQL Database Table; Example: --mysql_table batch_data',
        required=True)

    parser.add_argument(
        '--mysql_user',
        help='MySQL Database User; Example: --mysql_user user_admin',
        required=True)

    parser.add_argument(
        '--mysql_user_password',
        help=('MySQL Database Password; Example: --mysql_user_password pass'),
        required=True)
    
    args = parser.parse_args()

    mysqlConnection = mysql_connection(
        args.mysql_database, args.mysql_user, args.mysql_user_password)
    mysqlCursor = mysqlConnection.cursor()

    table_names = [args.mysql_table]
    for table_name in table_names:
        create_table(mysqlCursor, table_name)
        # drop_table(mysqlCursor, table_name)

    logging.info('Reading Dataset')
    user_sessions_chunks_df = pd.read_csv(args.input,
                                    encoding='utf-8', chunksize=int(10**5))

    conf = SparkConf().setAppName(
        "Batch Processing with Spark").setMaster("local")
     
    sc = SparkContext(conf = conf)
    sqlContext = SQLContext(sc)

    product_attributes = ['category', 'sub_category',
    'product','product_details']

    for user_sessions_chunk_df in user_sessions_chunks_df:

        logging.info('Transforming data from the Batch')
        # print(user_sessions_chunk_df.count())
        user_sessions_spDF = transform_data(
            sqlContext, user_sessions_chunk_df, product_attributes)
        # print(user_sessions_spDF.show(n=5))
        # print(column_names)

        logging.info(
            'Loading spDF Data from the Batch into batch_data MySQL Table')
        write_spDF_to_mysql(
            mysqlConnection, user_sessions_spDF, args.mysql_database,
            args.mysql_table, args.mysql_user, args.mysql_user_password)

    logging.info(
        'Finished Loading DF Data from all Batches into batch_data MySQL Table')
    

if __name__ == '__main__':
    main()