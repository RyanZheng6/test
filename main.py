from Fetch_News_Article import fetch_news_api_articles, fetch_google_news_articles, process_articles
from Relevancy_Module import read_keywords, display_keywords_info
from Sentiment_Analysis import analyze_sentiment, generate_analysis_report
from Excel_Creation_App import create_excel_file
from Mailing_App import send_email
import argparse

def main():
    # Set up command line argument parsing - only for keywords file
    parser = argparse.ArgumentParser(description='News analysis tool for Nomura Holdings')
    parser.add_argument('--keywords', '-k', type=str, 
                      help='Path to custom keywords file (default: default_keywords.txt)')
    args = parser.parse_args()
    
    # Fixed query - always Nomura Holdings
    query = "Nomura Holdings"
    
    # Read keywords from specified file or use default
    keywords = read_keywords(args.keywords)
    display_keywords_info(keywords)

    # Fetch articles from both sources
    news_api_articles = fetch_news_api_articles(query)
    google_news_articles = fetch_google_news_articles(query)

    # Combine articles from both sources
    all_articles = news_api_articles + google_news_articles
    print(f"Total articles collected: {len(all_articles)}")

    # Process and filter articles
    filtered_articles = process_articles(all_articles, keywords)

    # Sort articles by relevance score
    filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    # Print only the top 10 filtered articles
    print('\nNomura Holdings news from the last week (Top 10):')
    max_articles_to_print = min(10, len(filtered_articles))
    for i, article in enumerate(filtered_articles[:max_articles_to_print]):
        print(f"[{i + 1}] Relevance Score: {article['relevance_score']}")
        print(article['title'])
        print(f"Source: {article.get('source', {}).get('name', 'Unknown')}")
        print(article.get('url', 'No URL'))
        print()

    print(f"Total relevant articles: {len(filtered_articles)} (showing top {max_articles_to_print})")

    # Analyze sentiment for top articles
    if filtered_articles:
        analyzed_articles, sentiments = analyze_sentiment(filtered_articles, max_articles=10)

        # Generate and print analysis report
        if analyzed_articles:
            report, list_of_reports = generate_analysis_report(analyzed_articles, sentiments)
            
            # Create Excel file with results
            excel_filename = f"{query}.xlsx"
            create_excel_file(excel_filename, query, 
                             ["Title", "Relevance Score", "Sentiment: Negative", 
                              "Summary: In This Article", "Source"],
                             list_of_reports)
            
            # Send email with results
            recipients = [
                "urvi.dedhia1@nomura.com",
                "trisha.saxena@nomura.com",
                "rutvika.dhande1@nomura.com",
                "ryan.zheng1@nomura.com",
                "atsushi.tahara@nomura.com",
                "poorvanshi.sharma1@nomura.com"
            ]
            send_email(excel_filename, recipients)
            
            print("\n" + "=" * 50 + "\n")
            print(report)

    else:
        print("No relevant Nomura Holdings articles found.")


if __name__ == "__main__":
    main()