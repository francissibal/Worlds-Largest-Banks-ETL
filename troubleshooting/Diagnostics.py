# --- THIS IS A SPECIAL DIAGNOSTIC SCRIPT ---
import requests
from datetime import datetime
import os

# --- Global Variables ---
URL = 'https://en.wikipedia.org/wiki/List_of_largest_banks'

# Use the same output folder as the main ETL script
OUTPUT_DIR = './troubleshooting'
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, 'code_log.txt')
OUTPUT_HTML_FILE = os.path.join(OUTPUT_DIR, 'page_source.html')

def log_progress(message):
    """Appends a timestamped log message to the shared log file."""
    timestamp_format = '%Y-%m-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(timestamp + ' : ' + message + '\n')

def run_diagnostic(url):
    """
    Downloads the HTML from the URL and saves it to a file for inspection.
    """
    log_progress('Starting diagnostic run.')
    print(f"Attempting to download page from: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        page_text = response.text
        
        with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(page_text)
            
        print("-" * 50)
        print(f"SUCCESS: The webpage content has been saved to the file: '{OUTPUT_HTML_FILE}'")
        print("Please check the contents of this file as instructed.")
        print("-" * 50)
        log_progress(f'Successfully saved HTML to {OUTPUT_HTML_FILE}.')

    except requests.exceptions.RequestException as e:
        error_message = f"CRITICAL ERROR: Failed to retrieve the webpage. Error: {e}"
        log_progress(error_message)
        print(error_message)

if __name__ == '__main__':
    run_diagnostic(URL)
