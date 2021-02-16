# --- Stage 1 ---
# Base Layer, contains Go build tools
# Name this stage 'builder' so we can refer to it later
FROM golang:alpine AS builder

# Enable Go modules
ENV GO111MODULE=on

# Install Git and network certificates
RUN apk add git ca-certificates

# Set working dir to /app/src
WORKDIR /app/src

# Copy dep files
COPY go.mod .
COPY go.sum .

# Install dependencies
RUN go mod download

# Copy source code to image
COPY . /app/src

# Build image with Go modules and put binary
# in /go/bin/app
RUN CGO_ENABLED=0 GOOS=linux go build -o /go/bin/app

# --- Stage 2 ---
# use alpine which has network certs built in
FROM alpine:latest

# Copy built binary from previous stage
COPY --from=builder /go/bin/app /go/bin/app

EXPOSE 5000

# Run app
ENTRYPOINT ["/go/bin/app"]