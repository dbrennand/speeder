FROM golang:alpine as build
# Set working directory
WORKDIR /
# Required to clone librespeed-cli repo and install GCC to build the CLI
RUN apk add --no-cache build-base git
# Clone librespeed-cli repo
RUN git clone https://github.com/librespeed/speedtest-cli.git
WORKDIR /speedtest-cli
# Build the CLI binary
RUN go build -o librespeed main.go

# Setup Python dependencies
FROM python:3.9-alpine
# Copy requirements.txt and install dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
# Copy main script
COPY speed.py /
WORKDIR /
# Copy librespeed binary to Python alpine image to reduce size
COPY --from=build /speedtest-cli/librespeed .
# Run script
CMD ["python", "-u", "speed.py"]
