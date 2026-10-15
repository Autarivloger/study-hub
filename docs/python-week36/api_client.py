"""Bounded read-only collectors for a local fixture or the public GitHub API."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import math
import re
import time
from urllib.parse import parse_qs, urlsplit
import requests


class APIError(RuntimeError):
    """A sanitised error: no token, URL query or response body in its message."""


def retry_delay(value, *, now=None):
    """Retry-After seconds or HTTP date; malformed hints are not guessed."""
    if value is None:
        return None
    value = value.strip()
    if re.fullmatch(r"[0-9]{1,9}", value):
        return float(value)
    try:
        stamp = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise APIError("Invalid Retry-After; stop for review") from None
    if stamp.tzinfo is None:
        raise APIError("Retry-After date requires a timezone")
    now = now or datetime.now(timezone.utc)
    return max(0.0, (stamp-now).total_seconds())


def validate_item(row):
    if not isinstance(row, dict):
        raise APIError("Expected an item object")
    if type(row.get("id")) is not int or not 1 <= row["id"] <= 2**63-1:
        raise APIError("Invalid item id")
    if not isinstance(row.get("title"), str) or not 1 <= len(row["title"]) <= 1000:
        raise APIError("Invalid title")
    if row.get("state") not in {"open", "closed"} or row.get("kind") not in {"issue", "pull_request"}:
        raise APIError("Invalid item category")
    if type(row.get("comments")) is not int or not 0 <= row["comments"] <= 2**63-1:
        raise APIError("Invalid comment count")
    return {key:row[key] for key in ("id","title","state","comments","kind")}


class APIClient:
    def __init__(self, base: str, token: str="", *, attempts: int=3, max_wait: float=10.0,
                 sleep=time.sleep, jitter=lambda:0.0):
        parsed = urlsplit(base)
        loopback = (parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
                    and parsed.port is not None and not parsed.path)
        github = base == "https://api.github.com"
        if not (loopback or github) or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Choose the loopback fixture or exact GitHub HTTPS origin")
        if type(attempts) is not int or not 1 <= attempts <= 5:
            raise ValueError("Require 1–5 attempts")
        if not math.isfinite(max_wait) or not 0 <= max_wait <= 60:
            raise ValueError("Require a finite wait budget from 0 to 60 seconds")
        if not isinstance(token, str) or any(c.isspace() or ord(c)<33 or ord(c)>126 for c in token):
            raise ValueError("Invalid token format")
        self.base, self.attempts, self.max_wait = base, attempts, max_wait
        self.sleep, self.jitter = sleep, jitter
        self.session = requests.Session()
        # Avoid ambient .netrc credentials/proxies in this explicitly scoped drill.
        self.session.trust_env = False
        self.session.headers.update({"Accept":"application/json","User-Agent":"StudyHub-Week36/1.0"})
        if token:
            self.session.headers["Authorization"] = "Bearer " + token

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def get_json(self, path: str, *, params: dict | None=None) -> tuple[object, dict]:
        if not re.fullmatch(r"/[A-Za-z0-9_/-]+", path) or "//" in path:
            raise ValueError("Require a fixed local API path")
        waited = 0.0
        for attempt in range(self.attempts):
            response = None
            hint = None
            try:
                response = self.session.get(self.base+path, params=params, timeout=(3.05,10),
                                            allow_redirects=False)
            except requests.exceptions.SSLError:
                raise APIError("TLS verification failed; stop") from None
            except (requests.Timeout, requests.ConnectionError):
                retry = True
            except requests.RequestException:
                raise APIError("Request failed; inspect configuration") from None
            else:
                status = response.status_code
                retry = status in {429,500,502,503,504}
                if status == 403:
                    # Provider-specific exhausted primary/secondary rate hints.
                    if response.headers.get("X-RateLimit-Remaining") == "0" or "Retry-After" in response.headers:
                        retry = True
                        if "Retry-After" not in response.headers:
                            try:
                                reset = float(response.headers["X-RateLimit-Reset"])
                            except (KeyError, ValueError):
                                response.close()
                                raise APIError("Rate limit exhausted; stop and inspect reset time") from None
                            if not math.isfinite(reset):
                                response.close()
                                raise APIError("Invalid rate reset time")
                            hint = max(0.0, reset-time.time())
                    else:
                        response.close()
                        raise APIError("HTTP 403: access denied; no automatic retry")
                if not retry:
                    try:
                        if not 200 <= status < 300:
                            raise APIError(f"HTTP {status}: request stopped")
                        if status == 204:
                            raise APIError("Expected JSON but received no content")
                        content_type = response.headers.get("Content-Type","").split(";")[0].strip().lower()
                        if content_type != "application/json" and not content_type.endswith("+json"):
                            raise APIError("Expected a JSON content type")
                        try:
                            payload = response.json()
                        except requests.exceptions.JSONDecodeError:
                            raise APIError("Malformed JSON response") from None
                        return payload, dict(response.links)
                    finally:
                        response.close()
                try:
                    if hint is None:
                        hint = retry_delay(response.headers.get("Retry-After"))
                finally:
                    response.close()
            if attempt+1 == self.attempts:
                raise APIError("GET retry attempts exhausted")
            noise = float(self.jitter())
            if not math.isfinite(noise) or not 0 <= noise <= 1:
                raise APIError("Invalid retry jitter")
            delay = hint if hint is not None else min(4.0, 0.5*2**attempt) + noise
            if not math.isfinite(delay) or delay > self.max_wait-waited:
                raise APIError("Required wait exceeds budget; stop rather than retry early")
            self.sleep(delay)
            waited += delay
        raise APIError("GET failed")

    def collect_mock(self, *, max_pages: int=10, max_items: int=1000) -> list[dict]:
        cursor, cursors, ids, rows = None, set(), set(), []
        if type(max_pages) is not int or not 1 <= max_pages <= 100 or type(max_items) is not int or not 1 <= max_items <= 10000:
            raise ValueError("Invalid collection bounds")
        for page in range(max_pages):
            payload, _ = self.get_json("/items", params={} if cursor is None else {"cursor":cursor})
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), list) or "next_cursor" not in payload:
                raise APIError("Invalid cursor-page envelope")
            for source in payload["items"]:
                item = validate_item(source)
                if item["id"] in ids:
                    raise APIError("Duplicate id across pages; collection may have changed")
                ids.add(item["id"]); rows.append(item)
                if len(rows) > max_items:
                    raise APIError("Item budget exhausted; no complete result")
            cursor = payload["next_cursor"]
            if cursor is None:
                return rows
            if not isinstance(cursor,str) or not cursor or len(cursor)>200 or cursor in cursors:
                raise APIError("Invalid or repeated cursor")
            cursors.add(cursor)
        raise APIError("Page budget exhausted; no complete result")

    def collect_github(self, repository: str, *, max_pages: int=10) -> list[dict]:
        if self.base != "https://api.github.com" or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository):
            raise ValueError("Require GitHub origin and owner/repository")
        if any(part in {".",".."} for part in repository.split("/")):
            raise ValueError("Invalid repository path components")
        if type(max_pages) is not int or not 1 <= max_pages <= 100:
            raise ValueError("Invalid page budget")
        path = "/repos/"+repository+"/issues"
        rows, ids = [], set()
        fixed = {"state":"all","per_page":100,"sort":"created","direction":"asc"}
        for page in range(1,max_pages+1):
            payload, links = self.get_json(path,params={**fixed,"page":page})
            if not isinstance(payload,list):
                raise APIError("Expected GitHub list")
            for source in payload:
                if not isinstance(source,dict):
                    raise APIError("Expected GitHub item object")
                item=validate_item({**source,"kind":"pull_request" if "pull_request" in source else "issue"})
                if item["id"] in ids:
                    raise APIError("Duplicate GitHub id; rerun/review changing pages")
                ids.add(item["id"]);rows.append(item)
                if len(rows)>10000:
                    raise APIError("Item budget exhausted")
            next_link = links.get("next",{}).get("url")
            if next_link is None:
                return rows
            # Inspect a next-page hint, but reconstruct the request from fixed values.
            parsed = urlsplit(next_link)
            query = parse_qs(parsed.query)
            expected = {**{k:[str(v)] for k,v in fixed.items()},"page":[str(page+1)]}
            if (parsed.scheme!="https" or parsed.netloc!="api.github.com" or parsed.path!=path
                    or parsed.fragment or query!=expected):
                raise APIError("Untrusted or inconsistent next-page link")
        raise APIError("Page budget exhausted; no complete result")
