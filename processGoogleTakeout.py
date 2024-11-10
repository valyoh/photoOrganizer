import os
import json
from datetime import datetime
import time


def set_file_modification_time(file_path, timestamp):
    # Convert the timestamp to a datetime object
    dt = datetime.utcfromtimestamp(timestamp)
    # Convert the datetime object to a timestamp
    mod_time = time.mktime(dt.timetuple())
    # Set the modification time
    os.utime(file_path, (mod_time, mod_time))


def process_json_file(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        image_title = data.get('title')
        creation_timestamp = data.get('photoTakenTime', {}).get('timestamp')

        if image_title and creation_timestamp:
            image_path = os.path.join(os.path.dirname(json_file_path), image_title)
            if os.path.exists(image_path):
                set_file_modification_time(image_path, int(creation_timestamp))
                print(f"Updated {image_path} with photo taken time {creation_timestamp}")
            else:
                print(f"Image file {image_path} not found.")
        else:
            print(f"Invalid data in {json_file_path}")


def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_file_path = os.path.join(root, file)
                process_json_file(json_file_path)


# Replace 'your_directory_path' with the path to the directory containing your JSON files
process_directory('E:/takeout-20240926T082647Z-004')
