from prometheus_client import Counter, Histogram

# Counter for all HTTP requests, labelled by HTTP method and status code.
# Used to build:
#   - GET requests per minute by status code
#   - POST requests per minute by status code
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "status_code"],
)

# Histogram of latency for successful (HTTP 200) POST requests.
# Buckets give 0.01 s precision up to 0.10 s, then coarser for larger values.
# Used to compute 50th, 90th, 95th, 99th percentiles and the average.
POST_LATENCY = Histogram(
    "http_post_request_duration_seconds",
    "Latency of successful (200) POST requests in seconds",
    buckets=[
        0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
        0.10, 0.25, 0.50, 0.75,
        1.0, 2.5, 5.0, 10.0,
    ],
)
