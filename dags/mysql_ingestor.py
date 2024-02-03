from airflow import DAG
from airflow.decorators import dag, task
from airflow.models import Connection
from datetime import datetime
import pendulum
from airflow.operators.python import get_current_context
from ingestor import create_order, create_order_items, create_order_list, ingestor



#defining dag in a decorated way
@dag(
    schedule= None, #"*/2 * * * *",
    start_date=pendulum.datetime(2024, 1, 21, tz="UTC"),
    catchup=False,
    tags=["test"],
    doc_md = "this is a dag to define tasks for etl data from minio to clickhouse"
)
def mysql_ingestor():
#defining task in a decorated way
    @task 
    def ingestion():
        from ingestor import create_order, create_order_items, create_order_list, ingestor
        context = get_current_context()
        context_execution_date = context['execution_date']
        date_diff = context_execution_date.diff(pendulum.datetime(2024, 1, 31, 0, 0, 0)).in_minutes()
        
        order_possibilities = \
        [
            [1, 2, 4],
            [1, 2, 3, 5, 6],
            [1, 2, 3, 5, 7],
            [1, 2, 3, 5, 7, 9],
            [1, 2, 3, 5, 7, 8],

        ]

        orders = create_order(date_diff, date_diff + 1, order_possibilities)

        order_items = create_order_items(date_diff, list(orders.order_id.unique()))

        orders_list = create_order_list(orders)

        print(orders)

        # print(order_items)

        print(orders_list)

        ingestor(orders_list, order_items)


    ingestion()


#calling the dag function
mysql_ingestor()