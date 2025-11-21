import subprocess
import json
import os
import ssl
import socket
import requests
import datetime
import platform # New import to detect Windows
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv # New import

# --- CONFIGURATION ---
# This loads your .env file!
load_dotenv() 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Simulate a real browser to avoid being blocked by basic firewalls
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class SiteAuditor:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.report = {}

    def check_ssl_expiry(self):
        """Checks SSL certificate expiration date."""
        print("🔒 Checking SSL Certificate...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    # Date format example: 'May 25 23:59:59 2025 GMT'
                    expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (expire_date - datetime.datetime.now()).days
                    
                    status = "Critical" if days_left < 14 else "Good"
                    return {"days_remaining": days_left, "status": status}
        except Exception as e:
            return {"error": str(e), "status": "Error"}

    def run_lighthouse(self):
        """Runs Google Lighthouse for Core Web Vitals."""
        print("⚡ Running Google Lighthouse (this takes ~15s)...")
        filename = f"lighthouse_{self.domain}.json"
        
        # WINDOWS FIX: Detect if running on Windows and use .cmd
        lighthouse_cmd = "lighthouse.cmd" if platform.system() == "Windows" else "lighthouse"
        
        command = [
            lighthouse_cmd, self.url,
            "--output=json", f"--output-path={filename}",
            "--only-categories=performance,accessibility,seo",
            "--chrome-flags=--headless --no-sandbox", "--quiet"
        ]
        try:
            # shell=True helps Windows find the path sometimes, but .cmd is the safer fix
            subprocess.run(command, check=True)
            
            with open(filename, "r", encoding='utf-8') as f: # Added utf-8 encoding for safety
                data = json.load(f)
            os.remove(filename) # Clean up
            
            return {
                "performance_score": int(data["categories"]["performance"]["score"] * 100),
                "accessibility_score": int(data["categories"]["accessibility"]["score"] * 100),
                "mobile_speed_index": data["audits"]["speed-index"]["displayValue"]
            }
        except FileNotFoundError:
            print("❌ Error: Lighthouse not found.")
            print("   Run 'npm install -g lighthouse' in your terminal.")
            return {"error": "Lighthouse not installed"}
        except Exception as e:
            print(f"❌ Lighthouse failed: {e}")
            return {"error": "Could not run Lighthouse"}

    def check_page_health(self):
        """Scrapes the homepage for broken links, meta tags, and viewport."""
        print("🕷️ Crawling homepage for health metrics...")
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Meta Tags Check
            title = soup.title.string if soup.title else None
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_desc_content = meta_desc["content"] if meta_desc else None
            viewport = soup.find("meta", attrs={"name": "viewport"})
            h1 = soup.find("h1")

            # 2. Broken Link Checker (Internal Links Only)
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            internal_links = []
            for link in set(links): # Use set to remove duplicates
                full_url = urljoin(self.url, link)
                if self.domain in full_url:
                    internal_links.append(full_url)
            
            # Check up to 15 internal links to keep it fast
            broken_links = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = executor.map(self._check_link_status, internal_links[:15])
                for link, status in results:
                    if status >= 400:
                        broken_links.append(link)

            return {
                "title_tag": "Missing" if not title else "Good",
                "meta_description": "Missing" if not meta_desc_content else "Good",
                "h1_tag": "Missing" if not h1 else "Good",
                "mobile_viewport": "Missing (Critical for Mobile)" if not viewport else "Good",
                "broken_links_found": len(broken_links),
                "broken_link_examples": broken_links[:3] # Only show top 3
            }

        except Exception as e:
            return {"error": f"Crawl failed: {e}"}

    def _check_link_status(self, url):
        try:
            r = requests.head(url, headers=HEADERS, timeout=3)
            return url, r.status_code
        except:
            return url, 500

    def generate_hire_me_email(self, audit_data):
            """Uses OpenAI to write the Premium Consultant email."""
            print("🤖 Generating 'Miss Bott' Strategic Proposal...")
            
            if not OPENAI_API_KEY:
                return "ERROR: OpenAI API Key not found. Please check your .env file."

            client = OpenAI(api_key=OPENAI_API_KEY)
            
            prompt = f"""
            You are Miss Bott, a high-end Digital Consultant and Solutions Architect. You do not sell "bug fixes"; you sell high-performance digital transformations starting at €6,000.

            Write a cold outreach email to a business owner based on this audit of their website: {self.url}

            **Audit Findings:**
            - SSL/Security: {audit_data.get('ssl', {})} 
            - Performance: {audit_data.get('lighthouse', {})}
            - Health: {audit_data.get('health', {})} 

            **The Strategy (The "Why"):**
            - Treat these errors not as "small bugs" but as "symptoms of Technical Debt" caused by their current platform (likely WordPress).
            - Do NOT offer to "fix the links."
            - Explain that their current site is a liability (slow, insecure, leaking leads).
            - Propose a "Strategic Migration": Rebuilding the site on a modern, custom architecture (Python/Wagtail) to permanently solve these issues while preserving their brand and content.
            
            **Email Structure:**
            1. **Subject:** tailored to the most critical error (e.g., "Strategic concern regarding [Domain] performance")
            2. **The Hook:** Professional and concise. You analyzed their site as part of your market research.
            3. **The Diagnosis:** Reveal the data. Be direct. "Your site is scoring X. This indicates the underlying platform is struggling to scale."
            4. **The Pivot:** "Most agencies would offer to patch these errors for a fee. I advise against that. It’s a temporary fix for a structural problem."
            5. **The Solution:** Mention your premium service: A complete migration to a custom, high-speed stack.
            6. **The CTA:** Invite them for a "15-minute Strategy Review" to walk through the report. No sales pressure, just expert advice.
            
            **Tone:** Authoritative, sophisticated, expensive, yet helpful. Like a doctor giving a diagnosis.
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content

    def run_audit(self):
        # Aggregate all data
        self.report['ssl'] = self.check_ssl_expiry()
        self.report['lighthouse'] = self.run_lighthouse()
        self.report['health'] = self.check_page_health()
        
        # Generate Email
        email_draft = self.generate_hire_me_email(self.report)
        
        return {
            "technical_data": self.report,
            "email_draft": email_draft
        }

# --- EXECUTION ---
if __name__ == "__main__":
    target = input("Enter the website URL (e.g. https://example.com): ")
    auditor = SiteAuditor(target)
    result = auditor.run_audit()
    
    print("\n" + "="*30)
    print("🚩 TECHNICAL AUDIT REPORT")
    print("="*30)
    print(json.dumps(result['technical_data'], indent=2))
    
    print("\n" + "="*30)
    print("📧 DRAFTED EMAIL")
    print("="*30)
    print(result['email_draft'])