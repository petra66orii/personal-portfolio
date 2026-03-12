import datetime
import json
import os
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}


def _ollama_base_url():
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def _ollama_audit_model():
    return os.getenv("OLLAMA_AUDIT_MODEL", os.getenv("OLLAMA_MODEL", "mistral-nemo:12b"))


def _ollama_timeout():
    raw_timeout = os.getenv("OLLAMA_TIMEOUT", "120")
    try:
        return int(raw_timeout)
    except ValueError:
        return 120


class SiteAuditor:
    def __init__(self, url):
        self.url = url
        parsed = urlparse(url)
        self.domain = parsed.hostname or parsed.netloc
        self.report = {}

    def check_ssl_expiry(self):
        """Checks SSL certificate expiration date."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    expire_date = datetime.datetime.strptime(
                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                    )
                    days_left = (expire_date - datetime.datetime.now()).days
                    status = "Critical" if days_left < 14 else "Good"
                    return {"days_remaining": days_left, "status": status}
        except Exception as exc:
            return {"error": str(exc), "status": "Error"}

    def run_lighthouse(self):
        """Runs audit via Google PageSpeed Insights API."""
        api_key = os.getenv("GOOGLE_PAGESPEED_KEY")
        if not api_key:
            return {"error": "Missing GOOGLE_PAGESPEED_KEY in environment"}

        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": self.url,
            "key": api_key,
            "strategy": "mobile",
            "category": ["performance", "accessibility", "seo"],
        }

        try:
            response = requests.get(endpoint, params=params, timeout=120)
            if response.status_code != 200:
                return {"error": f"Google API failed: {response.status_code} - {response.text[:100]}"}

            data = response.json()
            lhs = data.get("lighthouseResult", {}).get("categories", {})
            return {
                "performance_score": int(lhs.get("performance", {}).get("score", 0) * 100),
                "accessibility_score": int(lhs.get("accessibility", {}).get("score", 0) * 100),
                "seo_score": int(lhs.get("seo", {}).get("score", 0) * 100),
                "core_web_vitals": data.get("loadingExperience", {}).get(
                    "overall_category", "Unavailable"
                ),
            }
        except Exception as exc:
            return {"error": f"Audit failed: {exc}"}

    def check_page_health(self):
        """Scrapes homepage for broken links and key metadata."""
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.title.string if soup.title else None
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_desc_content = meta_desc["content"] if meta_desc else None
            viewport = soup.find("meta", attrs={"name": "viewport"})
            h1 = soup.find("h1")

            links = [a.get("href") for a in soup.find_all("a", href=True)]
            internal_links = []
            for link in set(links):
                full_url = urljoin(self.url, link)
                full_hostname = urlparse(full_url).hostname or ""
                if full_hostname == self.domain:
                    internal_links.append(full_url)

            broken_links = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                results = executor.map(self._check_link_status, internal_links[:20])
                for link, status in results:
                    if status >= 400:
                        broken_links.append(link)

            return {
                "title_tag": "Missing" if not title else "Good",
                "meta_description": "Missing" if not meta_desc_content else "Good",
                "h1_tag": "Missing" if not h1 else "Good",
                "mobile_viewport": "Missing (Critical for Mobile)" if not viewport else "Good",
                "broken_links_found": len(broken_links),
                "broken_link_examples": broken_links[:3],
            }
        except Exception as exc:
            return {"error": f"Crawl failed: {exc}"}

    def _check_link_status(self, url):
        try:
            response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
            return url, response.status_code
        except Exception:
            return url, 500

    def _generate_with_ollama(self, prompt):
        payload = {
            "model": _ollama_audit_model(),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.7},
        }

        last_error = None
        for _ in range(2):
            try:
                response = requests.post(
                    f"{_ollama_base_url()}/api/chat",
                    json=payload,
                    timeout=_ollama_timeout(),
                )
                response.raise_for_status()
                content = (response.json().get("message") or {}).get("content", "").strip()
                if not content:
                    raise RuntimeError("Ollama returned an empty response")
                return content
            except Exception as exc:
                last_error = exc

        return f"ERROR: Ollama request failed after retries: {last_error}"

    def generate_hire_me_email(self, audit_data):
        """Uses a local Ollama model to draft outreach strategy email."""
        prompt = f"""You are Miss Bott, a high-end Digital Consultant and Solutions Architect.
You do not sell bug fixes; you sell high-performance digital transformations starting at EUR 6,000.

Write a cold outreach email to a business owner based on this audit of their website: {self.url}

Audit findings:
- SSL/Security: {audit_data.get('ssl', {})}
- Performance: {audit_data.get('lighthouse', {})}
- Health: {audit_data.get('health', {})}

Strategy:
- Treat issues as technical debt symptoms.
- Do not offer patchwork fixes.
- Explain risk: slow, insecure, lead leakage.
- Propose strategic migration to a modern custom architecture (Python/Wagtail) while preserving brand/content.

Email structure:
1) Subject tailored to critical issue.
2) Professional hook with context.
3) Data-based diagnosis.
4) Pivot away from temporary fixes.
5) Premium migration solution.
6) Invite to a 15-minute strategy review.

Tone: authoritative, sophisticated, expensive, helpful.

Required signature exactly:
--
Miss Bott
Digital Consultant & Solutions Architect
Email: developer@missbott.online
Website: https://missbott.online
"""
        return self._generate_with_ollama(prompt)

    def run_audit(self):
        self.report["ssl"] = self.check_ssl_expiry()
        self.report["lighthouse"] = self.run_lighthouse()
        self.report["health"] = self.check_page_health()

        email_draft = self.generate_hire_me_email(self.report)

        return {
            "technical_data": self.report,
            "email_draft": email_draft,
        }


if __name__ == "__main__":
    target = input("Enter the website URL (e.g. https://example.com): ")
    auditor = SiteAuditor(target)
    result = auditor.run_audit()

    print("\n" + "=" * 30)
    print("TECHNICAL AUDIT REPORT")
    print("=" * 30)
    print(json.dumps(result["technical_data"], indent=2))

    print("\n" + "=" * 30)
    print("DRAFTED EMAIL")
    print("=" * 30)
    print(result["email_draft"])
