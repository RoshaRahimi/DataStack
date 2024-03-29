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

---------------------------------------------------------------

DROP TABLE IF EXISTS user;
CREATE TABLE user
(
    id              INTEGER AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(50) NOT NULL,
    address         VARCHAR(200)NULL,
    birthdate       DATETIME    NULL,
    gender          SMALLINT    NOT NULL,
    phone_number    VARCHAR(20) NOT NULL,
    created_at      DATETIME    NOT NULL
);
INSERT  INTO user (first_name, last_name, email,address,birthdate,gender,phone_number,created_at)
VALUES  ('Bahram','Roha','bahram@roha.com','Ir',now(),0,'09051778550',now()),
        ('Rosha','Raha','rosha@raha.com','UK',now(),0,'09051778550',now()),
        ('Sohrab','Eka','sohrab@eha.com','USA',now(),0,'09051778550',now()),
        ('Baran','Bahari','baran@bahari.com','GR',now(),1,'09051778550',now());

DROP TABLE IF EXISTS vendor;
CREATE TABLE IF NOT EXISTS vendor
(
    id          INT UNSIGNED AUTO_INCREMENT  PRIMARY KEY,
    title       VARCHAR(30)                  NOT NULL,
    description VARCHAR(30)                  NOT NULL,
    email       VARCHAR(50)                  NULL,
    address     VARCHAR(100)                 NULL,
    created_at  DATETIME                     NOT NULL
);
INSERT INTO vendor (title,description,email,address,created_at)
VALUES  ('MC Donald','enjoy your food','mc@donald.com','UK',now()),
        ('China Tang','imagine china','china@tang.com','CN',now()),
        ('C London','first quality,best quality','c@london.com','UK',now());


DROP TABLE IF EXISTS order_status;
CREATE TABLE order_status (
    status_id   INT PRIMARY KEY AUTO_INCREMENT,
    title       VARCHAR(255)    NOT NULL,
    description VARCHAR(255)    NOT NULL,
    created_at  DATETIME        NOT NULL,
    updated_at  DATETIME        NULL
);
INSERT INTO order_status (title,description,created_at,updated_at)
VALUES  ('created','created',now(),now()),
        ('wait_to_payment','wait_to_payment',now(),now()),
        ('paied','paied',now(),now()),
        ('payment_cancelled','payment_cancelled',now(),now()),
        ('wait_to_approve','wait_to_approve',now(),now()),
        ('rejected','rejected',now(),now()),
        ('approved','approved',now(),now()),
        ('cancelled','cancelled',now(),now()),
        ('finalized', 'finalized', now(), now());



DROP TABLE IF EXISTS customer;
CREATE TABLE customer
(
    customer_id     INTEGER AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(50)     NOT NULL,
    address         VARCHAR(200)    NOT NULL,
    birthdate       DATETIME        NOT NULL,
    gender          SMALLINT        NOT NULL,
    phone_number    VARCHAR(20)     NOT NULL,
    created_at      DATETIME        NOT NULL
);
INSERT INTO customer(first_name, last_name, email,address,birthdate,gender,phone_number,created_at)
VALUES  ('Rosha','Raha','rosha@raha.com','Ir','2024-01-31 19:42:18',0,'22443321',NOW()),
        ('Mina','Bina','mina@bina.com','UK','2024-01-31 19:42:18',0,'23443321',NOW()),
        ('Mina','Nabina','mina@nabina.com','USA','2024-01-31 19:42:18',0,'24443321',NOW()),
        ('donya','Ava','donya@ava.com','TR','2024-01-31 19:42:18',0,'25443321',NOW()),
        ('maria','db','maria@db.com','GR','2024-01-31 19:42:18',0,'26443321',NOW()),
        ('nazli','Abzi','nazli@abzi.com','FR','2024-01-31 19:42:18',0,'27443321',NOW()),
        ('mahan','aban','mahan@aban.com','SE','2024-01-31 19:42:18',0,'28443321',NOW()),
        ('shahab','sang','shahab@sang.com','FN','2024-01-31 19:42:18',0,'29443321',NOW()),
        ('tala','bala','tala@bala.com','TB','2024-01-31 19:42:18',0,'22433321',NOW()),
        ('mali','bali','mali@bali.com','SW','2024-01-31 19:42:18',0,'22543321',NOW());



DROP TABLE IF EXISTS product;
CREATE TABLE product(
    product_id  INT PRIMARY KEY AUTO_INCREMENT,
    title       NVARCHAR(100)   NOT NULL,
    description NVARCHAR(100)   NULL,
    price       INT             NOT NULL,
    vendor_id   INT             NOT NULL
);
INSERT INTO product(title,description,price,vendor_id)
VALUES  ('sushi','sushi',10,1),
        ('noodle','noodle',10,1),
        ('spaghetti','spaghetti',10,1),
        ('burger','burger',12,2),
        ('sandwich','sandwich',12,2),
        ('peperoni','peperoni',14,2),
        ('hot dog','hot dog',9,3),
        ('mush burger','mush burger',7,3),
        ('salad','salad',3,3),
        ('fries','fries',2,1);


DROP TABLE IF EXISTS production_db.orders;
CREATE TABLE production_db.orders (
    order_id        INT PRIMARY KEY,
    customer_id     INT         NOT NULL,
    status_id       INT         NOT NULL,
    created_at      DATETIME    NOT NULL,
    updated_at      DATETIME    NULL default now(),
    FOREIGN KEY (status_id) REFERENCES order_status(status_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);


DROP TABLE IF EXISTS order_item;
CREATE TABLE order_item (
    order_item_id   INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity           INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES production_db.orders(order_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);
