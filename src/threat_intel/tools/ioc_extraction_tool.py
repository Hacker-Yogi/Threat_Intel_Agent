from crewai.tools import BaseTool
from iocextract import (
    extract_ips,
    extract_urls,
    extract_hashes
)
import re
import hashlib
from typing import List, Dict
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)


class DeterministicIOCExtractor(BaseTool):
    name: str = "deterministic_ioc_extractor"
    description: str = (
        "Deterministically extract raw IOCs from articles using iocextract "
        "and regex. No normalization or inference."
    )

    def _run(self, data) -> Dict:
         # CrewAI may pass the whole previous task output
        if isinstance(data, dict) and "articles" in data:
            articles = data["articles"]
        else:
            articles = data
    
        per_article = []
        global_iocs = {
            "ips_raw": set(),
            "urls_raw": set(),
            "hashes_raw": set(),
            "cves": set()
        }

        for article in articles:
            text = article.get("text", "")
            url = article.get("url", "")

            article_iocs = {
                "ips_raw": list(extract_ips(text)),
                "urls_raw": list(extract_urls(text)),
                "hashes_raw": list(extract_hashes(text)),
                "cves": re.findall(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE)
            }

            # stable article ID (important later)
            article_id = hashlib.sha256(url.encode()).hexdigest()

            per_article.append({
                "article_id": article_id,
                "url": url,
                "title": article.get("title"),
                "iocs": article_iocs
            })

            # aggregate globally
            for k in global_iocs:
                global_iocs[k].update(article_iocs[k])

        return {
            "per_article": per_article,
            "global_iocs": {k: sorted(v) for k, v in global_iocs.items()}
        }