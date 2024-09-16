FROM bitnami/spark:3.5.2

USER root

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN pip install google-cloud-storage google-auth google-auth-oauthlib google-auth-httplib2

ENV GCS_CONNECTOR_JAR_URL=https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar
ENV HADOOP_COMMON_LIB_JARS_DIR=/opt/bitnami/spark/jars

RUN curl -o ${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar ${GCS_CONNECTOR_JAR_URL}

#COPY --chown=1001:root jars/gcs-connector-hadoop3-latest.jar ${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar
#COPY jars/gcs-connector-hadoop3-latest.jar ${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar

RUN chmod 644 ${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar

USER 1001

RUN echo "export HADOOP_CLASSPATH=\$HADOOP_CLASSPATH:${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar" >> /opt/bitnami/spark/conf/spark-env.sh
RUN echo "export SPARK_JARS=${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar" >> /opt/bitnami/spark/conf/spark-env.sh
RUN echo "export SPARK_DIST_CLASSPATH=\$SPARK_DIST_CLASSPATH:${HADOOP_COMMON_LIB_JARS_DIR}/gcs-connector-hadoop3-latest.jar" >> /opt/bitnami/spark/conf/spark-env.sh
RUN echo "export SPARK_SUBMIT_OPTIONS='--conf spark.hadoop.fs.gs.impl=com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem --conf spark.hadoop.google.cloud.auth.service.account.enable=true'" >> /opt/bitnami/spark/conf/spark-env.sh

