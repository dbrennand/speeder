import os
import influxdb
import subprocess
import json
import time

__version__ = "0.0.1"

# Retrieve environment variables, if not found, use defaults
## LibreSpeed CLI environment variables
SPEEDTEST_INTERVAL = os.environ.get("SPEEDTEST_INTERVAL", 1800) # Default: 30 minutes
SPEEDTEST_SERVER_ID = os.environ.get("SPEEDTEST_SERVER_ID", None)
## InfluxDB environment variables
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "127.0.0.1")
INFLUXDB_PORT = os.environ.ge("INFLUXDB_PORT", 8086)
INFLUXDB_USERNAME = os.environ.ge("INFLUXDB_USERNAME", "root")
INFLUXDB_PASSWORD = os.environ.ge("INFLUXDB_PASSWORD", "root")
INFLUXDB_DB_NAME = os.environ.ge("INFLUXDB_DB_NAME", "internet_speed")

# Connect to the InfluxDB database using a context manager
with influxdb.InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USERNAME, password=INFLUXDB_PASSWORD, database=INFLUXDB_DB_NAME) as influx:
    # Run the speedtest using the LibreSpeed CLI on a set interval
    while True:
        # Run the speedtest using the LibreSpeed CLI
        ## Check if SPEEDTEST_SERVER_ID has been provided, if so, use the server ID
        if SPEEDTEST_SERVER_ID:
            print(f"Running speedtest with server ID: {SPEEDTEST_SERVER_ID}.")
            process = subprocess.Popen(["./librespeed", f"--server {SPEEDTEST_SERVER_ID}", "--telemetry-level disabled", "--json"], stdout=subprocess.PIPE)
        else:
            print(f"Running speedtest.")
            process = subprocess.Popen(["./librespeed", "--telemetry-level disabled", "--json"], stdout=subprocess.PIPE)
        # Wait for speedtest to finish
        result, err = process.communicate()
        exit_code = process.wait()
        # Check if speedtest failed
        if exit_code not 0:
            # Speedtest failed
            print(f"Speedtest failed with exit code: {exit_code}.\nError: {err.decode('utf-8')}")
        else:
            # Speedtest succeeded
            print(f"Speedtest succeeded. Parsing JSON and writing results to InfluxDB database: {INFLUXDB_DB_NAME}.")
            # Load and parse JSON results
            json_result = json.loads(result.decode('utf-8'))
            # Write InfluxDB result
            json_body = [
                {
                    "measurement": "internet_speed",
                    "tags": {
                        "server_name": json_result["server"]["name"],
                        "server_url": json_result["server"]["url"],
                        "hostname": json_result["client"]["hostname"],
                        "region": json_result["client"]["region"],
                        "city": json_result["client"]["city"],
                        "country": json_result["client"]["country"],
                        "org": json_result["client"]["org"],
                        "timezone": json_result["client"]["timezone"]
                    },
                    "time": json_result["timestamp"],
                    "fields": {
                        "bytes_sent": json_result["bytes_sent"],
                        "bytes_received": json_result["bytes_received"],
                        "ping": json_result["ping"],
                        "jitter": json_result["jitter"],
                        "upload": json_result["upload"],
                        "download": json_result["download"]
                    }
                }
            ]
            # Write results to InfluxDB
            print(f"Writing results to InfluxDB database: {json_body}")
            influx.write_points(json_body)
        # Sleep on the specified interval
        time.sleep(SPEEDTEST_INTERVAL)
