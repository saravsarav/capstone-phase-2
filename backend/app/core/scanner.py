import httpx
import asyncio
from urllib.parse import urlparse, urlencode, parse_qs, urljoin
from typing import List, Dict


# ── Payloads ──────────────────────────────────────────────────────────────────

SQL_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
    "1; DROP TABLE users--",
    "' UNION SELECT NULL--",
]

SQL_ERROR_SIGNATURES = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "pg::syntaxerror",
    "sqlite3::exception",
    "odbc sql server driver",
    "ora-01756",
    "microsoft ole db provider for sql server",
    "syntax error or access violation",
]

XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "'\"><svg onload=alert(1)>",
    "<body onload=alert('xss')>",
]

OPEN_REDIRECT_PAYLOADS = [
    "https://evil.com",
    "//evil.com",
]

OPEN_REDIRECT_PARAMS = ["redirect", "url", "next", "return", "returnurl", "goto", "dest", "destination"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _inject_param(base_url: str, param_name: str, payload: str) -> str:
    """Append a test parameter with payload to the URL."""
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{param_name}={payload}"


def _get_existing_params(url: str) -> dict:
    parsed = urlparse(url)
    return parse_qs(parsed.query)


# ── Main Scanner ──────────────────────────────────────────────────────────────

async def scan_target(url: str) -> List[Dict]:
    """
    Modular Scanning Engine:
    - Source 1: HTTP Security Headers
    - Source 2: Server Banner / Tech Stack Disclosure
    - Source 3: Source Code Pattern Matching
    - Source 4: SQL Injection (Active - payload injection)
    - Source 5: Cross-Site Scripting / XSS (Active - reflection check)
    - Source 6: Open Redirect (Active - parameter injection)
    - Source 7: CORS Misconfiguration
    """
    vulnerabilities = []

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            headers = response.headers
            content = response.text.lower()
            original_text = response.text

            # ── Source 1: HTTP Security Headers ──────────────────────────────
            security_headers = {
                "X-Content-Type-Options": "Missing nosniff protection — browser may MIME-sniff responses.",
                "X-Frame-Options": "Clickjacking protection missing — page can be embedded in an iframe.",
                "Content-Security-Policy": "No CSP policy defined — allows inline scripts and XSS vectors.",
                "Strict-Transport-Security": "HSTS not enforced — connections can be downgraded to HTTP.",
                "Referrer-Policy": "No Referrer-Policy set — sensitive URL data may leak to third parties.",
                "Permissions-Policy": "No Permissions-Policy — browser features (camera, mic) unrestricted.",
            }
            for header, desc in security_headers.items():
                if header not in headers:
                    vulnerabilities.append({
                        "type": f"Missing Header: {header}",
                        "description": desc,
                        "evidence": f"Header '{header}' absent in HTTP response.",
                        "raw_severity": "Medium"
                    })

            # ── Source 2: Server Banner & Tech Stack Disclosure ───────────────
            if "Server" in headers:
                vulnerabilities.append({
                    "type": "Server Banner Disclosure",
                    "description": "Server identity broadcasted via HTTP headers, aiding attacker reconnaissance.",
                    "evidence": f"Server: {headers['Server']}",
                    "raw_severity": "Low"
                })
            if "X-Powered-By" in headers:
                vulnerabilities.append({
                    "type": "Technology Disclosure (X-Powered-By)",
                    "description": "Backend tech stack revealed — helps attackers target known CVEs.",
                    "evidence": f"X-Powered-By: {headers['X-Powered-By']}",
                    "raw_severity": "Low"
                })

            # ── Source 3: Source Code Pattern Matching ────────────────────────
            patterns = {
                "password":       "Potential hardcoded credentials found in JS/HTML source.",
                "eval(":          "Dangerous eval() usage detected — possible code injection vector.",
                "apikey":         "Potential API key leaked in frontend source code.",
                "secret":         "Possible secret token or key found in response body.",
                "private_key":    "Private key string pattern found in source.",
                "access_token":   "Access token potentially exposed in HTML/JS.",
            }
            for pattern, reason in patterns.items():
                if pattern in content:
                    vulnerabilities.append({
                        "type": "Source Code Exposure",
                        "description": reason,
                        "evidence": f"Pattern '{pattern}' detected in page source.",
                        "raw_severity": "High"
                    })

            # ── Source 4: SQL Injection (Active) ──────────────────────────────
            sqli_found = False
            for payload in SQL_PAYLOADS:
                if sqli_found:
                    break
                test_url = _inject_param(url, "id", payload)
                try:
                    sqli_resp = await client.get(test_url, timeout=8.0)
                    resp_lower = sqli_resp.text.lower()
                    for sig in SQL_ERROR_SIGNATURES:
                        if sig in resp_lower:
                            vulnerabilities.append({
                                "type": "SQL Injection",
                                "description": (
                                    "The application echoes SQL error messages when malicious input is injected. "
                                    "An attacker can extract, modify, or delete database records."
                                ),
                                "evidence": f"Payload '{payload}' triggered DB error signature: '{sig}'",
                                "raw_severity": "Critical"
                            })
                            sqli_found = True
                            break
                except Exception:
                    pass

            # ── Source 5: Cross-Site Scripting / XSS (Active) ─────────────────
            xss_found = False
            for payload in XSS_PAYLOADS:
                if xss_found:
                    break
                test_url = _inject_param(url, "q", payload)
                try:
                    xss_resp = await client.get(test_url, timeout=8.0)
                    # Check if the payload is reflected back unencoded in the response
                    if payload.lower() in xss_resp.text.lower():
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "description": (
                                "User-supplied input is reflected in the HTTP response without proper encoding. "
                                "Attackers can inject malicious scripts executed in victims' browsers."
                            ),
                            "evidence": f"Payload '{payload}' reflected unencoded in the response body.",
                            "raw_severity": "High"
                        })
                        xss_found = True
                except Exception:
                    pass

            # ── Source 6: Open Redirect (Active) ─────────────────────────────
            redirect_found = False
            for param in OPEN_REDIRECT_PARAMS:
                if redirect_found:
                    break
                for payload in OPEN_REDIRECT_PAYLOADS:
                    test_url = _inject_param(url, param, payload)
                    try:
                        # Don't follow redirects here — check Location header
                        redirect_resp = await client.get(test_url, timeout=8.0, follow_redirects=False)
                        location = redirect_resp.headers.get("Location", "")
                        if payload in location or "evil.com" in location:
                            vulnerabilities.append({
                                "type": "Open Redirect",
                                "description": (
                                    f"The '{param}' parameter controls redirect destination without validation. "
                                    "Attackers can redirect users to phishing or malware sites."
                                ),
                                "evidence": f"Param '{param}={payload}' → Location: {location}",
                                "raw_severity": "High"
                            })
                            redirect_found = True
                            break
                    except Exception:
                        pass

            # ── Source 7: CORS Misconfiguration ──────────────────────────────
            acao = headers.get("Access-Control-Allow-Origin", "")
            acac = headers.get("Access-Control-Allow-Credentials", "")
            if acao == "*":
                vulnerabilities.append({
                    "type": "CORS Misconfiguration",
                    "description": (
                        "Access-Control-Allow-Origin is set to wildcard (*). "
                        "Any external website can make cross-origin requests to this server."
                    ),
                    "evidence": "Access-Control-Allow-Origin: *",
                    "raw_severity": "Medium"
                })
            elif acao and acac.lower() == "true":
                vulnerabilities.append({
                    "type": "CORS Misconfiguration (Credentials)",
                    "description": (
                        "CORS allows credentials from a reflected or permissive origin. "
                        "This can lead to cross-origin authenticated session hijacking."
                    ),
                    "evidence": f"Access-Control-Allow-Origin: {acao} | Allow-Credentials: true",
                    "raw_severity": "High"
                })

    except Exception as e:
        vulnerabilities.append({
            "type": "Scan Interface Error",
            "description": f"Failed to reach target: {str(e)}",
            "evidence": "Network timeout or SSL/TLS error",
            "raw_severity": "Info"
        })

    return vulnerabilities
