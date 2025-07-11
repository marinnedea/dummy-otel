#!/bin/bash

NAMESPACE="dummy-observability"
LABEL_SELECTOR="app=dummy-otel"

POD_IP=$(kubectl get pod -n "$NAMESPACE" -l "$LABEL_SELECTOR" -o jsonpath='{.items[0].status.podIP}')

if [ -z "$POD_IP" ]; then
  echo "$(date) - Could not find dummy-otel pod IP"
  exit 1
fi

echo "$(date) - Polling dummy-otel at $POD_IP"

for endpoint in / /0/ /health; do
  echo -n "$endpoint => "
  curl -s "http://$POD_IP:8000$endpoint" || echo "FAILED"
done

echo ""
