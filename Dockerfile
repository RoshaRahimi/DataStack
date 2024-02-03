FROM apache/airflow:2.8.1
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" apache-airflow-providers-apache-spark==2.1.3
RUN pip install airflow-providers-clickhouse
RUN pip install mysql-connector-python
RUN pip install clickhouse-driver
RUN pip install minio


#FROM confluentinc/cp-kafka-connect-base:latest-ubi8

#ENV CONNECT_PLUGIN_PATH: "/usr/share/java,/usr/share/confluent-hub-components"
#ENV CLASSPATH="/usr/share/confluent-hub-components/java/*:${CLASSPATH}"

#RUN echo "Installing Connector"
#RUN confluent-hub install --no-prompt debezium/debezium-connector-mysql:latest

# COPY ./entrypoint.sh .

# ENTRYPOINT [ "./entrypoint.sh" ]
