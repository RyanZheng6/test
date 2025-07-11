import sys
import argparse
from Excel_Creation_App import create_Report
from Client_Manage_App import start_processing_clients

def main():
    parser = argparse.ArgumentParser(description='Client News Monitoring Service')
    parser.add_argument('clients_file', help='Path to the clients file (e.g., clients.txt)')
    parser.add_argument('--limit', type=int, help='Limit the number of articles to process per client')
    
    args = parser.parse_args()
    
    # Check if the clients file exists
    try:
        with open(args.clients_file, 'r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        print(f"Error: Clients file '{args.clients_file}' not found.")
        sys.exit(1)
    
    # Check if default_keywords.txt exists
    try:
        with open('default_keywords.txt', 'r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        print("Error: default_keywords.txt file not found.")
        print("Please ensure default_keywords.txt exists in the current directory.")
        sys.exit(1)
    
    # Generate excel report
    reportname = create_Report()
    print(f"Created report file: {reportname}")
    
    # Start processing each client
    start_processing_clients(args.clients_file, reportname, args.limit)
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()