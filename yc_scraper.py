import csv
import json
import sys
import time
from typing import Any, Dict, Iterable, List, Set

import requests


ALGOLIA_HOST = "https://45bwzj1sgc-dsn.algolia.net"
QUERIES_PATH = "/1/indexes/*/queries"

# These query params and headers mirror the provided cURL.
# API key here is a search key restricted to specific indices/tags.
QUERY_PARAMS = {

}

REQUEST_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Origin": "https://www.ycombinator.com",
    "Referer": "https://www.ycombinator.com/",
}


def build_params_string(page: int, hits_per_page: int = 1000) -> str:
    facets = [
        "app_answers",
        "app_video_public",
        "batch",
        "demo_day_video_public",
        "industries",
        "isHiring",
        "nonprofit",
        "question_answers",
        "regions",
        "subindustry",
        "top_company",
    ]
    # Algolia expects a URL-encoded query-string in the `params` field
    # We keep it explicit for parity with the provided cURL
    encoded_facets = json.dumps(facets)
    restrict_indices = json.dumps([
        "YCCompany_production",
        "YCCompany_By_Launch_Date_production",
    ])
    analytics_tags = json.dumps(["ycdc"])
    tag_filters = json.dumps(["ycdc_public"])  # to match server behavior
    return (
        f"facets={requests.utils.quote(encoded_facets)}"
        f"&hitsPerPage={hits_per_page}"
        f"&maxValuesPerFacet=1000"
        f"&page={page}"
        f"&query="
        f"&restrictIndices={requests.utils.quote(restrict_indices)}"
        f"&analyticsTags={requests.utils.quote(analytics_tags)}"
        f"&tagFilters={requests.utils.quote(tag_filters)}"
    )


def fetch_page(page: int) -> Dict[str, Any]:
    url = f"{ALGOLIA_HOST}{QUERIES_PATH}"
    body = {
        "requests": [
            {
                "indexName": "YCCompany_production",
                "params": build_params_string(page),
            }
        ]
    }

    # Retry basic transient failures (HTTP 429/5xx)
    max_attempts = 5
    backoff_seconds = 1.0
    for attempt in range(1, max_attempts + 1):
        resp = requests.post(
            url,
            params=QUERY_PARAMS,
            data=json.dumps(body),
            headers=REQUEST_HEADERS,
            timeout=30,
        )

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code in {429, 500, 502, 503, 504} and attempt < max_attempts:
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
            continue

        resp.raise_for_status()

    # Should never reach here due to raise_for_status on final attempt
    raise RuntimeError("Unexpected failure fetching page")


def iterate_all_hits() -> Iterable[Dict[str, Any]]:
    page = 0
    hits_per_page_observed = None

    while True:
        payload = fetch_page(page)
        results = payload.get("results", [])
        if not results:
            break

        first = results[0]
        hits: List[Dict[str, Any]] = first.get("hits", [])
        if hits_per_page_observed is None:
            hits_per_page_observed = first.get("hitsPerPage", len(hits)) or 1000

        if not hits:
            break

        for hit in hits:
            yield hit

        # Stop when the current page returned fewer hits than the page size
        if len(hits) < (hits_per_page_observed or 1000):
            break

        page += 1


def to_primitive(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    # Serialize lists/dicts consistently as JSON strings for CSV cells
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def collect_fieldnames(hits: List[Dict[str, Any]]) -> List[str]:
    keys: Set[str] = set()
    for h in hits:
        keys.update(h.keys())
    # Stable order: common identifiers first, then alphabetical
    preferred = [
        "id",
        "objectID",
        "name",
        "slug",
        "batch",
        "industry",
        "industries",
        "subindustry",
        "regions",
        "all_locations",
        "team_size",
        "status",
        "stage",
        "isHiring",
        "top_company",
        "nonprofit",
        "website",
        "one_liner",
        "long_description",
        "small_logo_thumb_url",
        "launched_at",
        "tags",
        "former_names",
    ]
    ordered = [k for k in preferred if k in keys]
    for k in sorted(keys):
        if k not in ordered:
            ordered.append(k)
    return ordered


def write_csv(rows: List[Dict[str, Any]], output_path: str) -> None:
    if not rows:
        # Ensure we still create an empty file with no rows if nothing fetched
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            pass
        return

    fieldnames = collect_fieldnames(rows)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: to_primitive(row.get(k)) for k in fieldnames})


def main() -> int:
    output_csv = "/Users/rubybui/code/YC-Scraper/yc_companies.csv"
    print("Fetching YC companies from Algolia…", flush=True)

    all_hits: List[Dict[str, Any]] = []
    fetched = 0
    for hit in iterate_all_hits():
        all_hits.append(hit)
        fetched += 1
        if fetched % 1000 == 0:
            print(f"Fetched {fetched}…", flush=True)

    print(f"Total hits fetched: {len(all_hits)}", flush=True)
    print(f"Writing CSV to {output_csv}…", flush=True)
    write_csv(all_hits, output_csv)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


