import requests
import json
import datetime
import os
import re
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline

# Create a txt file with financial keywords


def create_keyword_file_if_not_exists():
    if not os.path.exists('financial_keywords.txt'):
        with open('financial_keywords.txt', 'w') as f:
            keywords = [
                "bank",
                "finance",
                "market",
                "invest",
                "stock",
                "share",
                "bond",
                "asset",
                "capital",
                "fund",
                "trading",
                "financial",
                "securities",
                "investment",
                "debt",
                "corporate",
                "equity",
                "merger",
                "acquisition",
                "investor",
                "portfolio",
                "management",
                "risk",
                "liquidity",
                "profit",
                "revenue",
                "growth",
                "fiscal",
                "economic",
                "global",
                "advisor"
            ]
            f.write('\n'.join(keywords))


def read_keywords(filename):
    """Read keywords from a file."""
    with open(filename, 'r') as f:
        return [line.strip().lower() for line in f if line.strip()]


def calculate_relevance_score(text, keywords):
    """Calculate relevance score based on keyword occurrence."""
    if not text:
        return 0

    text = text.lower()
    score = 0

    for keyword in keywords:
        # Count occurrences of the keyword in the text
        # Use word boundary for single words to prevent partial matches
        if len(keyword.split()) == 1:
            # Use regex with word boundaries for single words
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
        else:
            count = text.count(keyword.lower())

        # Add to score (multi-word keywords get higher weight)
        word_count = len(keyword.split())
        score += count * word_count

    return score


def clean_html_content(html_content):
    """Extract readable text from HTML content."""
    if not html_content or not isinstance(html_content, str):
        return ""

    # Check if it looks like HTML
    if '<' in html_content and '>' in html_content:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            # Get text and clean it
            text = soup.get_text(strip=True)
            # Replace multiple spaces with single space
            text = re.sub(r'\s+', ' ', text)
            return text[:300] + "..." if len(text) > 300 else text
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return html_content[:300]
    else:
        # Not HTML, just return as is with length limit
        return html_content[:300] + "..." if len(html_content) > 300 else html_content


def create_custom_summary(article):
    """Create a simple summary based on article data."""
    title = article.get('title', '')
    description = article.get('description', '')
    content = article.get('content', '')
    source = article.get('source', {}).get('name', 'Unknown Source')

    summary = f"Title: {title}\n"

    # First try to get a clean description
    clean_desc = ""
    if description:
        clean_desc = clean_html_content(description)
        # Clean up the description
        clean_desc = re.sub(r'(subscribe|cookie|privacy|terms|browser)', '', clean_desc, flags=re.IGNORECASE)

    # If description didn't yield good results, try content
    if not clean_desc or len(clean_desc) < 20 or clean_desc.startswith("<a href="):
        if content:
            clean_content = clean_html_content(content)
            summary += f"Summary: {clean_content}\n"
        else:
            # If both are missing, just note that
            summary += "Summary: No summary available.\n"
    else:
        summary += f"Summary: {clean_desc}\n"

    summary += f"Source: {source}"
    return summary
