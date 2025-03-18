import pandas as pd
import json
import time
import requests
from config import statistics_url

# Read the data from the CSV file
def read_data():
    df = pd.read_csv('results_stats.csv')
    data = {}
    fails = 0
    count = 0
    failPrcnt = 0
    ts = int(time.time() * 1000)

    for index, row in df.iterrows():
        # The CSV file has the following columns:
        # Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min Response Time,Max Response Time,Average Content Size,Requests/s,Failures/s,50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%
        fails = row['Failure Count']
        count = row['Request Count']
        failPrcnt = 0
        if (fails > 0) & (count > 0):
            failPrcnt = (fails / count) * 100

        data = {
            #"time": ts,
            'request_count': count,
            'failure_count': fails,
            'failure_percentage': failPrcnt,
            'median_response_time': row['Median Response Time'],
            'requests_per_second': row['Requests/s'],
            'failures_per_second': row['Failures/s'],
            }
        if (row['Name'] == 'Aggregated'):
            return data

    return data

# Post statistics data to URL
def send_data(data):
    headers = { 'Content-Type': 'application/json' }
    response = requests.post(statistics_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Data sent successfully")
    else:
        print("Failed to send data")

def main(toPrint=True):
    if statistics_url == '':
        print("Statistics URL is not set in config.py")
        return

    data = read_data()
    if toPrint:
        print("Statistics Data:")
        print(json.dumps(data))
        print("--------------")
    send_data(data)

if __name__ == "__main__":
    main()