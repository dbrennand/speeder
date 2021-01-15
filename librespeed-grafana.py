from loguru import logger
import os
import influxdb
import subprocess
import json
import time

__version__ = "0.0.1"

logger.debug(f"Starting librespeed-grafana version: {__version__}.")

# Retrieve environment variables, if not found, use defaults
## LibreSpeed CLI environment variables
SPEEDTEST_INTERVAL = int(os.environ.get("SPEEDTEST_INTERVAL", 300))  # 5 minutes
SPEEDTEST_SERVER_ID = str(os.environ.get("SPEEDTEST_SERVER_ID", None))
## InfluxDB environment variables
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "influxdb")
INFLUXDB_PORT = int(os.environ.get("INFLUXDB_PORT", 8086))
INFLUXDB_USER = os.environ.get("INFLUXDB_USER", "root")
INFLUXDB_USER_PASSWORD = os.environ.get("INFLUXDB_USER_PASSWORD", "root")
INFLUXDB_DB = os.environ.get("INFLUXDB_DB", "internet_speed")

# Check if SPEEDTEST_SERVER_ID environment variable has not been provided
if not SPEEDTEST_SERVER_ID:
    logger.debug(
        "SPEEDTEST_SERVER_ID environment variable has no server ID. Choose from the list below and set the environment variable."
    )
    servers = subprocess.run(["/librespeed", "--list"], capture_output=True, text=True)
    logger.debug(servers.stdout)
    exit()

# Connect to InfluxDB
logger.debug(
    f"Connecting to InfluxDB using host: {INFLUXDB_HOST}, port: {INFLUXDB_PORT}, username: {INFLUXDB_USER}, database name: {INFLUXDB_DB}."
)
influx = influxdb.InfluxDBClient(
    host=INFLUXDB_HOST,
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_USER_PASSWORD,
    database=INFLUXDB_DB,
    retries=0,
)

# Run the speedtest using the LibreSpeed CLI on an interval
while True:
    # Run the speedtest using the LibreSpeed CLI
    logger.debug(
        f"Running speedtest with server ID: {SPEEDTEST_SERVER_ID} and telemetry disabled."
    )
    result = subprocess.run(
        [
            "/librespeed",
            "--server",
            SPEEDTEST_SERVER_ID,
            "--telemetry-level",
            "disabled",
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    # Check if speedtest failed
    if result.returncode != 0:
        # Speedtest failed
        # CLI errors go to stdout
        logger.debug(
            f"Speedtest failed with exit code: {result.returncode}.\nError: {result.stdout}"
        )
    else:
        # Speedtest succeeded
        logger.debug(f"Speedtest succeeded. Parsing JSON results.")
        # Load and parse JSON results
        json_result = json.loads(result.stdout)
        # Create InfluxDB JSON body
        json_body = [
            {
                "measurement": "internet_speed",
                "tags": {
                    "server_name": json_result["server"]["name"],
                    "server_url": json_result["server"]["url"],
                    "ip": json_result["client"]["ip"],
                    "hostname": json_result["client"]["hostname"],
                    "region": json_result["client"]["region"],
                    "city": json_result["client"]["city"],
                    "country": json_result["client"]["country"],
                    "org": json_result["client"]["org"],
                    "timezone": json_result["client"]["timezone"],
                },
                "time": json_result["timestamp"],
                "fields": {
                    "bytes_sent": json_result["bytes_sent"],
                    "bytes_received": json_result["bytes_received"],
                    "ping": float(json_result["ping"]),
                    "jitter": float(json_result["jitter"]),
                    "upload": float(json_result["upload"]),
                    "download": float(json_result["download"]),
                },
            }
        ]
        # Write results to InfluxDB
        logger.debug(
            f"Writing results to InfluxDB database: {INFLUXDB_DB}.\nResults: {json_body}"
        )
        influx.write_points(json_body)
    logger.debug(f"Sleeping for {SPEEDTEST_INTERVAL} seconds.")
    # Sleep on the specified interval
    time.sleep(SPEEDTEST_INTERVAL)
