# librespeed-grafana

Use [LibreSpeed-CLI](https://github.com/librespeed/speedtest-cli), [InfluxDB](https://www.influxdata.com/products/influxdb/) and [Grafana](https://grafana.com/) to monitor your internet speed! 🚀

## Prerequisites

1. Docker

2. docker-compose

## Usage

> [!NOTE]
> Make sure you run the commands below from the project directory.

1. Build the librespeed-grafana container image using the command: `docker-compose build`

2. Set the `SPEEDTEST_SERVER_ID` environment variable located in the [.env](.env) file to the server ID to perform speedtests against.

    > [!NOTE]
    > If you don't know any server IDs, run the following command and they will be shown: `docker run --rm -it librespeed-grafana:0.0.1 /librespeed --list`

3. Modify any other environment variables located in the [.env](.env) file.

    > [!WARNING]
    > It is **highly** recommended that you change the default usernames and passwords!
    >
    > When modifying the `INFLUXDB_USER` and `INFLUXDB_USER_PASSWORD` environment variables. Make sure you modify them also in [datasource.yml](/grafana-config/datasources/datasource.yml)
    >
    > ```yaml
    > # You SHOULD change these!
    > user: root
    > secureJsonData:
    >   password: root
    > ```

4. Start the containers using the command: `docker-compose up -d`

5. Access Grafana at `http://localhost:3000`

## Disclaimer

I did **not** create the LibreSpeed project or CLI. The great folks over at [LibreSpeed](https://github.com/librespeed) did.

If you like this project then please give their repositories a star! ⭐

## Authors -- Contributors

* [**dbrennand**](https://github.com/dbrennand) - *Author*

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) for details.
