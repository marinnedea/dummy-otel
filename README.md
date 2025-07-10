# dummy-otel

A minimal Flask app that emits:

- ✅ OpenTelemetry traces (via OTLP gRPC)
- ✅ Prometheus metrics at `/metrics`
- ✅ Logs to stdout

## Usage

### Set environment variables:
```yaml
- OTEL_EXPORTER_OTLP_ENDPOINT=grpc://<your-alloy-service>:4317
- OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

### Build & Run Locally
```bash
docker build -t dummy-otel .
docker run -p 8000:8000 dummy-otel
```
