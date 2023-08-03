# Speedtest-grafana

Use [Grafana](https://grafana.com/), [InfluxDB](https://www.influxdata.com/products/influxdb/) and the [librespeed/speedtest-cli](https://github.com/librespeed/speedtest-cli) to monitor your internet speed! 🚀

## Prerequisites

1. Docker

2. Docker Compose

## Usage

> [!NOTE]
>
> Make sure you run the commands below from the project directory.

1. Build the speedtest-grafana container image using the command: `docker-compose build`

2. Set the `SPEEDTEST_SERVER_ID` environment variable located in the [.env](.env) file to the server ID to perform speedtests against.

    > [!NOTE]
    >
    > If you don't know any server IDs, run the following command and they will be shown: `docker run --rm -it speedtest-grafana:1.0.0 /librespeed --list`

3. Modify any other environment variables located in the [.env](.env) file.

    > [!WARNING]
    >
    > It is **highly** recommended that you change the default usernames and passwords!

4. Start the containers using the command: `docker-compose up -d`

5. Access Grafana at [`http://localhost:3000`](http://localhost:3000)

    > [!NOTE]
    >
    > You should also be able to access Grafana from your host's IP address.

## Disclaimer

I did **NOT** create the LibreSpeed project or CLI. The great folks over at [LibreSpeed](https://github.com/librespeed) did.

If you like this project then please give their repositories a star! ⭐

## Authors -- Contributors

* [**dbrennand**](https://github.com/dbrennand) - *Author*

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) for details.
