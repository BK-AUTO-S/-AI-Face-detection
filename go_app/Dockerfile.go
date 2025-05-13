# Stage 1: Build the Go application
FROM golang:1.20-alpine AS builder

WORKDIR /app

# Install git for fetching dependencies if needed
RUN apk add --no-cache git

COPY go.mod ./
RUN go mod tidy
RUN go mod download

COPY . ./

# Build the Go app
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app/faceregco_go_app ./main.go

# Stage 2: Create the runtime image
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /app

# Copy the pre-built binary from the builder stage
COPY --from=builder /app/faceregco_go_app .

# Copy templates and static files for the Go app
COPY templates ./templates
# If you have static assets for Go app, copy them too
# COPY static ./static

# This directory will be mounted as a volume for the SQLite database
RUN mkdir -p /data

ENV DB_PATH=/data/face_database.db

EXPOSE 8000

CMD ["./faceregco_go_app"]
