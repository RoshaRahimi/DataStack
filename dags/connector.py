from pyspark.sql import SparkSession
from typing import Dict
from pyspark.sql.functions import to_date, col
from pyspark.sql import functions as F

# define function to create spark session
def create_spark_session(app_name: str, memory_usage: int, minio_config: Dict):
    """
    Create and configure a SparkSession for processing data.

    Args:
        app_name (str): A name for the Spark application.
        memory_usage (int): The amount of memory (in gigabytes) to allocate for the Spark driver.
        minio_config (dict): A dictionary containing MinIO (S3-compatible) configuration parameters.
            It should include the following keys:
            - "access_key" (str): The access key for connecting to MinIO.
            - "secret_key" (str): The secret key for connecting to MinIO.
            - "host" (str): The MinIO host (e.g., "https://minio.example.com").

    Returns:
        SparkSession: A configured SparkSession instance for data processing.
    """

    spark = SparkSession.builder \
        .appName(f"{app_name}") \
        .master("local[*]") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
        .config("spark.driver.memory", f"{memory_usage}g") \
        .config("spark.jars.packages","com.amazonaws:aws-java-sdk:1.12.634,org.apache.hadoop:hadoop-aws:3.2.2,com.clickhouse:clickhouse-jdbc:0.3.2-patch11,mysql:mysql-connector-java:8.0.22")\
        .config("spark.hadoop.fs.s3a.aws.credentials.provider","org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")\
        .config("spark.hadoop.fs.s3a.access.key", minio_config.get("minio_access_key")) \
        .config("spark.hadoop.fs.s3a.secret.key", minio_config.get("minio_secret_key")) \
        .config("spark.hadoop.fs.s3a.endpoint", f"{minio_config.get('minio_host')}:{minio_config.get('minio_port')}") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("fs.s3a.path.style.access", "true") \
        .getOrCreate()
    return spark




#read data from minio
def read_from_minio(spark_instance, bucket_name, topic, date, format):
    year, month, day = date.split("-")
    if format == 'csv':
        result = spark_instance.read.csv(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")
    elif format == 'json':
        result = spark_instance.read.json(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")
    elif format == 'parquet':
        result = spark_instance.read.parquet(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")
    return result

#write data to minio
def write_to_minio(data_frame, bucket_name, topic, date, format):
    year, month, day = date.split("-")
    if format == 'csv':
        data_frame.write.format("csv").save(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")
    elif format == 'json':
        data_frame.write.format("json").save(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")
    elif format == 'parquet':
        data_frame.write.format("parquet").save(f"s3a://{bucket_name}/topics/{topic}/year={year}/month={month}/day={day}/")




#read spark dataframe from clickhouse
def read_spark_dataframe_from_clickhouse(spark_session, clickhouse_config, query: str ):
    dataframe = spark_session.read.format('jdbc') \
                                        .option('driver', 'com.github.housepower.jdbc.ClickHouseDriver') \
                                        .option('url', f"jdbc:clickhouse://{clickhouse_config.get('clickhouse_host')}:{clickhouse_config.get('clickhouse_port')}") \
                                        .option('user', clickhouse_config.get('clickhouse_user')) \
                                        .option('password', clickhouse_config.get('clickhouse_password')) \
                                        .option('query', query).load()
    return dataframe


#write spark dataframe into clickhouse
def write_spark_dataframe_to_clickhouse(dataframe, clickhouse_config, table_name, mode, order_by_col):
    dataframe.write.format('jdbc').mode(mode) \
        .option('driver', 'com.clickhouse.jdbc.ClickHouseDriver') \
        .option('url', f"jdbc:clickhouse://{clickhouse_config.get('clickhouse_host')}:{clickhouse_config.get('clickhouse_port')}") \
        .option('dbtable', table_name) \
        .option('user', clickhouse_config.get('clickhouse_user')) \
        .option('password', clickhouse_config.get('clickhouse_password')) \
        .option('createTableOptions', f'ENGINE = MergeTree() ORDER BY {order_by_col}') \
        .save()


def insert_parquet_into_clickhouse(clickhouse_client, minio_connection, date: str, bucket : str, topic: str, schema: str, table: str ) -> None:
    """
    Insert data from Parquet files stored in a Minio (S3-compatible) bucket into a ClickHouse table.

    Parameters:
    - clickhouse_client (clickhouse_driver.Client): The ClickHouse client object for executing queries.
    - minio_connection (dict): A dictionary containing Minio connection details.
        - 'minio_host' (str): The Minio server hostname.
        - 'minio_port' (int): The Minio server port.
        - 'minio_access_key' (str): Access key for Minio.
        - 'minio_secret_key' (str): Secret key for Minio.
    - date (str): The date in 'YYYY-MM-DD' format indicating the data to be loaded.
    - bucket (str): The bucket name on Minio S3
    - topic (str): The topic or data category from which Parquet files will be loaded.
    - schema (str): The ClickHouse database schema where the target table resides.
    - table (str): The name of the ClickHouse table where data will be inserted.

    Returns:
    None

    This function inserts data from Parquet files located in a Minio bucket into a ClickHouse table.
    The 'date' parameter specifies the date for which data should be loaded, and 'topic' represents the data category.
    The 'schema' and 'table' parameters determine the ClickHouse destination where data will be inserted.
    """
    year, month, day = date.split("-")
    insert_query = f"""INSERT INTO {schema}.{table}
                        SELECT *
                        FROM s3('http://minio:{minio_connection.get("minio_port")}/{bucket}/topics/{topic}/year={year}/month={month}/day={day}/*.parquet', 
                        '{minio_connection.get("minio_access_key")}', 
                        '{minio_connection.get("minio_secret_key")}','Parquet');"""
    clickhouse_client.execute(insert_query)




# define config dictionaries for minio and clickhouse
minio_config = {
    "minio_access_key":"minio_access_key", 
    "minio_secret_key":"minio_secret_key", 
    "minio_host":"http://127.0.0.1",
    "minio_port":"9000"
}

clickhouse_config = {
    "clickhouse_host":'127.0.0.1',
    "clickhouse_port":"8123",
    "clickhouse_user":'admin',
    "clickhouse_password":'123qweasd',
}

