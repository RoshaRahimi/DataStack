# DataStack
DataStack is a Docker Compose project that provides a robust and versatile stack for managing and analyzing data. This stack includes various services to handle different aspects of the data lifecycle.


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


# Connector Configuration:

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

# Converter Configuration:

key.converter: Converter for key serialization (JSON in this case).
value.converter: Converter for value serialization (Avro in this case).
key.converter.schemas.enable and value.converter.schemas.enable: Enable or disable schema inclusion in messages.
value.converter.schema.registry.url: URL for the Avro schema registry.

# Log Retention Configuration:

log.retention.bytes, log.retention.hours, log.retention.minutes, log.retention.ms: Log retention settings.


# Transformations:

transforms: Comma-separated list of transformations to apply.
transforms.unwrap.type: Transformation to unwrap the Debezium message format.
transforms.unwrap.drop.tombstones: Whether to drop tombstone events (set to true). remains deleted records with operation 'd'
transforms.unwrap.add.fields: Additional fields to be added to the unwrapped message (e.g., operation type, timestamps).

# Timestamp Converter:

transforms.TimestampConverter.type: Transformation to convert timestamp format.
transforms.TimestampConverter.field: Field containing the timestamp.
transforms.TimestampConverter.format: Format of the timestamp.
transforms.TimestampConverter.target.type: Target type for the timestamp.

# Snapshot Mode:

snapshot.mode: Specifies how to handle initial snapshotting (set to "initial").