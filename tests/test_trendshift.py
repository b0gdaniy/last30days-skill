"""Trendshift is a keyless, explicitly requested repository-momentum source."""

from lib import pipeline, trendshift


LISTING = '''
<a href="/repositories/42">acme/rocket</a>
<a href="/repositories/7">other/widget</a>
<a href="/repositories/42">acme/rocket</a>
'''


def test_listing_parser_preserves_rank_and_deduplicates_repositories():
    items = trendshift.parse_listing(LISTING, as_of="2026-09-28")

    assert [item["title"] for item in items] == ["acme/rocket", "other/widget"]
    assert [item["engagement"]["rank"] for item in items] == [1, 2]
    assert items[0]["url"] == "https://trendshift.io/repositories/42"
    assert items[0]["date"] == "2026-09-28"


def test_source_is_off_by_default_and_available_only_on_opt_in():
    assert "trendshift" not in pipeline.available_sources({}, None, x_pending=False)
    assert "trendshift" in pipeline.available_sources({}, ["trendshift"], x_pending=False)
    assert "trendshift" in pipeline.available_sources(
        {"INCLUDE_SOURCES": "trendshift"}, None, x_pending=False
    )


def test_search_uses_shared_html_fetch_and_filters_unrelated_repositories(monkeypatch):
    captured = {}

    def fake_get_text(url, **kwargs):
        captured["url"] = url
        captured["accept"] = kwargs["accept"]
        return LISTING

    monkeypatch.setattr(trendshift.http, "get_text", fake_get_text)
    items = trendshift.search_trendshift("acme rocket", "2026-08-29", "2026-09-28")

    assert [item["title"] for item in items] == ["acme/rocket"]
    assert captured == {"url": "https://trendshift.io/", "accept": "text/html"}


def test_trendshift_is_a_discovery_source_when_explicitly_requested():
    report = pipeline.run_discover(
        domain="agents",
        config={},
        depth="quick",
        requested_sources=["trendshift"],
        mock=True,
        subreddits=None,
        lookback_days=30,
    )

    assert "trendshift" in report.source_status
