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

-----------------------------------------------------------------

---users
CREATE TABLE user_queue
(
    id              Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    birthdate       Nullable(DATETIME64),
    gender          Nullable(Int8),
    phone_number    Nullable(String),
    created_at      Nullable(DATETIME64)
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.user', 'cons_user', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';


CREATE TABLE user
(
    id              Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           String,
    address         String,
    birthdate       Int64,
    gender          Nullable(Int8),
    phone_number    String,
    created_at      Int64
)
    ENGINE = MergeTree()
    ORDER BY (id);


CREATE MATERIALIZED VIEW user_mv to user (
    id              Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    birthdate       Nullable(DATETIME),
    gender          Nullable(Int8),
    phone_number    Nullable(String),
    created_at      Nullable(DATETIME)
    )
AS
SELECT id,
       first_name,
       last_name,
       email,
       address,
       toDateTime(birthdate) as birthdate,
       gender,
       phone_number,
       toDateTime(created_at) as created_at
FROM user_queue;


------------------------------------- vendor
CREATE TABLE vendor_queue
(
    id              Int64,
    title           Nullable(String),
    description     Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    created_at      Nullable(DATETIME64)
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.vendor', 'cons_vendor', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';

CREATE TABLE vendor
(
    id              Int64,
    title           Nullable(String),
    description     Nullable(String),
    email           String,
    address         String,
    created_at      Int64
)
    ENGINE = MergeTree()
    ORDER BY (id);

CREATE MATERIALIZED VIEW vendor_mv to vendor (
    id              Int64,
    title           Nullable(String),
    description     Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    created_at      Nullable(DATETIME)
    )
AS
SELECT id,
       title,
       description,
       email,
       address,
       toDateTime(created_at) as created_at
FROM vendor_queue;



-----------------------------order_status
CREATE TABLE order_status_queue
(
    status_id              Int64,
    title      Nullable(String),
    description       Nullable(String),
    created_at      Nullable(DATETIME64)
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.order_status', 'cons_order_status', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';


CREATE TABLE order_status
(
    status_id       Int64,
    title           Nullable(String),
    description     Nullable(String),
    created_at      Int64
)
    ENGINE = MergeTree()
    ORDER BY (status_id);

CREATE MATERIALIZED VIEW order_status_mv to order_status (
    status_id       Int64,
    title           Nullable(String),
    description     Nullable(String),
    created_at      Nullable(DATETIME)
    )
AS
SELECT status_id,
       title,
       description,
       toDateTime(created_at) as created_at
FROM order_status_queue;



----------------------------------customer
CREATE TABLE customer_queue
(
    customer_id     Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    birthdate       Nullable(DATETIME64),
    gender          Nullable(Int8),
    phone_number    Nullable(String),
    created_at      Nullable(DATETIME64)
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.customer', 'cons_customer', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';

CREATE TABLE customer
(
    customer_id     Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           String,
    address         String,
    birthdate       Int64,
    gender          Nullable(Int8),
    phone_number    String,
    created_at      Int64
)
    ENGINE = MergeTree()
    ORDER BY (customer_id);

CREATE MATERIALIZED VIEW customer_mv to customer (
    customer_id     Int64,
    first_name      Nullable(String),
    last_name       Nullable(String),
    email           Nullable(String),
    address         Nullable(String),
    birthdate       Nullable(DATETIME),
    gender          Nullable(Int8),
    phone_number    Nullable(String),
    created_at      Nullable(DATETIME)
    )
AS
SELECT customer_id,
       first_name,
       last_name,
       email,
       address,
       toDateTime(birthdate) as birthdate,
       gender,
       phone_number,
       toDateTime(created_at) as created_at
FROM customer_queue;


--------------------------------------------product
CREATE TABLE product_queue
(
    product_id              Int64,
    title                   Nullable(String),
    description             Nullable(String),
    price                   Int64,
    vendor_id               Int64
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.product', 'cons_product', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';


CREATE TABLE product
(
    product_id      Int64,
    title           Nullable(String),
    description     Nullable(String),
    price           Int64,
    vendor_id       Int64
)
    ENGINE = MergeTree()
    ORDER BY (product_id);

CREATE MATERIALIZED VIEW product_mv to product (
    product_id      Int64,
    title           Nullable(String),
    description     Nullable(String),
    price           Int64,
    vendor_id       Int64
    )
AS
SELECT product_id,
       title,
       description,
       price,
       vendor_id
FROM product_queue;


---------------------------------------------order
CREATE TABLE order_queue
(
    order_id        Int64,
    customer_id     Int64,
    status_id       Int64,
    created_at      Nullable(DATETIME64),
    updated_at      Nullable(DATETIME64)
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.order', 'cons_order', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';

CREATE TABLE order
(
    order_id        Int64,
    customer_id     Int64,
    status_id       Int64,
    created_at      Int64,
    updated_at      Int64
)
    ENGINE = MergeTree()
    ORDER BY (order_id);


CREATE MATERIALIZED VIEW order_mv to order (
    order_id        Int64,
    customer_id     Int64,
    status_id       Int64,
    created_at      Nullable(DATETIME),
    updated_at      Nullable(DATETIME)
    )
AS
SELECT order_id,
       customer_id,
       status_id,
       toDateTime(created_at) as created_at,
       toDateTime(updated_at) as updated_at
FROM order_queue;





-------------------------------------------------order_item
CREATE TABLE order_item_queue
(
    order_item_id   Int64,
    order_id        Int64,
    product_id      Int64,
    count           Int64
)
    ENGINE = Kafka('kafka-broker:19092', 'production.production_db.order_item', 'cons_order_item', 'AvroConfluent')--'JSONEachRow',--AvroConfluent
        SETTINGS format_avro_schema_registry_url = 'http://schema-registry:8081';

CREATE TABLE order_item
(
    order_item_id   Int64,
    order_id        Int64,
    product_id      Int64,
    count           Int64
)
    ENGINE = MergeTree()
    ORDER BY (order_item_id);


CREATE MATERIALIZED VIEW order_item_mv to order_item (
    order_item_id   Int64,
    order_id        Int64,
    product_id      Int64,
    count           Int64
    )
AS
SELECT order_item_id,
       order_id,
       product_id,
       count
FROM order_item_queue;



