FROM golang:alpine as build
# Set working directory
WORKDIR /
# Required to clone the librespeed/speedtest-cli repo and install GCC to build the CLI
RUN apk add --no-cache git build-base
# Clone the librespeed/speedtest-cli repo
RUN git clone --branch v1.0.12 https://github.com/librespeed/speedtest-cli.git
WORKDIR /speedtest-cli
# Build the librespeed CLI binary
RUN go build -o librespeed main.go

FROM ghcr.io/astral-sh/uv:python3.13-alpine
COPY pyproject.toml /
COPY uv.lock /
COPY speeder.py /
WORKDIR /
RUN uv sync
# Copy the librespeed CLI binary to the Python image to reduce size
COPY --from=build /speedtest-cli/librespeed .
# Run speedtest script
CMD ["python", "speeder.py"]
