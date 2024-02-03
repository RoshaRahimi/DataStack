# DataStack
DataStack
DataStack is a comprehensive Docker Compose project designed to provide a robust and versatile stack for managing and analyzing data. This stack brings together various services, each playing a crucial role in different stages of the data lifecycle.

## Overview
In the ever-evolving landscape of data management and analytics, DataStack stands out as a powerful solution. Leveraging Docker Compose, this project seamlessly integrates different services to handle various aspects of the data journey, from ingestion to analysis. This project contains different services, and its architecture can be divided into four parts:

- Ingestion: There is a Python script that serves as an ingestor to ingest sample data into the MySQL database, which serves as the production database.

- Change Data Capture: Changes in the data are captured using Debezium and stored in Kafka topics.

- Live Data Access Access: The ClickHouse database connects to Kafka to read data from the topics. Based on the data, some views are created to provide live insights.

- Historical Data: Initially, the data is stored in MinIO. Then, a PySpark application extracts and transforms the data, loading it into another bucket in MinIO. Finally, another PySpark application loads this transformed data directly from MinIO into ClickHouse as historical data.

## Kafka and Debezium
DataStack relies on Apache Kafka and Debezium for its data streaming and change data capture capabilities. Kafka, a distributed event streaming platform, provides a scalable and fault-tolerant foundation for real-time data processing. Debezium, a distributed platform for CDC, enables the streaming of database changes into Kafka topics, ensuring a reliable and up-to-date data pipeline.

The decision to use Kafka and Debezium was driven by the need for a robust and scalable solution to handle data changes in real-time. These technologies empower DataStack to keep data flowing seamlessly across different components of the ecosystem.

## MySQL and Minio
DataStack integrates MySQL as a source database and Minio as a cloud storage solution. MySQL, a widely used relational database, serves as a dependable source for data, and Debezium captures changes from MySQL for streaming into Kafka. Minio, an object storage system compatible with Amazon S3, acts as a versatile sink for storing and managing data.

The choice of MySQL and Minio within the ecosystem ensures compatibility, flexibility, and scalability. MySQL, with its reliability and ACID compliance, serves as a trustworthy source for data. Minio, being S3-compatible, allows seamless integration with a variety of applications and tools in the cloud ecosystem.

The synergy between MySQL and Minio in DataStack enhances the overall data management experience, enabling efficient sourcing and storage of data. The reliability of MySQL coupled with the versatility of Minio provides a solid foundation for a wide range of data-driven applications and use cases.

DataStack is designed with the understanding that effective data management goes beyond storage and retrieval. It encompasses the entire data lifecycle, from the initial capture of changes to real-time streaming and ultimately to storage in a resilient and scalable cloud environment.

Whether you're dealing with data ingestion, transformation, or analysis, DataStack offers a comprehensive solution, allowing you to focus on deriving insights from your data rather than managing the intricacies of the underlying infrastructure.

Stay tuned for further details on installation, usage, and contributing guidelines as DataStack evolves to meet the diverse needs of data professionals and enthusiasts alike.

## Airflow and Python Jobs
In this project, we have utilized Apache Airflow, an open-source platform for orchestrating, scheduling, and monitoring workflows, to handle the batch processing component. There are two primary DAGs in this project. The first DAG, mysql_ingestor.py, is responsible for ingesting data into the MySQL production database every five minutes. The second DAG, etl.py, implements the ETL (Extract, Transform, Load) process to provide historical data and perform daily operations the transformation process are handled by Pyspark and the connection info are defined and handled in airflow connection part. Before running the containers, it is necessary to configure the settings for Apache Airflow. Additionally, it is important to ensure that the environment is properly configured for the Docker Compose setup. 

<pre>
    mkdir -p ./dags ./logs ./plugins ./config
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    docker compose up airflow-init
</pre>

## ClickHouse
DataStack leverages ClickHouse as a powerful data warehousing solution. ClickHouse efficiently fetches data from Kafka and stores it in materialized views, enabling the generation of insightful reports. As a columnar database, ClickHouse excels at handling analytical queries, making it an ideal choice for data warehousing within the DataStack ecosystem.

The incorporation of ClickHouse further enhances DataStack's capabilities, providing a scalable and high-performance solution for storing and analyzing large volumes of data. Stay tuned for more details on installation, usage, and contributing guidelines as DataStack evolves to meet the diverse needs of data professionals and enthusiasts alike.



![Alt text](https://github.com/RoshaRahimi/DataStack/blob/main/image/datastack-2024-02-01-00-55-Page-1.jpg)




when start using mysql as a source, you have to set a root permission in mysql, it helps to avoid raising permission error when running connector creator command for mysql.

<pre>
GRANT GRANT OPTION ON *.* TO 'root'@'localhost';
</pre>

after running docker compose file, you will have kafka-ui to see the status of connectors include sinks and sources and schema-registry and messages
you need to add some commans in kafka-connect to have debezium connector install. this is the command to install mysql debezium connector

<pre>
docker container exec -it kafka-connect /bin/bash
</pre>

<pre>
confluent-hub install --no-prompt debezium/debezium-connector-mysql:latest
</pre>

after instlling debezium connector you need to reset kafka-connect

<pre>
docker restart kafka-connect
</pre>

command to create minio sink connector

<pre>
curl http://localhost:8083/connectors -i -X POST -H "Content-Type:application/json" -d "@/connectors/minio-sink.properties"
</pre>

command to create mysql source connector

<pre>
curl http://localhost:8083/connectors -i -X POST -H "Content-Type:application/json" -d "@/connectors/mysql-source.properties"
</pre>

now we have a source connector to mysql that get messages from it and have a sink connector to minio to consume messages from mysql.


this is the mysql connector that we have, let see how it does work:

{
    "name": "mysql-source-v55", 
    "config": {
        "connector.class": "io.debezium.connector.mysql.MySqlConnector", 
        "database.hostname": "mysql_falafel", 
        "database.port": "3306", 
        "database.user": "root", 
        "database.password": "my-secret-pw", 
        "database.server.id": "1", 
        "topic.prefix": "production", 
        "schema.history.internal.kafka.bootstrap.servers": "kafka-broker:19092", 
        "schema.history.internal.kafka.topic": "dbhistory.production", 
        "include.schema.changes": "false",

        "key.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter": "io.confluent.connect.avro.AvroConverter",
        "key.converter.schemas.enable": "false",
        "value.converter.schemas.enable": "true",
        "value.converter.schema.registry.url": "http://schema-registry:8081",

        "log.retention.bytes":"-1",
        "log.retention.hours":"168",       
        "log.retention.minutes":"null",
        "log.retention.ms":"-1",
        
        "transforms": "unwrap,TimestampConverter",
        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "transforms.unwrap.drop.tombstones": "true",
        "transforms.unwrap.add.fields": "op,source.ts_ms:EVENT_TS,ts_ms:KAFKA_EVENT_TS",

        "transforms.TimestampConverter.type": "org.apache.kafka.connect.transforms.TimestampConverter$Value",
        "transforms.TimestampConverter.field": "created_at",
        "transforms.TimestampConverter.format": "yyyy-MM-dd HH:mm:ss",
        "transforms.TimestampConverter.target.type": "string",

        "snapshot.mode": "initial"
    }
}


### Connector Configuration:

connector.class: Specifies the class implementing the connector, in this case, it's the Debezium MySQL Connector.
database.hostname: The hostname of the MySQL server. actually it is the name of mysql service in docker compose file
database.port: The port on which the MySQL server is running.
database.user and database.password: Credentials for connecting to the MySQL server.
database.server.id: A unique identifier for this MySQL server instance in the Debezium cluster.
topic.prefix: Prefix for Kafka topics to which changes will be streamed.
schema.history.internal.kafka.bootstrap.servers: Kafka bootstrap servers for internal schema history tracking.
schema.history.internal.kafka.topic: Kafka topic for storing internal schema history.
include.schema.changes: Whether to include schema changes in the streaming events (set to false).
The include.schema.changes configuration parameter in the Debezium MySQL Connector controls whether the streaming events sent to Apache Kafka should include information about changes to the database schema. When include.schema.changes is set to false, it means that the connector will not include information about alterations to the database schema in the messages that it sends to Kafka topics.

### Converter Configuration:

key.converter: Converter for key serialization (JSON in this case).
value.converter: Converter for value serialization (Avro in this case).
key.converter.schemas.enable and value.converter.schemas.enable: Enable or disable schema inclusion in messages.
value.converter.schema.registry.url: URL for the Avro schema registry.

### Log Retention Configuration:

log.retention.bytes, log.retention.hours, log.retention.minutes, log.retention.ms: Log retention settings.


### Transformations:

transforms: Comma-separated list of transformations to apply.
transforms.unwrap.type: Transformation to unwrap the Debezium message format.
transforms.unwrap.drop.tombstones: Whether to drop tombstone events (set to true). remains deleted records with operation 'd'
transforms.unwrap.add.fields: Additional fields to be added to the unwrapped message (e.g., operation type, timestamps).

### Timestamp Converter:

transforms.TimestampConverter.type: Transformation to convert timestamp format.
transforms.TimestampConverter.field: Field containing the timestamp.
transforms.TimestampConverter.format: Format of the timestamp.
transforms.TimestampConverter.target.type: Target type for the timestamp.

### Snapshot Mode:

snapshot.mode: Specifies how to handle initial snapshotting (set to "initial").
