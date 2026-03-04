from urllib.parse import urlencode


def build_pagination_links(
    base_path: str,
    page: int,
    size: int,
    total: int,
    extra_params: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """
    Return (next_url, prev_url) for a paginated response.

    Returns None for next if on the last page, None for prev if on the first.
    extra_params are appended as additional query string values (e.g. {"q": "python"}).
    """
    params = {"size": size, **(extra_params or {})}
    base = f"{base_path}?{urlencode(params)}"

    next_url = f"{base}&page={page + 1}" if page * size < total else None
    prev_url = f"{base}&page={page - 1}" if page > 1 else None
    return next_url, prev_url
