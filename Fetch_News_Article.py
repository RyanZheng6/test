import requests
import json
import datetime
import os
import re
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline
from Relevancy_Module import calculate_relevance_score

def fetch_news_api_articles(query, days_back=7, api_key="641688cba56f4ae8b7ef0acb60543185"):
    """Fetch articles from News API."""
    print(f"Fetching articles from News API for: {query}")
    last_week = datetime.datetime.now() - datetime.timedelta(days=days_back)

    url = (
        'https://newsapi.org/v2/everything?'
        f'q="{query}"&'
        f'from={last_week.strftime("%Y-%m-%d")}&'
        'sortBy=popularity&'
        f'apiKey={api_key}'
    )

    try:
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            print(f"Retrieved {len(articles)} articles from News API")
            return articles
        else:
            print(f"Error fetching from News API: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Exception when fetching from News API: {e}")
        return []


def fetch_google_news_articles(query):
    """Fetch articles from Google News via RSS feed."""
    print(f"Fetching articles from Google News for: {query}")
    query_formatted = query.replace(' ', '+')
    rss_url = f"https://news.google.com/rss/search?q={query_formatted}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(rss_url)

        articles = []
        for entry in feed.entries:
            article = {
                'title': entry.title,
                'description': entry.get('description', ''),
                'content': entry.get('content', ''),
                'url': entry.link,
                'publishedAt': entry.get('published', ''),
                'source': {'name': 'Google News'}
            }

            # Try to get the actual source from the title
            title_parts = entry.title.split(' - ')
            if len(title_parts) > 1:
                article['source']['name'] = title_parts[-1]
                article['title'] = ' - '.join(title_parts[:-1])

            articles.append(article)

        print(f"Retrieved {len(articles)} articles from Google News")
        return articles
    except Exception as e:
        print(f"Exception when fetching from Google News: {e}")
        return []


def process_articles(articles, keywords):
    """Process and filter articles.
    
    Args:
        articles (list): List of articles to process
        keywords (dict or list): Keywords to use for relevance scoring
        
    Returns:
        list: Filtered and processed articles
    """
    filtered_articles = []
    min_relevance_score = 3  # Minimum score to consider an article relevant

    for article in articles:
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        content = article.get('content', '') or ''

        # Check if 'nomura' appears in the title, description or content
        if ('nomura' in title.lower() or
                'nomura' in description.lower() or
                'nomura' in content.lower()):
            # Combine all text for relevance scoring
            combined_text = f"{title} {description} {content}"
            relevance_score = calculate_relevance_score(combined_text, keywords)

            # Add relevance score to article if it meets the minimum threshold
            if relevance_score >= min_relevance_score:
                article['relevance_score'] = relevance_score
                filtered_articles.append(article)

    print(f"Filtered {len(filtered_articles)} relevant articles from {len(articles)} total articles")
    return filtered_articles