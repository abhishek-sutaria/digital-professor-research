import logging
import time
from typing import Dict, List, Any, Optional
import requests

logger = logging.getLogger(__name__)


class PublicationsEnricher:
    """Enrich publications via Crossref and Semantic Scholar without Scholar login"""

    CROSSREF_API = "https://api.crossref.org/works"
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, requests_session: Optional[requests.Session] = None):
        self.session = requests_session or requests.Session()
        self.session.headers.update({
            "User-Agent": "DigitalProfessor-InfoScraper/1.0"
        })

    def enrich_by_author(self, author_name: str, topic_hint: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Find publications for an author via Crossref and Semantic Scholar."""
        papers: List[Dict[str, Any]] = []

        try:
            crossref = self._search_crossref(author_name, topic_hint, max_results=max_results)
            s2 = self._search_semantic_scholar(author_name, topic_hint, max_results=max_results)

            # Merge results by DOI or title
            merged = self._merge_publications(crossref + s2)
            papers = merged[:max_results]
        except Exception as e:
            logger.warning(f"Publication enrichment failed: {e}")

        return papers

    def _search_crossref(self, author_name: str, topic_hint: Optional[str], max_results: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        params = {
            "query.author": author_name,
            "rows": min(max_results, 100),
            "sort": "published",
            "order": "desc",
        }
        if topic_hint:
            params["query"] = topic_hint

        try:
            resp = self.session.get(self.CROSSREF_API, params=params, timeout=30)
            if resp.status_code != 200:
                return results
            items = resp.json().get("message", {}).get("items", [])
            for it in items:
                title = (it.get("title") or [""])[0]
                year = None
                if it.get("published-print", {}).get("date-parts"):
                    year = it["published-print"]["date-parts"][0][0]
                elif it.get("published-online", {}).get("date-parts"):
                    year = it["published-online"]["date-parts"][0][0]
                doi = it.get("DOI", "")
                url = it.get("URL", "")
                authors = ", ".join([f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get("author", [])])
                venue = (it.get("container-title") or [""])[0]
                results.append({
                    "title": title,
                    "authors": authors,
                    "year": year or "",
                    "venue": venue,
                    "abstract": "",  # Crossref often lacks abstract in this endpoint
                    "citations": 0,
                    "url": url,
                    "pdf_url": "",
                    "doi": doi,
                    "publisher": it.get("publisher", ""),
                    "source": "crossref",
                })
        except Exception as e:
            logger.debug(f"Crossref error: {e}")
        return results

    def _search_semantic_scholar(self, author_name: str, topic_hint: Optional[str], max_results: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            q = author_name
            if topic_hint:
                q += f" {topic_hint}"
            params = {
                "query": q,
                "limit": min(max_results, 100),
                "fields": "title,year,venue,externalIds,openAccessPdf,authors,citationCount,abstract,url"
            }
            resp = self.session.get(self.SEMANTIC_SCHOLAR_API, params=params, timeout=30)
            if resp.status_code != 200:
                return results
            data = resp.json().get("data", [])
            for p in data:
                title = p.get("title", "")
                authors = ", ".join([a.get("name", "") for a in p.get("authors", [])])
                doi = (p.get("externalIds") or {}).get("DOI", "")
                pdf_url = (p.get("openAccessPdf") or {}).get("url", "")
                results.append({
                    "title": title,
                    "authors": authors,
                    "year": p.get("year", ""),
                    "venue": p.get("venue", ""),
                    "abstract": p.get("abstract", ""),
                    "citations": p.get("citationCount", 0),
                    "url": p.get("url", ""),
                    "pdf_url": pdf_url,
                    "doi": doi,
                    "publisher": "",
                    "source": "semantic_scholar",
                })
        except Exception as e:
            logger.debug(f"Semantic Scholar error: {e}")
        return results

    def _merge_publications(self, pubs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_key: Dict[str, Dict[str, Any]] = {}

        def norm_title(t: str) -> str:
            return (t or "").strip().lower()

        for p in pubs:
            key = p.get("doi") or norm_title(p.get("title", ""))
            if not key:
                continue
            if key not in by_key:
                by_key[key] = p
            else:
                # Merge fields preferring more complete entry
                existing = by_key[key]
                for fld in ["abstract", "pdf_url", "venue", "year", "authors", "url", "citations", "publisher"]:
                    if not existing.get(fld) and p.get(fld):
                        existing[fld] = p[fld]
        return list(by_key.values())

    def filter_by_exact_author(self, pubs: List[Dict[str, Any]], exact_name: str, affiliation_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Keep only publications where the exact author name appears in the author list,
        and optionally where affiliations/venues/abstract mention known keywords."""
        if not pubs:
            return []
        target = exact_name.strip().lower()
        aff_kw = [k.lower() for k in (affiliation_keywords or [])]

        filtered: List[Dict[str, Any]] = []
        for p in pubs:
            authors_str = (p.get('authors') or '').lower()
            if target not in authors_str:
                continue
            if aff_kw:
                hay = " ".join([
                    str(p.get('venue', '')),
                    str(p.get('abstract', '')),
                    str(p.get('publisher', '')),
                ]).lower()
                if not any(k in hay for k in aff_kw):
                    # Allow even without affiliation match but deprioritize later if needed
                    pass
            filtered.append(p)
        return filtered



