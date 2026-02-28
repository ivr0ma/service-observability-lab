import time

from main.metrics import REQUEST_COUNT, POST_LATENCY


class PrometheusMiddleware:
    """
    Django middleware that tracks:
    - total HTTP request count by method and status code (Counter)
    - latency of successful (HTTP 200) POST requests (Histogram)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        method = request.method.lower()
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, status_code=status).inc()

        if request.method == "POST" and response.status_code == 200:
            POST_LATENCY.observe(duration)

        return response
