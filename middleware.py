from time import perf_counter_ns

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from cases.logging import Colors, format_time_magnitude, log, print_color
from state import visit_counter


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = perf_counter_ns()
        response = await call_next(request)
        end_time = perf_counter_ns()

        time_elapsed = end_time - start_time

        if 200 <= response.status_code < 300:
            color = Colors.GREEN
        elif 300 <= response.status_code < 400:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        log(
            f"[{request['method']}] {response.status_code} {request['path']}",
            color,
            end=" | ",
        )

        print_color(f"Request took: {format_time_magnitude(time_elapsed)}", Colors.BLUE)

        response.headers["process-time"] = str(round(time_elapsed) / 1e6)

        return response


class PageVisitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not request["path"].startswith("/admin") and not request["path"].startswith(
            "/static"
        ):
            visit_counter.increment()

        response = await call_next(request)

        response.headers["page-visits"] = str(visit_counter.counter)
        return response
