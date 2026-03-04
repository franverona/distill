from app.utils.pagination import build_pagination_links


def test_single_page_no_links():
    next_url, prev_url = build_pagination_links(
        base_path="/endpoint", page=1, size=10, total=10
    )

    assert next_url is None
    assert prev_url is None


def test_no_next_on_last_page():
    next_url, prev_url = build_pagination_links(
        base_path="/endpoint", page=3, size=10, total=30
    )

    assert next_url is None
    assert prev_url == "/endpoint?size=10&page=2"


def test_no_prev_on_first_page():
    next_url, prev_url = build_pagination_links(
        base_path="/endpoint", page=1, size=10, total=30
    )

    assert next_url == "/endpoint?size=10&page=2"
    assert prev_url is None


def test_both_links_on_middle_page():
    next_url, prev_url = build_pagination_links(
        base_path="/endpoint", page=5, size=10, total=100
    )

    assert next_url == "/endpoint?size=10&page=6"
    assert prev_url == "/endpoint?size=10&page=4"


def test_extra_params_included_in_links():
    next_url, prev_url = build_pagination_links(
        base_path="/endpoint", page=5, size=10, total=100, extra_params={"q": "python"}
    )

    assert next_url == "/endpoint?size=10&q=python&page=6"
    assert prev_url == "/endpoint?size=10&q=python&page=4"
