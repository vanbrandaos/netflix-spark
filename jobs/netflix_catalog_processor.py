from pyspark.sql import SparkSession
import json, os, sys, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(levelname)-5s %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_line(line):
    fields = []
    current_field = []
    inside_quotes = False

    for char in line:
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == ',' and not inside_quotes:
            fields.append(''.join(current_field).strip())
            current_field = []
        else:
            current_field.append(char)    
    fields.append(''.join(current_field).strip())

    return fields

def process_column(row, index):
    if len(row) > index and row[index].strip():
        return (row[index].strip(), 1)
    return ("Unknown", 1)

def extract_year(row):
    return (row[7], 1) if len(row) > 7 and row[7].strip() else ("Unknown", 1)

def parse_duration(duration_str):
    duration_str = duration_str.strip()
    if "min" in duration_str.lower():
        return int(duration_str.lower().replace("min", "").strip()), 0
    elif "season" in duration_str.lower():
        return 0, int(duration_str.lower().replace("seasons", "").replace("season", "").strip())
    else:
        return 0, 0

def main():    
    netflix_file_dir = os.getenv('NETFLIX_SPARK_FILE', 'hdfs://hadoop:9000/user/hduser/data/netflix_titles.csv')
    
    spark = SparkSession.builder \
        .appName("Spark GCS Example") \
        .config("spark.jars", "/opt/bitnami/spark/jars/gcs-connector-hadoop3-latest.jar") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/bitnami/spark/secrets/spark-gcloud-key.json") \
        .getOrCreate()


    rdd = spark.sparkContext.textFile(netflix_file_dir)
    header = rdd.first()
    rdd_cleaned = rdd.map(lambda line: clean_line(line)) \
                      .filter(lambda row: row[0] != header.split(",")[0])
  
    directors_rdd = rdd_cleaned.map(lambda row: process_column(row, 3)) \
                            .filter(lambda pair: pair[0].lower() != "unknown") \
                            .reduceByKey(lambda x, y: x + y)
    top_directors = directors_rdd.sortBy(lambda x: x[1], ascending=False).take(5)

    countries_rdd = rdd_cleaned.map(lambda row: process_column(row, 5)) \
                            .filter(lambda pair: pair[0].lower() != "unknown") \
                            .reduceByKey(lambda x, y: x + y)
    top_countries = countries_rdd.sortBy(lambda x: x[1], ascending=False).take(5)

    release_year_rdd = rdd_cleaned.map(lambda row: process_column(row, 7)) \
                                .filter(lambda pair: pair[0] != "Unknown") \
                                .reduceByKey(lambda x, y: x + y)
    releases = release_year_rdd.sortBy(lambda x: x[1], ascending=False).take(40)

    day_rdd = rdd_cleaned.map(lambda row: process_column(row, 6)) \
                        .filter(lambda pair: pair[0].strip().lower() != "unknown") \
                        .reduceByKey(lambda x, y: x + y)
    day_with_more_additions = day_rdd.sortBy(lambda x: x[1], ascending=False).first()

    type_rdd = rdd_cleaned.map(lambda row: process_column(row, 1)) \
                        .filter(lambda pair: pair[0].strip().lower() != "unknown") \
                        .reduceByKey(lambda x, y: x + y)
    type_pairs = type_rdd.take(2)

    durations_rdd = rdd_cleaned.map(lambda row: process_column(row, 9)) \
                            .filter(lambda pair: pair[0].lower() != "unknown") \
                            .map(lambda pair: parse_duration(pair[0])) \
                            .reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]))

    total_minutes, total_seasons = durations_rdd
    num_records = rdd_cleaned.count()
    average_minutes = total_minutes / num_records if num_records > 0 else 0
    average_seasons = total_seasons / num_records if num_records > 0 else 0

    data = {
        "top_countries": {item: count for item, count in top_countries},
        "top_directors": {item: count for item, count in top_directors},
        "day_with_more_additions": day_with_more_additions[0],
        "total_types": {item: count for item, count in type_pairs},
        "releases": {item: count for item, count in releases},
        "means": {
            "duration": average_minutes,
            "seasons": average_seasons
        },
        "total": rdd_cleaned.count()
    }

    json_data = json.dumps(data, indent=3)

    #print(json_data)

    data_list = [data]
    df = spark.createDataFrame(data_list)

    gcs_bucket_path = "gs://spark-netflix-bucket-39/data/netflix3.json"
    df.write.mode('overwrite').json(gcs_bucket_path)
    
    #df.write.format("json").save("hdfs://hadoop:9000/user/hduser/results")


    spark.stop()
    print(f"\nDONE!")

if __name__ == "__main__":
    main()
