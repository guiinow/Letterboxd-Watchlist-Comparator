import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from justwatch import JustWatch


COUNTRY = "BR"
PROVIDER = "mubi"
CACHE_PATH = Path("cache/mubi_catalog.json")
OUTPUT_PATH = Path("filmes-mubi.csv")
CACHE_MAX_AGE = timedelta(days=7)
PAGE_SIZE = 100
PROVIDER_URL = "https://br.justwatch.com/br/provedor/mubi"
GRAPHQL_URL = "https://apis.justwatch.com/graphql"
GRAPHQL_HEADERS = {
    "Origin": "https://br.justwatch.com",
    "Referer": "https://br.justwatch.com/",
    "User-Agent": "Mozilla/5.0",
}
GRAPHQL_QUERY = """
query GetMubiMovies(
    $country: Country!
    $first: Int!
    $language: Language!
    $languageEnglish: Language!
    $after: String
    $filter: TitleFilter
) {
    popularTitles(
        country: $country
        filter: $filter
        first: $first
        sortBy: POPULAR
        after: $after
    ) {
        edges {
            cursor
            node {
                id
                objectId
                content(country: $country, language: $language) {
                    title
                    fullPath
                    originalReleaseYear
                }
                contentEnglish: content(country: $country, language: $languageEnglish) {
                    title
                }
            }
        }
        pageInfo {
            endCursor
            hasNextPage
        }
        totalCount
    }
}
"""
PROVIDER_RECORD_PATTERN = re.compile(
    r'"title":"(?P<title>[^"\\]*)",'
    r'"fullPath":"\\u002Fbr\\u002F(?P<kind>filme|serie)'
    r'\\u002F(?P<slug>[^"?]+)",'
    r'"originalReleaseYear":(?P<year>null|\d{4})'
)


def normalize_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""

    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def cache_is_fresh(cache_path: Path = CACHE_PATH) -> bool:
    if not cache_path.exists():
        return False

    modified_at = datetime.fromtimestamp(cache_path.stat().st_mtime, timezone.utc)
    return datetime.now(timezone.utc) - modified_at < CACHE_MAX_AGE


def read_cache(cache_path: Path = CACHE_PATH) -> list[dict[str, Any]]:
    with cache_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    return payload.get("films", [])


def write_cache(films: list[dict[str, Any]], cache_path: Path = CACHE_PATH) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "country": COUNTRY,
        "provider": PROVIDER,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "films": films,
    }
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def fetch_mubi_catalog_from_graphql() -> list[dict[str, Any]]:
    """Fetch every current MUBI movie from JustWatch's GraphQL API."""
    films: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    after = None

    while True:
        variables = {
            "country": COUNTRY,
            "first": PAGE_SIZE,
            "language": "pt",
            "languageEnglish": "en",
            "after": after,
            "filter": {"objectTypes": ["MOVIE"], "packages": ["mbi"]},
        }
        response = requests.post(
            GRAPHQL_URL,
            json={
                "operationName": "GetMubiMovies",
                "query": GRAPHQL_QUERY,
                "variables": variables,
            },
            headers=GRAPHQL_HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise ValueError(payload["errors"][0].get("message", "GraphQL error"))

        catalog = payload.get("data", {}).get("popularTitles") or {}
        for edge in catalog.get("edges", []):
            node = edge.get("node", {})
            content = node.get("content") or {}
            title_id = str(node.get("objectId") or node.get("id") or "")
            if not title_id or not content.get("title") or title_id in seen_ids:
                continue

            seen_ids.add(title_id)
            films.append(
                {
                    "id": title_id,
                    "title": content["title"],
                    "original_title": (node.get("contentEnglish") or {}).get("title"),
                    "year": content.get("originalReleaseYear"),
                }
            )

        page_info = catalog.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break

        next_cursor = page_info.get("endCursor")
        if not next_cursor or next_cursor == after:
            raise ValueError("GraphQL retornou um cursor de paginação inválido")
        after = next_cursor

    return films


def fetch_mubi_catalog_from_legacy_api() -> list[dict[str, Any]]:
    """Try the old JustWatch package API for compatibility."""
    client = JustWatch(country=COUNTRY)
    films: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    page = 1

    while True:
        response = client.search_for_item(
            providers=[PROVIDER],
            page=page,
            page_size=PAGE_SIZE,
        )
        items = response.get("items", [])
        if not items:
            break

        for item in items:
            title_id = item.get("id")
            title = item.get("title")
            if title_id is None or not title:
                continue

            title_id = str(title_id)
            if title_id in seen_ids:
                continue

            seen_ids.add(title_id)
            films.append(
                {
                    "id": title_id,
                    "title": title,
                    "original_title": None,
                    "year": item.get("original_release_year"),
                }
            )

        total_results = response.get("total_results")
        if total_results is not None and page * PAGE_SIZE >= total_results:
            break

        if len(items) < PAGE_SIZE:
            break

        page += 1

    return films


def fetch_mubi_catalog_from_provider_page() -> list[dict[str, Any]]:
    """Fetch the current MUBI movie catalog from JustWatch's public page."""
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    films: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    page = 1

    while True:
        url = PROVIDER_URL if page == 1 else f"{PROVIDER_URL}?page={page}"
        response = session.get(url, timeout=30)
        response.raise_for_status()

        page_items = []
        for match in PROVIDER_RECORD_PATTERN.finditer(response.text):
            data = match.groupdict()
            if data["kind"] != "filme" or data["slug"] in seen_ids:
                continue

            title_id = data["slug"]
            seen_ids.add(title_id)
            page_items.append(
                {
                    "id": title_id,
                    "title": data["title"],
                    "original_title": None,
                    "year": None if data["year"] == "null" else int(data["year"]),
                }
            )

        if not page_items:
            break

        films.extend(page_items)
        page_links = re.findall(r'href="/br/provedor/mubi\?page=(\d+)"', response.text)
        next_pages = [int(link) for link in page_links if int(link) > page]
        if not next_pages:
            break

        page = min(next_pages)

    return films


def load_mubi_catalog(cache_path: Path = CACHE_PATH) -> list[dict[str, Any]]:
    if cache_is_fresh(cache_path):
        return read_cache(cache_path)

    try:
        try:
            films = fetch_mubi_catalog_from_graphql()
        except (requests.RequestException, KeyError, TypeError, ValueError) as api_error:
            print(
                f"Aviso: API GraphQL indisponível ({api_error}); tentando a "
                "API antiga do pacote JustWatch.",
                file=sys.stderr,
            )
            try:
                films = fetch_mubi_catalog_from_legacy_api()
            except (requests.RequestException, KeyError, TypeError, ValueError) as legacy_error:
                print(
                    f"Aviso: API antiga indisponível ({legacy_error}); "
                    "usando a página pública do provedor.",
                    file=sys.stderr,
                )
                films = fetch_mubi_catalog_from_provider_page()

        if not films:
            raise ValueError("nenhum filme foi retornado pelo JustWatch")

        write_cache(films, cache_path)
        return films
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        print(f"Aviso: não foi possível consultar o JustWatch: {error}", file=sys.stderr)
        if cache_path.exists():
            print("Aviso: usando o cache antigo da MUBI.", file=sys.stderr)
            return read_cache(cache_path)
        return []


def compare_watchlist_with_mubi(
    watchlist_path: str | Path,
    output_path: str | Path = OUTPUT_PATH,
    cache_path: str | Path = CACHE_PATH,
) -> pd.DataFrame:
    """Return and save watchlist films currently listed on MUBI in Brazil."""
    watchlist = pd.read_csv(watchlist_path, encoding="utf-8-sig")
    required_columns = {"Name", "Year"}
    missing_columns = required_columns - set(watchlist.columns)
    if missing_columns:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(missing_columns))}")

    catalog = load_mubi_catalog(Path(cache_path))
    catalog_df = pd.DataFrame(catalog)
    if catalog_df.empty:
        matches = pd.DataFrame(columns=["Watchlist", "Year", "MUBI", "JustWatch ID"])
    else:
        watchlist = watchlist.copy()
        watchlist["match_title"] = watchlist["Name"].map(normalize_text)
        watchlist["match_year"] = pd.to_numeric(watchlist["Year"], errors="coerce")
        catalog_df["match_title"] = catalog_df["title"].map(normalize_text)
        if "original_title" not in catalog_df.columns:
            catalog_df["original_title"] = None
        catalog_df["match_original_title"] = catalog_df["original_title"].map(normalize_text)
        catalog_df["match_year"] = pd.to_numeric(catalog_df["year"], errors="coerce")

        catalog_titles = pd.concat(
            [
                catalog_df[["id", "title", "year", "match_title", "match_year"]],
                catalog_df[["id", "original_title", "year", "match_original_title", "match_year"]]
                .rename(columns={"original_title": "title", "match_original_title": "match_title"}),
            ],
            ignore_index=True,
        ).dropna(subset=["match_title"])

        matches = watchlist.merge(
            catalog_titles,
            on=["match_title", "match_year"],
            how="inner",
        )
        matches = matches.rename(
            columns={
                "Name": "Watchlist",
                "title": "MUBI",
                "id": "JustWatch ID",
            }
        )[["Watchlist", "match_year", "MUBI", "JustWatch ID"]]
        matches = matches.rename(columns={"match_year": "Year"}).drop_duplicates()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matches.to_csv(output_path, index=False, encoding="utf-8")
    return matches


def main() -> None:
    watchlist_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "watchlist-guiinow-2026-02-02-22-14-utc.csv"
    )
    matches = compare_watchlist_with_mubi(watchlist_path)
    print(f"Filmes da watchlist encontrados na MUBI: {len(matches)}")
    print(f"Resultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
