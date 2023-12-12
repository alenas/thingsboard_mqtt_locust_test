import json
import time

    
    
def update_timestamps(json_file_path):
    current_unix_timestamp = int(time.time())

    try:
        with open(json_file_path, 'r') as json_file:
            try:
                json_data = json.load(json_file)
            except json.decoder.JSONDecodeError as e:
               
                return

        for key in json_data['GIS-ID']:
            json_data['GIS-ID'][key]['timestamp'] = current_unix_timestamp

        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    except IOError as e:
        

if __name__ == "__main__":
    json_file_path = "data.json"  
    update_timestamps(json_file_path)

  

