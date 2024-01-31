CREATE TABLE falafel_db.orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_status VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME NULL
);


CREATE TABLE falafel_db.order_items (
  order_item_id INT PRIMARY KEY,
  order_id int,
  product_id INT,
  quantity INT,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

