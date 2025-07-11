# dummy-otel - [![GitHub release](https://img.shields.io/github/v/release/marinnedea/dummy-otel)](https://github.com/marinnedea/dummy-otel/releases)

A minimal Python Flask app that emits:

- OpenTelemetry **traces** (sent via OTLP/gRPC to the endpoint specified in OTEL_EXPORTER_OTLP_ENDPOINT)
- Prometheus **metrics** at `/metrics`
- Structured **logs** to stdout

Built for **Kubernetes observability pipelines** with **Grafana Alloy** or any OTLP-compatible collector.

---

## Requirements

You must have **Grafana Alloy** (or any OTLP-compatible receiver) running and accessible at the configured endpoint.

> In a Grafana Cloud Kubernetes Monitoring setup, this is usually:
> ```
> grpc://grafana-k8s-monitoring-alloy-metrics.<namespace>.svc.cluster.local:4317
> ```

Alloy must support:
- OTLP/gRPC (`4317`)
- Prometheus metric scraping (via `k8s.grafana.com/scrape: "true"` annotation)
- Stdout logs (if Alloy is configured to collect pod logs)

---

## Usage

### 🐳 Run with Docker

Prebuilt multi-architecture Docker images are available on GitHub Container Registry (GHCR):
- https://github.com/marinnedea/dummy-otel/pkgs/container/dummy-otel


```bash
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://your-otel-collector:4317 \
  -e OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
  ghcr.io/marinnedea/dummy-otel:latest
```

Platforms Supported
- linux/amd64
- linux/arm64

Pull Specific Version
```bash
docker pull ghcr.io/marinnedea/dummy-otel:latest
```

### Build & Run Locally

```bash
docker build -t dummy-otel .
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=grpc://<your-alloy-host>:4317 \
  -e OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
  dummy-otel
```

Then:
```bash
curl http://localhost:8000
curl http://localhost:8000/metrics
```

## Deploy to Kubernetes

Use a Deployment like this:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dummy-otel
  namespace: dummy-otel
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dummy-otel
  template:
    metadata:
      labels:
        app: dummy-otel
      annotations:
        k8s.grafana.com/scrape: "true"
    spec:
      containers:
        - name: dummy-otel
          image: ghcr.io/marinnedea/dummy-otel:latest
          ports:
            - containerPort: 8000
          env:
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: grpc://grafana-k8s-monitoring-alloy-metrics.my-pi-namespace.svc.cluster.local:4317
            - name: OTEL_EXPORTER_OTLP_PROTOCOL
              value: grpc
```

## Status

Designed and tested on:

  - Raspberry Pi 5/ ARM64
  - K3s and Kubernetes
  - Grafana Alloy and Grafana Cloud

## Related Projects

  - [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
  - [Prometheus Python client](https://github.com/prometheus/client_python)
  - [Grafana Alloy](https://grafana.com/docs/alloy/)

