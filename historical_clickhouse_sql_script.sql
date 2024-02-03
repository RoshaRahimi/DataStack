DROP TABLE IF EXISTS default.orders
CREATE TABLE default.orders(
    order_id Int64,
    created_at Datetime64,
    customer_id Int64,
    order_status_id_list Array(String),
    updated_at_list Array(String),
    order_item_id_list Array(Int64),
    product_id_list Array(Int64),
    quantity_list Array(Int64)
)
Engine = MergeTree()
order by order_id;
