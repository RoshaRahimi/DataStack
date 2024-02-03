from airflow import DAG
from airflow.decorators import dag, task
from airflow.models import Connection
from datetime import datetime
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection
import pendulum


#defining dag in a decorated way
@dag(
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 21, tz="UTC"),
    catchup=False,
    tags=["test"],
    doc_md = "this is a dag to define tasks for etl data from minio to clickhouse"
)
def ofood_etl():
#defining task in a decorated way
    @task.virtualenv(requirements=["clickhouse-driver", "minio"], doc_md = "this is a task for etl data from minio to clickhouse")
    def extract_transform_phase():
        import pyspark
        import connector as c
        from pyspark.sql.functions import to_date, col
        from pyspark.sql import functions as F
        from airflow.models import Connection
        from pyspark.sql.window import Window
        # from minio import Minio

        #minio_connection = Connection.get_connection_from_secrets('minio_connection')

        minio_connection = Connection.get_connection_from_secrets("minio-connection")

        clickhouse_connection = Connection.get_connection_from_secrets("clickhouse-connection")


        # loading configs
        # minio_config = {
        # "minio_access_key": minio_connection.login,
        # "minio_secret_key": minio_connection.password,
        # "minio_host": minio_connection.extra_dejson.get("minio_host"),
        # "minio_port":minio_connection.extra_dejson.get("minio_port")}

        clickhouse_config = {
        "clickhouse_host": clickhouse_connection.host,
        "clickhouse_port": clickhouse_connection.port,
        "clickhouse_user": clickhouse_connection.login,
        "clickhouse_password": clickhouse_connection.password}

        minio_config = {
        "minio_access_key": "minio_access_key",
        "minio_secret_key": "minio_secret_key",
        "minio_host": "minio",
        "minio_port": 9000}

        # define spark session
        spark_session = c.create_spark_session("ofood_etl", 1, minio_config)


        orders = c.read_from_minio(
                            bucket_name="production", 
                            topic="production.falafel_db.orders",
                            date="2024-01-31",
                            format="parquet",
                            spark_instance=spark_session
                            )

        order_items = c.read_from_minio(
                            bucket_name="production", 
                            topic="production.falafel_db.order_items",
                            date="2024-01-31",
                            format="parquet",
                            spark_instance=spark_session
                            )


        orders = orders.withColumn("created_at_datetime", F.from_unixtime(orders.created_at/1000)) \
            .withColumn("updated_at_datetime", F.from_unixtime(orders.updated_at/1000))
        


        transformed_orders = orders.groupby(["order_id", "created_at_datetime", "customer_id"]) \
        .agg(F.collect_list("order_status").alias("order_status_list"), F.collect_list("updated_at_datetime").alias("updated_at_list")).withColumnRenamed("created_at_datetime", "created_at") 

        transformed_orders.show()
        transformed_order_items = order_items.groupby(["order_id"]).agg(F.collect_list("order_item_id").alias("order_item_id_list"), F.collect_list("product_id").alias("product_id_list"), F.collect_list("quantity").alias("quantity_list"))


        final_order = transformed_orders.join(transformed_order_items, on = "order_id", how="inner")

        final_order.show()

    
        
        # window = Window.partitionBy("order_id").orderBy("date")


        c.write_to_minio(bucket_name="production-transformation",\
                 topic="production.falafel_db.orders",
                 data_frame=final_order,
                 date="2024-01-31",
                 format='parquet'
                 )
            
    
    @task.virtualenv(requirements=["clickhouse-driver"])
    def load_phase():
        import connector as c
        from clickhouse_driver import Client
        
        clickhouse_client = Client(
        host='clickhouse',
        port='9000',
        user='admin',
        password='123qweasd',
        settings={'use_numpy': True})


        minio_config = {
        "minio_access_key": "minio_access_key", #minio_connection.login,
        "minio_secret_key": "minio_secret_key", #minio_connection.password,
        "minio_host":"minio",
        "minio_port":"9000"}


        c.insert_parquet_into_clickhouse(clickhouse_client= clickhouse_client, 
                               minio_connection=minio_config, 
                               date='2024-01-31', 
                               bucket='production-transformation', 
                               topic='production.falafel_db.orders', 
                               schema='default', 
                               table='orders')



    extract_transform_phase() >> load_phase()
    


#calling the dag function
ofood_etl()