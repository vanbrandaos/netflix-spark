from pyspark.sql import SparkSession
from google.cloud import storage
from google.oauth2 import service_account
import json, os, logging

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

netflix_file_dir = os.getenv('NETFLIX_SPARK_FILE', 'hdfs://localhost:9000/user/hduser/data/netflix_titles.csv')
spark_master_url = os.getenv('SPARK_MASTER_URL', 'spark://spark-master:7077')  

logger.info(f"\nNETFLIX PROCESSOR")
logger.info(f"ENVS")
logger.info('SPARK_MASTER_URL= %s', spark_master_url)
logger.info('NETFLIX_SPARK_FILE= %s', netflix_file_dir)
logger.info (f"\nPROCESSING...")

spark = SparkSession.builder \
    .appName("NetflixDataProcessor") \
    .config("spark.master", spark_master_url) \
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
print(json_data)

# bucket_name = 'spark-netflix-bucket-39'
# destination_blob_name = 'data/netflix.json'
# credentials_path = '/home/soma/dev/ufrj/netflix-spark/secrets/sa-private-key.json'

# credentials = service_account.Credentials.from_service_account_file(credentials_path)
# storage_client = storage.Client(credentials=credentials)
# bucket = storage_client.bucket(bucket_name)
# blob = bucket.blob(destination_blob_name)
# blob.upload_from_string(json_data, content_type='application/json')
# print(f'File uploaded to {destination_blob_name}.')

spark.stop()
print(f"\nDONE!")
