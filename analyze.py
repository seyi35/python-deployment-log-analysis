import json
from datetime import datetime, timedelta

DEPLOYED_AT = datetime.fromisoformat("2026-11-15T10:05:00+00:00")
WINDOW = timedelta(minutes=5)


# Decide which five-minute window contains this request.
def classify_window(timestamp):
    # The deployment was at 10:05. Subtracting five minutes gives us 10:00.
    if DEPLOYED_AT - WINDOW <= timestamp < DEPLOYED_AT:
        return "before"

    # A request arriving exactly at 10:05 belongs to the after window.
    if DEPLOYED_AT <= timestamp < DEPLOYED_AT + WINDOW:
        return "after"

    # Skip requests earlier than 10:00 or at 10:10 and later.
    return None

def is_server_error(status):
    # Count HTTP responses from 500 through 599 as server errors.
    return 500 <= status < 600

def analyze(path):
    counts = {"before": {}, "after": {}}

    with open(path, encoding="utf-8") as log:
        for line in log:
            entry = json.loads(line)
            timestamp = datetime.fromisoformat(entry["ts"])
            window = classify_window(timestamp)
            if window is None:
                continue

            route = entry["route"]
            bucket = counts[window].setdefault(route, {"requests": 0, "errors": 0})
            bucket["requests"] += 1
            if is_server_error(entry["status"]):
                bucket["errors"] += 1

    return counts


if __name__ == "__main__":
    for window, routes in analyze("requests.jsonl").items():
        for route, bucket in sorted(routes.items()):
            errors = bucket["errors"]
            requests = bucket["requests"]
            rate = errors / requests
            print(f"{window:6} {route:8} {errors}/{requests}  {rate:.1%}")
