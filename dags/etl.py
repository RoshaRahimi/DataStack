from airflow.decorators import dag, task
from airflow.models import Connection
from datetime import datetime
from pyspark.sql import functions as F
from airflow.hooks.base_hook import BaseHook
import pendulum
from airflow.operators.python import get_current_context
import connector as c
from pyspark.sql.functions import to_date, col
from pyspark.sql.window import Window
from clickhouse_driver import Client



#defining dag in a decorated way
@dag(
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 21, tz="UTC"),
    catchup=False,
    doc_md = "this is a dag to define tasks for etl data from minio to clickhouse"
)
def etl():
#defining task in a decorated way
    @task
    def extract_transform_phase():
        pass
        
        context = get_current_context()
        context_execution_date = context['execution_date'].format('YYYY-MM-DD')

        minio_connection = Connection.get_connection_from_secrets("minio-connection")



        minio_config = {
        "minio_access_key": minio_connection.login,
        "minio_secret_key": minio_connection.password,
        "minio_host": minio_connection.extra_dejson.get("minio_host"),
        "minio_port":minio_connection.extra_dejson.get("minio_port")}


        # define spark session
        spark_session = c.create_spark_session("ofood_etl", 1, minio_config)

        orders = c.read_from_minio(
                            bucket_name = "production", 
                            topic = "production.production_db.orders",
                            date = context_execution_date,
                            format = "parquet",
                            spark_instance = spark_session
                            ) 

        orders = orders.withColumn("created_at_datetime", F.from_unixtime(orders.created_at/1000)) \
            .withColumn("updated_at_datetime", F.from_unixtime(orders.updated_at/1000))
        
        order_item = c.read_from_minio(
                            bucket_name = "production", 
                            topic = "production.production_db.order_item",
                            date = context_execution_date,
                            format = "parquet",
                            spark_instance=spark_session
                            )


        

        transformed_orders = orders.groupby(["order_id", "created_at_datetime", "customer_id"]) \
        .agg(F.collect_list("status_id").alias("order_status_id_list"), F.collect_list("updated_at_datetime").alias("updated_at_list")).withColumnRenamed("created_at_datetime", "created_at") 


        transformed_order_item = order_item.groupby(["order_id"]).agg(F.collect_list("order_item_id").alias("order_item_id_list"), F.collect_list("product_id").alias("product_id_list"), F.collect_list("quantity").alias("quantity_list"))


        final_order = transformed_orders.join(transformed_order_item, on = "order_id", how="inner")

    
        
        # window = Window.partitionBy("order_id").orderBy("date")


        c.write_to_minio(bucket_name="production-transformation",\
                 topic="production.production_db.orders",
                 data_frame = final_order,
                 date = context_execution_date,
                 format = 'parquet'
                 )
            
    
    @task
    def load_phase():
        
        context = get_current_context()
        context_execution_date = context['execution_date'].format('YYYY-MM-DD')

        clickhouse_connection = Connection.get_connection_from_secrets("clickhouse-connection")
        
        clickhouse_client = Client(
        host = clickhouse_connection.host,
        port = clickhouse_connection.port,
        user = clickhouse_connection.login,
        password = clickhouse_connection.password,
        settings={'use_numpy': True})


        minio_connection = Connection.get_connection_from_secrets("minio-connection")

        minio_config = {
        "minio_access_key": minio_connection.login,
        "minio_secret_key": minio_connection.password,
        "minio_host": minio_connection.extra_dejson.get("minio_host"),
        "minio_port":minio_connection.extra_dejson.get("minio_port")}


        c.insert_parquet_into_clickhouse(clickhouse_client = clickhouse_client, 
                               minio_connection = minio_config, 
                               date = context_execution_date, 
                               bucket = 'production-transformation', 
                               topic = 'production.production_db.orders', 
                               schema = 'default', 
                               table = 'orders')



    extract_transform_phase() >> load_phase()
    



etl()