FROM python:3.6-slim-buster

RUN apt-get update && apt-get install -y openjdk-11-jdk iputils-ping curl

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/secrets/sa-private-key.json"

EXPOSE 5000

ENTRYPOINT ["bash"]
#CMD [ "python", "src/process_data.py", "--host=0.0.0.0", "--port=5000"]
