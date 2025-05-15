from Relevancy_Module import create_custom_summary
from textblob import TextBlob
import requests
import json
import datetime
import os
import re
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline


def analyze_sentiment(articles, max_articles=5):
    """Analyze sentiment for the top articles."""
    if not articles:
        return [], []

    print(f"Analyzing sentiment for top {min(max_articles, len(articles))} articles:")

    # Process top articles
    analyzed_articles = []
    sentiments = []

    def get_sentiment(polarity):
        """Convert polarity score to sentiment categories"""
        if polarity >= 0.6:
            return 'Very Positive'
        elif 0.2 <= polarity < 0.6:
            return 'Positive'
        elif -0.2 < polarity < 0.2:
            return 'Neutral'
        elif -0.6 <= polarity <= -0.2:
            return 'Negative'
        else:
            return 'Very Negative'

    for i, article in enumerate(articles[:max_articles]):
        # Create a custom summary
        summary = create_custom_summary(article)

        # Get sentiment
        blob = TextBlob(summary)
        sentiment = get_sentiment(blob.sentiment.polarity)

        # Store results
        analyzed_articles.append({
            'index': i + 1,
            'title': article['title'],
            'summary': summary,
            'relevance_score': article['relevance_score'],
            'sentiment': sentiment,
            'url': article.get('url', '')
        })
        sentiments.append(sentiment)

    return analyzed_articles, sentiments


def generate_analysis_report(articles, sentiments):
    """Generate a detailed analysis report."""
    if not articles:
        return "No articles available for analysis."

    report = "# Nomura Holdings News Analysis Report\n\n"
    report += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    report += f"Articles Analyzed: {len(articles)}\n\n"

    # Sentiment breakdown
    report += "## Sentiment Breakdown\n\n"
    sentiment_counts = {}
    for sentiment in sentiments:
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(sentiments)) * 100
        report += f"- {sentiment}: {count} articles ({percentage:.1f}%)\n"

    # Most relevant articles
    report += "\n## Most Relevant Articles\n\n"
    list_of_Reports = []
    for article in articles:
        report += f"### [{article['index']}] {article['title']}\n"
        report += f"Relevance Score: {article['relevance_score']}\n"
        report += f"Sentiment: {article['sentiment']}\n"

        # Extract and format summary
        summary_text = article['summary']
        # Remove HTML tags if present
        summary_text = re.sub(r'<.*?>', '', summary_text)
        # Remove "Title: " prefix if present in the summary
        summary_text = re.sub(r'^Title: .*\n', '', summary_text)
        # Ensure we don't have empty lines
        summary_text = '\n'.join(line for line in summary_text.split('\n') if line.strip())

        report += f"{summary_text}\n"
        report += f"URL: {article['url']}\n\n"
        list_of_Reports.append([article['title'],article['relevance_score'],article['sentiment'],article['summary'],article['url']])

    return report, list_of_Reports