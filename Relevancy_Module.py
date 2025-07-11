import requests
import json
import datetime
import os
import re
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline

def read_keywords_with_weights(filename):
    """Read keywords with weights from a file."""
    keywords = {}
    
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. Using default keywords.")
        filename = 'default_keywords.txt'
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                # Check if line contains weight (keyword:weight format)
                if ':' in line:
                    parts = line.split(':', 1)
                    keyword = parts[0].strip().lower()
                    try:
                        weight = int(parts[1].strip())
                        # Ensure weight is between 1-5
                        weight = max(1, min(5, weight))
                    except ValueError:
                        print(f"Warning: Invalid weight for keyword '{keyword}'. Using default weight 3.")
                        weight = 3
                else:
                    # No weight specified, use default
                    keyword = line.lower()
                    weight = 3
                
                keywords[keyword] = weight
        
        print(f"Loaded {len(keywords)} keywords from {filename}")
        return keywords
    
    except Exception as e:
        print(f"Error reading keywords file {filename}: {e}")
        print("Using default keywords...")
        return read_keywords_with_weights('default_keywords.txt')

def get_client_keywords(client_name):
    """Get keywords for a specific client."""
    # Create filename from client name
    safe_filename = re.sub(r'[^\w\s-]', '', client_name)  # Remove special chars
    safe_filename = re.sub(r'[-\s]+', '_', safe_filename)  # Replace spaces/hyphens with underscores
    keywords_file = f"{safe_filename}.txt"
    
    print(f"Looking for keywords file: {keywords_file}")
    
    if os.path.exists(keywords_file):
        print(f"Using client-specific keywords from {keywords_file}")
        return read_keywords_with_weights(keywords_file)
    else:
        print(f"No client-specific keywords found for {client_name}. Using default keywords.")
        return read_keywords_with_weights('default_keywords.txt')

def calculate_relevance_score(text, keywords_dict):
    """Calculate relevance score based on keyword occurrence and weights."""
    if not text or not keywords_dict:
        return 0

    text = text.lower()
    score = 0

    for keyword, weight in keywords_dict.items():
        # Count occurrences of the keyword in the text
        # Use word boundary for single words to prevent partial matches
        if len(keyword.split()) == 1:
            # Use regex with word boundaries for single words
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
        else:
            count = text.count(keyword.lower())

        # Add to score (weight multiplies the base score)
        # Multi-word keywords get higher base weight
        word_count = len(keyword.split())
        base_score = count * word_count
        weighted_score = base_score * weight
        score += weighted_score

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