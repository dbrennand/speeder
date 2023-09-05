"""
MIT License

Copyright (c) 2023 dbrennand

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient
from loguru import logger
import subprocess
import os
import json
import time

__version__ = "1.1.0"

logger.debug(f"Starting speeder version: {__version__}.")

# Retrieve environment variables
SPEEDER_SPEEDTEST_INTERVAL = int(
    os.environ.get("SPEEDER_SPEEDTEST_INTERVAL", 300)
)  # 5 minutes
SPEEDER_SPEEDTEST_SERVER_ID = os.environ.get("SPEEDER_SPEEDTEST_SERVER_ID", None)
SPEEDER_INFLUXDB_HOST = os.environ.get("SPEEDER_INFLUXDB_HOST", "influxdb")
SPEEDER_INFLUXDB_PORT = int(os.environ.get("SPEEDER_INFLUXDB_PORT", 8086))
SPEEDER_INFLUXDB_TOKEN = os.environ.get("SPEEDER_INFLUXDB_TOKEN", "root")
SPEEDER_INFLUXDB_ORG = os.environ.get("SPEEDER_INFLUXDB_ORG", "internet_speed")
SPEEDER_INFLUXDB_BUCKET = os.environ.get("SPEEDER_INFLUXDB_BUCKET", "internet_speed")

# Check environment variable has not been provided
if not SPEEDER_SPEEDTEST_SERVER_ID:
    logger.debug(
        "SPEEDER_SPEEDTEST_SERVER_ID environment variable has no server ID. Choose from the list below and set the environment variable."
    )
    servers = subprocess.run(["/librespeed", "--list"], capture_output=True, text=True)
    logger.debug(servers.stdout)
    exit(1)

# Connect to InfluxDB
logger.debug(
    f"Connecting to InfluxDB {SPEEDER_INFLUXDB_HOST}:{SPEEDER_INFLUXDB_PORT}, bucket: {SPEEDER_INFLUXDB_BUCKET}."
)
with InfluxDBClient(
    url=f"http://{SPEEDER_INFLUXDB_HOST}:{SPEEDER_INFLUXDB_PORT}",
    token=SPEEDER_INFLUXDB_TOKEN,
    org=SPEEDER_INFLUXDB_ORG,
) as client:
    # Run the speedtest using the librespeed/speedtest-cli on an interval
    while True:
        logger.debug(
            f"Running speedtest with server ID: {SPEEDER_SPEEDTEST_SERVER_ID} and telemetry disabled."
        )
        result = subprocess.run(
            [
                "/librespeed",
                "--server",
                SPEEDER_SPEEDTEST_SERVER_ID,
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
            # Parse JSON results
            try:
                json_result = json.loads(result.stdout)
            except json.decoder.JSONDecodeError as err:
                logger.debug(f"Failed to parse JSON results.\nError: {err}")
                logger.debug(f"Sleeping for {SPEEDER_SPEEDTEST_INTERVAL} seconds.")
                time.sleep(SPEEDER_SPEEDTEST_INTERVAL)
                continue
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                # Create InfluxDB record
                record = [
                    {
                        "measurement": "internet_speed",
                        "tags": {
                            "server_name": json_result[0]["server"]["name"],
                            "server_url": json_result[0]["server"]["url"],
                            "ip": json_result[0]["client"]["ip"],
                            "hostname": json_result[0]["client"]["hostname"],
                            "region": json_result[0]["client"]["region"],
                            "city": json_result[0]["client"]["city"],
                            "country": json_result[0]["client"]["country"],
                            "org": json_result[0]["client"]["org"],
                            "timezone": json_result[0]["client"]["timezone"],
                        },
                        "time": json_result[0]["timestamp"],
                        "fields": {
                            "bytes_sent": json_result[0]["bytes_sent"],
                            "bytes_received": json_result[0]["bytes_received"],
                            "ping": float(json_result[0]["ping"]),
                            "jitter": float(json_result[0]["jitter"]),
                            "upload": float(json_result[0]["upload"]),
                            "download": float(json_result[0]["download"]),
                        },
                    }
                ]
                # Write results to InfluxDB
                logger.debug(
                    f"Writing results to InfluxDB bucket: {SPEEDER_INFLUXDB_BUCKET}.\nResults: {record}"
                )
                write_api.write(bucket=SPEEDER_INFLUXDB_BUCKET, record=record)
        logger.debug(f"Sleeping for {SPEEDER_SPEEDTEST_INTERVAL} seconds.")
        time.sleep(SPEEDER_SPEEDTEST_INTERVAL)
