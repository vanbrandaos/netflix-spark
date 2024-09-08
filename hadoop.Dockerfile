FROM eclipse-temurin:8-jdk-focal
RUN apt-get update -y \
    && export DEBIAN_FRONTEND=noninteractive && apt-get install -y --no-install-recommends \
        sudo \
        curl \
        ssh \
    && apt-get clean
RUN useradd -m hduser && echo "hduser:supergroup" | chpasswd && adduser hduser sudo && echo "hduser     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && cd /usr/bin/ && sudo ln -s python3 python
COPY hadoop-volumes/ssh_config /etc/ssh/ssh_config

WORKDIR /home/hduser
USER hduser
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 0600 ~/.ssh/authorized_keys

ENV HADOOP_VERSION=3.2.1

#COPY hadoop-${HADOOP_VERSION}.tar.gz /home/hduser/

RUN curl -sL --retry 3 \
  "http://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
  | gunzip \
  | tar -x -C /home/hduser/ \
 && rm -rf ${HADOOP_HOME}/share/doc

RUN tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /home/hduser/ \
 && rm -rf /home/hduser/hadoop-${HADOOP_VERSION}/share/doc \
 && mkdir -p /home/hduser/hadoop-${HADOOP_VERSION} \
 && chown -R hduser:hduser /home/hduser/hadoop-${HADOOP_VERSION} \
 && rm /home/hduser/hadoop-${HADOOP_VERSION}.tar.gz

RUN mv /home/hduser/hadoop-${HADOOP_VERSION} /home/hduser/hadoop
ENV HADOOP_HOME /home/hduser/hadoop

ENV HDFS_NAMENODE_USER hduser
ENV HDFS_DATANODE_USER hduser
ENV HDFS_SECONDARYNAMENODE_USER hduser

ENV YARN_RESOURCEMANAGER_USER hduser
ENV YARN_NODEMANAGER_USER hduser

RUN echo "export JAVA_HOME=/opt/java/openjdk/" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
#COPY hadoop-volumes/namenode/core-site.xml $HADOOP_HOME/etc/hadoop/
#COPY hadoop-volumes/namenode/hdfs-site.xml $HADOOP_HOME/etc/hadoop/
#COPY hadoop-volumes/yarn-site.xml $HADOOP_HOME/etc/hadoop/

RUN sudo mkdir -p /opt/hadoop/data/namenode && sudo chown -R hduser:hduser /opt/hadoop/data
RUN sudo mkdir -p /opt/hadoop/data/datanode && sudo chown -R hduser:hduser /opt/hadoop/data


COPY hadoop-volumes/docker-entrypoint.sh $HADOOP_HOME/etc/hadoop/
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

WORKDIR /usr/local/bin
RUN sudo ln -s ${HADOOP_HOME}/etc/hadoop/docker-entrypoint.sh .
WORKDIR /home/hduser

#YARNSTART=0 will prevent yarn scheduler from being launched
ENV YARNSTART 0

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
