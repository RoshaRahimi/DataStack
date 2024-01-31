drop table if exists orders_queue
create table orders_queue
(
    order_id     Nullable(Int64),
    customer_id  Nullable(Int64),
    order_status Nullable(String),
    created_at   Nullable(String) ,
    updated_at   Nullable(Int64)
)
ENGINE = Kafka('kafka-broker:19092', 'production.falafel_db.orders', 'cons_orders', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
    SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';

drop table if exists orders
CREATE TABLE orders
(
    order_id     Int64,
    customer_id  Nullable(Int64),
    order_status Nullable(String),
    created_at   Nullable(String),
    updated_at   Nullable(Int64)
)
    ENGINE = ReplacingMergeTree(order_id)

    ORDER BY (order_id);


drop table if exists orders_mv
CREATE MATERIALIZED VIEW orders_mv to orders (
    order_id     Int64,
    customer_id  Nullable(Int64),
    order_status Nullable(String),
    created_at   Nullable(String),
    updated_at   Nullable(Int64)
    )
AS
SELECT
    order_id,
    customer_id,
    order_status,
    created_at,
    toDateTime64(updated_at, 3) as updated_at
FROM orders_queue;
