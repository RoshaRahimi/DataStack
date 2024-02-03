import random
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector
from time import sleep

###################################################################
# defining connection parameters
config = {
    'user': 'root',
    'password': 'my-secret-pw',
    'host': 'mysql_production',
    'database': 'production_db',
    'port': '3306'
}

#defining CRUD functions

#inseret function
def insert_function(dataframe, table_name, config):
    columns = ', '.join(dataframe.columns)
    values_placeholder = ', '.join(['%s'] * len(dataframe.columns))
    values = [tuple(row) for row in dataframe.values]
    query = f"""
    INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder})
    """
    try:
        connection = mysql.connector.connect(**config)
        print("Connected to MySQL database!")
        mycursor = connection.cursor()
        mycursor.executemany(query, values)
        connection.commit()
        connection.close()
    except mysql.connector.Error as error:
        print(f"Failed to connect to MySQL: {error}")

#read function
def read_function(query):
    try:
        connection = mysql.connector.connect(**config)
        print("Connected to MySQL database!")
        result = pd.read_sql(query, connection)
        return result
    except mysql.connector.Error as error:
        print(f"Failed to connect to MySQL: {error}")


#update function
def update_function(table, columns, values, condition_column, condition_value, config):
    update_query = f"UPDATE {table} SET "
    update_query += ", ".join(f"{column} = %s" for column in columns)
    update_query += f" WHERE {condition_column} = %s"
    print(update_query)
    try:
        connection = mysql.connector.connect(**config)
        print("Connected to MySQL database!")
        mycursor = connection.cursor()
        mycursor.execute(update_query, (*values, condition_value))
        connection.commit()
        connection.close()
    except mysql.connector.Error as error:
        print(f"Failed to connect to MySQL: {error}")

###################################################################################


order_possibilities = \
[
    [1, 2, 4],
    [1, 2, 3, 5, 6],
    [1, 2, 3, 5, 7],
    [1, 2, 3, 5, 7, 9],
    [1, 2, 3, 5, 7, 8],

]

# intervals for creating random date
intervals = [(0, 5), (6 , 11), (12, 17), (18, 23), (24, 29), (30, 35)]

# Generate random orders



def create_order(from_order_id, to_order_id, order_possibilities):
    orders = []
    number_of_orders = to_order_id - from_order_id + 1 
    for order_id in range(from_order_id, to_order_id + 1):
        customer_id = random.randint(1, 10)
        order_status_count = random.randint(0, 4)
        order_status = order_possibilities[order_status_count]
        dates = [datetime.now() + timedelta(minutes=random.randint(i[0], i[1])) for i in intervals[:len(order_status)]]
        hour_shift = timedelta(hours=random.randint(0, 12))
        dates = [i + hour_shift for i in dates]

        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'status_id': order_status,
            'created_at': dates
        }
        orders.append(order)

    orders_df = pd.DataFrame(orders)
    exploded_orders_df = orders_df.explode(['status_id', 'created_at'])
    return exploded_orders_df


def create_order_items(order_item_id_from, order_list):
    order_items = []
    item_id_counter = order_item_id_from  # Initialize the item ID counter
    for order_id in order_list:
        num_items = random.randint(1, 5)  # Random number of items per order
        
        for _ in range(num_items):  # Use "_" as a throwaway variable since the item ID will be generated manually
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 10)
            
            order_item = {
                'order_item_id': item_id_counter,
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity,
            }
            order_items.append(order_item) 
            item_id_counter += 1  # Increment the item ID counter
    
    order_items_df = pd.DataFrame(order_items)
    order_items_df['order_item_id'] = order_items_df.order_item_id.apply(lambda x: str(x))
    order_items_df['order_id'] = order_items_df.order_id.apply(lambda x: str(x))
    order_items_df['product_id'] = order_items_df.product_id.apply(lambda x: str(x))
    order_items_df['quantity'] = order_items_df.quantity.apply(lambda x: str(x))
    
    return order_items_df



def create_order_list(order_df):

    initial_list = []
    for i in list(order_df.order_id.unique()):
        sub_df = order_df[order_df["order_id"]==i]
        initial_list.append(sub_df)
    df_list = initial_list.copy()
    df_list = [df.reset_index() for df in df_list]
    return df_list




def ingestor(orders_list, order_items):
    updated_list = []
    for i in range(6):
        sleep(5)
        for df in orders_list:
            if df.shape[0]>0:
                insert_record = df.head(1)[['order_id', 'customer_id', 'status_id', 'created_at']]
                order_id = insert_record.order_id[0]
                status_id = insert_record.status_id[0]
                creation_date = insert_record.created_at[0]
                if status_id == 1:
                    insert_function(insert_record ,"production_db.orders", config)
                    # order_items_records = order_items_df[order_items_df['order_id']==order_id]
                    # mysql_crud.insert_function(order_items_records, "production_db.order_items", config)
                    sleep(2)
                    insert_function(order_items, "production_db.order_item", config)
                else:
                    update_function(
                        table="production_db.orders", 
                        columns=["status_id", "updated_at"], 
                        values=[status_id, creation_date], 
                        condition_column="order_id", 
                        condition_value= str(order_id), 
                        config = config)

            if df.shape[0] > 1:
                updated_list.append(df.drop(0))
        updated_list = [df.reset_index() for df in updated_list]
        updated_list = [df[['order_id', 'customer_id', 'status_id', 'created_at']] for df in updated_list]
        orders_list = updated_list
        updated_list = []
        





