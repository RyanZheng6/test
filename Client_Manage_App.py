from Fetch_News_Article import fetch_news_api_articles, fetch_google_news_articles, process_articles
from Sentiment_Analysis import analyze_sentiment, generate_analysis_report
from Excel_Creation_App import addClientDetails, createSummarySheet
from Mailing_App import send_email
from Relevancy_Module import get_client_keywords
from collections import Counter

def summarize_client_details(query, analyzed_articles, sentiments):
    sentiments_counter = Counter(sentiments)
    max_Sentiment = sentiments_counter.most_common(1)[0][0] if sentiments_counter else 'Neutral'
    number_of_articles = len(analyzed_articles)
    number_of_positives = sentiments_counter.get('Very Positive', 0) + sentiments_counter.get('Positive', 0)
    number_of_negatives = sentiments_counter.get('Very Negative', 0) + sentiments_counter.get('Negative', 0)
    return [query, 'link', max_Sentiment, number_of_articles, number_of_positives, number_of_negatives]

def specificQuery(query, filename, limit_articles=None):
    # Get client-specific keywords
    keywords = get_client_keywords(query)
    print(f"Using {len(keywords)} keywords for {query}")
    
    # Fetch articles from both sources
    news_api_articles = fetch_news_api_articles(query)
    google_news_articles = fetch_google_news_articles(query)

    # Combine articles from both sources
    all_articles = news_api_articles + google_news_articles
    print(f"Total articles collected: {len(all_articles)}")

    # Process and filter articles
    filtered_articles = process_articles(query, all_articles, keywords)

    # Sort articles by relevance score
    filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    # Apply article limit if specified
    if limit_articles:
        filtered_articles = filtered_articles[:limit_articles]
        print(f'\n{query} news from the last week (Top {limit_articles}):')
        max_articles_to_print = min(limit_articles, len(filtered_articles))
    else:
        print(f'\n{query} news from the last week (All articles):')
        max_articles_to_print = len(filtered_articles)

    # Print filtered articles
    for i, article in enumerate(filtered_articles[:max_articles_to_print]):
        print(f"[{i + 1}] Relevance Score: {article['relevance_score']}")
        print(article['title'])
        print(f"Source: {article.get('source', {}).get('name', 'Unknown')}")
        print(article.get('url', 'No URL'))
        print()

    print(f"Total relevant articles: {len(filtered_articles)} (showing {max_articles_to_print})")

    # Analyze sentiment for all filtered articles
    if filtered_articles:
        analyzed_articles, sentiments = analyze_sentiment(filtered_articles)

        # Generate and print analysis report
        if analyzed_articles:
            list_of_reports = generate_analysis_report(query, analyzed_articles, sentiments)
            addClientDetails(filename, query, ["Sr. No.", "Article Title", "Date", "Source", "Summary", "Url", "Relevance Score", "Sentiment Analysis"], list_of_reports)
            print("\n" + "=" * 50 + "\n")
            summary = summarize_client_details(query, analyzed_articles, sentiments)
            return summary
    else:
        print(f"No relevant {query} articles found.")
        return None

def mail_app(reportname):
    recipients = [
        "earlycareer-cnnm2@nomura.com"
    ]
    send_email(reportname, recipients)

def fetch_clients_list(filename):
    lines_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    lines_list.append(line)
        return lines_list
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None

def start_processing_clients(filename, reportname, limit_articles=None):
    clients = fetch_clients_list(filename)
    if clients is not None:
        summaries = []
        for client in clients:
            print(f"\n{'='*60}")
            print(f"Processing client: {client}")
            print(f"{'='*60}")
            summary = specificQuery(client, reportname, limit_articles)
            if summary is not None:
                summaries.append(summary)
        
        if summaries:
            createSummarySheet(reportname, 'Summary', 
                             ["Company", "Sheet Link", "Maximum Sentiment", "Total no of articles", "Positive Articles", "Negative Articles"], 
                             summaries)
        else:
            print("No summaries generated for any clients.")
    
    mail_app(reportname)