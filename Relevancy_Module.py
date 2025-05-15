import requests
import json
import datetime
import os
import re
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline

DEFAULT_KEYWORDS_FILE = 'default_keywords.txt'

def read_keywords(filename=None):
    """Read keywords and their weights from a file.
    
    Args:
        filename (str, optional): Path to keywords file. If None, uses default.
    
    Returns:
        dict: Dictionary of keywords and their weights
    """
    # If no filename provided or file doesn't exist, use default
    if not filename or not os.path.exists(filename):
        filename = DEFAULT_KEYWORDS_FILE
        
    if not os.path.exists(filename):
        print(f"Warning: Keywords file {filename} not found!")
        return {}
        
    print(f"Reading keywords from: {filename}")
    keywords_dict = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Check if the keyword has a weight
            if ':' in line:
                keyword, weight = line.rsplit(':', 1)
                try:
                    keywords_dict[keyword.strip().lower()] = int(weight.strip())
                except ValueError:
                    # If weight is not a valid integer, default to 1
                    keywords_dict[keyword.strip().lower()] = 1
            else:
                # Default weight is 1 if no weight specified
                keywords_dict[line.lower()] = 1
    
    return keywords_dict


def calculate_relevance_score(text, keywords):
    """Calculate relevance score based on keyword occurrence and their weights.
    
    If keywords is a list, treat all keywords with equal weight of 1.
    If keywords is a dict, use the weights provided in the dict.
    """
    if not text:
        return 0

    text = text.lower()
    score = 0

    # Check if keywords is a dictionary or list
    if isinstance(keywords, dict):
        # Dictionary with weights
        for keyword, weight in keywords.items():
            if len(keyword.split()) == 1:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            else:
                count = text.count(keyword.lower())
            
            word_count = len(keyword.split())
            score += count * word_count * weight
    else:
        # List of keywords (backwards compatibility)
        for keyword in keywords:
            if len(keyword.split()) == 1:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            else:
                count = text.count(keyword.lower())
            
            word_count = len(keyword.split())
            score += count * word_count

    return score


def display_keywords_info(keywords):
    """Display information about loaded keywords."""
    if isinstance(keywords, dict):
        total_keywords = len(keywords)
        if total_keywords == 0:
            print("No keywords loaded.")
            return
            
        # Count keywords by weight
        weight_counts = {}
        for keyword, weight in keywords.items():
            weight_counts[weight] = weight_counts.get(weight, 0) + 1
        
        # Sort keywords by weight for display
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        
        # Display summary information
        print(f"Loaded {total_keywords} keywords")
        print("Weight distribution:")
        for weight, count in sorted(weight_counts.items(), reverse=True):
            print(f"  - Weight {weight}: {count} keywords")
        
        print("Top keywords by weight:")
        for keyword, weight in sorted_keywords[:5]:
            print(f"  - {keyword} (weight: {weight})")
        
        if total_keywords > 5:
            print(f"  - and {total_keywords - 5} more keywords...")
    else:
        # For backward compatibility with list format
        print(f"Loaded {len(keywords)} keywords")
        if keywords:
            print(f"Sample keywords: {', '.join(keywords[:5])}" + 
                 (f"... and {len(keywords) - 5} more" if len(keywords) > 5 else ""))


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