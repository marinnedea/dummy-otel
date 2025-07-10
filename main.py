from flask import Flask, request
import logging
from prometheus_client import Counter, generate_latest
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import otel_config

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Prometheus metric
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])

# Logger setup
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    logging.info("Handling request to '/'")
    return "Hello from dummy-otel!"

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; version=0.0.4"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
  
