FROM golang:alpine as build
# Set working directory
WORKDIR /
# Required to clone the librespeed/speedtest-cli repo and install GCC to build the CLI
RUN apk add --no-cache git build-base
# Clone the librespeed/speedtest-cli repo
RUN git clone https://github.com/librespeed/speedtest-cli.git
WORKDIR /speedtest-cli
# Build the librespeed CLI binary
RUN go build -o librespeed main.go

FROM python:3.9-alpine
# Copy requirements.txt and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
# Copy speedtest script
COPY speedtest.py /
WORKDIR /
# Copy the librespeed CLI binary to the Python alpine image to reduce size
COPY --from=build /speedtest-cli/librespeed .
# Run speedtest script
CMD ["python", "speedtest.py"]
