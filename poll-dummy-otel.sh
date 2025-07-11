#!/bin/bash

KUBE_CMD="/usr/local/bin/kubectl"
NAMESPACE="dummy-observability"
LABEL_SELECTOR="app=dummy-otel"
LOG_FILE="$HOME/dummy-otel/poll.log"

timestamp() {
  date --iso-8601=seconds
}

POD_IP=$($KUBE_CMD get pod -n "$NAMESPACE" -l "$LABEL_SELECTOR" -o jsonpath='{.items[0].status.podIP}')

if [ -z "$POD_IP" ]; then
  echo "$(timestamp), level=error, msg=\"Could not find dummy-otel pod IP\"" >> "$LOG_FILE"
  exit 1
fi

echo "$(timestamp), level=info, msg=\"Polling dummy-otel\", pod_ip=\"$POD_IP\"" >> "$LOG_FILE"

for endpoint in / /0/ /health; do
  response=$(curl -s -w "%{http_code}" -o /tmp/response.tmp "http://$POD_IP:8000$endpoint")
  body=$(cat /tmp/response.tmp | tr -d '\n' | sed 's/"/\\"/g')
  echo "$(timestamp), level=info, endpoint=\"$endpoint\", status=\"$response\", response=\"${body}\"" >> "$LOG_FILE"
done
