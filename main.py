import sys
from Relevancy_Module import create_keyword_file_if_not_exists, read_keywords
from Excel_Creation_App import create_Report
from Client_Manage_App import start_processing_clients

filename = sys.argv[1]
def main():
    # Initialize keyword file and read keywords
    create_keyword_file_if_not_exists()
    keywords = read_keywords('financial_keywords.txt')
    print(f"Using keywords: {', '.join(keywords[:10])}... and {len(keywords) - 10} more")

    #generate excel report
    reportname = create_Report()
    #Start processing each clients
    start_processing_clients(filename,keywords, reportname)

if __name__ == "__main__":
    main()
