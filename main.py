import os
import time
import logging
import requests
import random
from flask import Flask

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

# Tracing
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider

# Instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# OTLP endpoint
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

# Resource
resource = Resource.create({
    "service.name": "dummy-otel",
    "service.namespace": "dummy-observability",
    "service.version": "1.1.3",
    "deployment.environment": "development"
})

# Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
)

# Metrics
metrics.set_meter_provider(MeterProvider(
    resource=resource,
    metric_readers=[
        PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
            export_interval_millis=5000
        )
    ]
))
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
    name="dummy_requests_total",
    unit="1",
    description="Counts requests to /0/"
)

# Logging
log_exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Use standard logging.Logger with OTEL LoggingHandler
otel_logger = logging.getLogger("dummy-otel")
otel_logger.setLevel(logging.INFO)
otel_logger.addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))

# Flask App
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def index():
    otel_logger.info("Hit / route")
    return "Hello from dummy-otel!"

@app.route("/health")
def health():
    return "OK", 200

@app.route("/0/")
def generate_everything():
    otel_logger.info("Handling /0/ request")

    with tracer.start_as_current_span("generate-trace-span") as span:
        request_counter.add(1, {"endpoint": "/0/"})

        # Simulate variable response time
        delay = random.uniform(0.1, 1.0)
        time.sleep(delay)

        # Simulate a random failure
        if random.random() < 0.3:  # 30% chance of failure
            error_msg = f"Simulated failure after {delay:.2f}s"
            otel_logger.error(error_msg)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))
            return "Internal Server Error", 500

        # Normal behavior
        r = requests.get("https://httpbin.org/status/200")
        otel_logger.info(f"Downstream call returned: {r.status_code}")
        return f"Trace, metric, and log generated after {delay:.2f}s"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
