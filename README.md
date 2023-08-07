# Speedtest-grafana

Use [Grafana](https://grafana.com/), [InfluxDB](https://www.influxdata.com/products/influxdb/) and the [librespeed/speedtest-cli](https://github.com/librespeed/speedtest-cli) to monitor your internet speed! 🚀

## Prerequisites

1. Docker

2. Docker Compose

## Usage

1. Build the speedtest-grafana container image:

    ```bash
    docker compose build
    ```

2. Set the `SPEEDTEST_SERVER_ID` environment variable located in the [.env](.env) file to the server ID to perform speedtests against.

    > **Note**
    >
    > If you don't know any server IDs, run the following command to list them:
    > ```bash
    > docker run --rm -it speedtest-grafana:1.0.0 /librespeed --list
    > ```

3. Set the `DOCKER_INFLUXDB_INIT_PASSWORD`, `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` and `GF_SECURITY_ADMIN_PASSWORD` environment variables located in the [.env](.env) file.

4. Start the containers:

    ```bash
    docker compose up -d
    ```

5. Access Grafana at [`http://localhost:3000`](http://localhost:3000)

    > **Note**
    >
    > Grafana will also be available from your host's IP address.

## Disclaimer

I did **NOT** create the LibreSpeed project or CLI. The great folks over at [LibreSpeed](https://github.com/librespeed) did.

If you like this project then please give their repositories a star! ⭐

## Authors -- Contributors

[**Daniel Brennand**](https://github.com/dbrennand) - *Author*

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) for details.
