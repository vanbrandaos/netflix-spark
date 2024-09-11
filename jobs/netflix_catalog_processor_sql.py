from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, split, when, count, sum
import json, os, sys, logging
from pyspark.sql.functions import trim, when, col, lit, avg

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(levelname)-5s %(name)s - %(message)s')
logger = logging.getLogger(__name__)

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


    df = spark.read.csv(netflix_file_dir, header=True, inferSchema=True, nullValue="") #usar fillna substituiria null. <column: subs>
    
#     pyspark.sql.GroupedData.max
# pyspark.sql.GroupedData.mean
# pyspark.sql.GroupedData.min
# pyspark.sql.GroupedData.pivot
# pyspark.sql.GroupedData.sum
# Math Functions
# Datetime Functions
# Collection Functions
# Sort Functions
# String Functions
# pyspark.sql.DataFrame.union
# pyspark.sql.DataFrame.subtract
# pyspark.sql.DataFrame.summary
# pyspark.sql.DataFrame.tail
# pyspark.sql.DataFrame.take
# pyspark.sql.DataFrame.show
# pyspark.sql.DataFrame.sort
# pyspark.sql.DataFrame.sample
# pyspark.sql.DataFrame.sampleBy
# pyspark.sql.DataFrame.schema
# pyspark.sql.DataFrame.select
# pyspark.sql.DataFrame.orderBy
# pyspark.sql.DataFrame.isEmpty
# pyspark.sql.DataFrame.groupBy


    num_records = df.count()
    
    filtered_directors = df.filter(df["director"].isNotNull())
    top_directors = filtered_directors.groupBy("director").count().orderBy("count", ascending = False).limit(5)
    
    filtered_countries = df.filter(df["country"].isNotNull()) 
    top_countries = filtered_countries.groupBy("country").count().orderBy("count", ascending = False).limit(5)
    
    filtered_release_year = df.filter(df["release_year"].isNotNull()) 
    top_release_year = filtered_release_year.groupBy("release_year").count().orderBy("count", ascending = False).limit(50)

    filtered_date_added = df.filter(df["date_added"].isNotNull()) 
    top_date = filtered_date_added.groupBy("date_added").count().orderBy("count", ascending = False).first().date_added

    filtered_type = df.filter(df["type"].isNotNull()).filter(df["type"].isin("Movie", "TV Show"))
    types_by_group = filtered_type.groupBy("type").count()


    filtered_duration = df.filter(df["duration"].isNotNull()) 
    filtered_duration_minutes = filtered_duration.filter(filtered_duration["duration"].endswith("min"))
    filtered_duration_seasons = filtered_duration.filter(filtered_duration["duration"].endswith("Season") | filtered_duration["duration"].endswith("Seasons"))
    
    filtered_duration_minutes = filtered_duration_minutes.withColumn("duration_minutes", split(col("duration"), " ")[0].cast("int"))
    filtered_duration_seasons = filtered_duration_seasons.withColumn("duration_seasons", split(col("duration"), " ")[0].cast("int"))

    average_minutes = filtered_duration_minutes.select(avg("duration_minutes")).collect()[0][0]
    average_minutes = average_minutes if average_minutes is not None else 0
    average_seasons = filtered_duration_seasons.select(avg("duration_seasons")).collect()[0][0]
    average_seasons = average_seasons if average_seasons is not None else 0
    

    top_countries_data = top_countries.collect()
    top_directors_data = top_directors.collect()
    total_types_data = types_by_group.collect()
    releases_data = top_release_year.collect()


    result = {
        "top_countries": {row['country']: row['count'] for row in top_countries_data},
        "top_directors": {row['director']: row['count'] for row in top_directors_data},
        "day_with_more_additions": top_date,
        "total_types": {row['type']: row['count'] for row in total_types_data},
        "releases": {str(row['release_year']): row['count'] for row in releases_data},
        "means": {
            "duration": average_minutes,
            "seasons": average_seasons
        },
        "total": num_records
    }

    json_data = json.dumps(result, indent=3)
    print(json_data)

    # # data_list = [data]
    # # df = spark.createDataFrame(data_list)

    # # gcs_bucket_path = "gs://spark-netflix-bucket-39/data/netflix3.json"
    # # df.write.mode('overwrite').json(gcs_bucket_path)
    
    # # #df.write.format("json").save("hdfs://hadoop:9000/user/hduser/results")


    # # spark.stop()
    # # print(f"\nDONE!")

if __name__ == "__main__":
    main()
