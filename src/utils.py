import json
from google.cloud import storage
from google.oauth2 import service_account

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

def create_dict_from_arrays(list):
    new_list = {item: count for item, count in list}
    return [new_list]

def create_dict_from_tuples(list):
    result_dict = {item: count for item, count in list}
    return result_dict

def upload_json_to_bucket(bucket_name, destination_blob_name, json_data, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json_data, content_type='application/json')
    print(f'File uploaded to {destination_blob_name}.')
