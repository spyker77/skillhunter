from rest_framework.request import Request


def parse_request(request: Request) -> tuple[str, int | None, str, str]:
    query = request.GET.get("q")
    limit = request.GET.get("limit")
    if limit is not None:
        limit = int(limit)
    user_agent = request.headers.get("User-Agent")
    # Either get the IP address from the HTTP_X_FORWARDED_FOR or from the REMOTE_ADDR header.
    if x_forwarded_for := request.headers.get("X-Forwarded-For"):
        ip_address = x_forwarded_for.split(", ")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    return query, limit, user_agent, ip_address
