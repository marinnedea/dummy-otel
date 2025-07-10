# dummy-otel

A minimal Python Flask app that emits:

- ✅ OpenTelemetry **traces** (via OTLP gRPC)
- ✅ Prometheus **metrics** at `/metrics`
- ✅ Structured **logs** to stdout

Built for **Kubernetes observability pipelines** with **Grafana Alloy** or any OTLP-compatible collector.

---

## 🛠 Requirements

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

## 🚀 Usage
## 📦 Releases

[![GitHub release](https://img.shields.io/github/v/release/marinnedea/dummy-otel)](https://github.com/marinnedea/dummy-otel/releases)

Prebuilt multi-architecture Docker images are available on GitHub Container Registry (GHCR).

### 🐳 Run with Docker

```bash
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://your-otel-collector:4317 \
  -e OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
  ghcr.io/marinnedea/dummy-otel:latest
```

🔄 Platforms Supported
- linux/amd64
- linux/arm64

📥 Pull Specific Version
```bash
docker pull ghcr.io/marinnedea/dummy-otel:v1.0.0
```

📤 Emit Telemetry

Once running, this app will emit:
- Logs: to stdout
- Metrics: available at http://localhost:8000/metrics (Prometheus format)
- Traces: sent via OTLP/gRPC to the endpoint specified in OTEL_EXPORTER_OTLP_ENDPOINT


### 🔧 Build & Run Locally

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

## 🧩 Deploy to Kubernetes

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
          image: ghcr.io/youruser/dummy-otel:arm64
          ports:
            - containerPort: 8000
          env:
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: grpc://grafana-k8s-monitoring-alloy-metrics.my-pi-namespace.svc.cluster.local:4317
            - name: OTEL_EXPORTER_OTLP_PROTOCOL
              value: grpc
```

## 📊 Output

   - GET / → Triggers a trace span and logs a message
   - GET /metrics → Exposes Prometheus metrics
   - Stdout logs → include trace IDs for correlation (visible in Grafana Cloud if logs are enabled)

## 🏁 Status

Designed and tested on:

  - ✅ Raspberry Pi / ARM64
  - ✅ K3s and Kubernetes
  - ✅ Grafana Alloy and Grafana Cloud

## 🔗 Related Projects

  - [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
  - [Prometheus Python client](https://github.com/prometheus/client_python)
  - [Grafana Alloy](https://grafana.com/docs/alloy/)


