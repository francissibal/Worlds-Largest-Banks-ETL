# --- THIS IS A SPECIAL DIAGNOSTIC SCRIPT ---
import requests
from datetime import datetime

# --- Global Variables ---
URL = 'https://en.wikipedia.org/wiki/List_of_largest_banks'
LOG_FILE = 'code_log.txt'
OUTPUT_HTML_FILE = 'page_source.html'

def log_progress(message):
    """Appends a timestamped log message to the log file."""
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')

def run_diagnostic(url):
    """
    Downloads the HTML from the URL and saves it to a file for inspection.
    """
    log_progress('Starting diagnostic run.')
    print(f"Attempting to download page from: {url}")

    # Use headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # Add a timeout to prevent the script from hanging
        response = requests.get(url, headers=headers, timeout=15)
        
        # This will raise an error if the download failed (e.g., 404 Not Found)
        response.raise_for_status() 
        
        page_text = response.text
        
        # Save the received HTML to a file
        with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(page_text)
            
        print("-" * 50)
        print(f"SUCCESS: The webpage content has been saved to the file: '{OUTPUT_HTML_FILE}'")
        print("Please check the contents of this file as instructed.")
        print("-" * 50)
        log_progress(f'Successfully saved HTML to {OUTPUT_HTML_FILE}.')

    except requests.exceptions.RequestException as e:
        # This will catch any network errors, timeouts, or bad status codes
        error_message = f"CRITICAL ERROR: Failed to retrieve the webpage. Error: {e}"
        log_progress(error_message)
        print(error_message)

if __name__ == '__main__':
    run_diagnostic(URL)# --- THIS IS A SPECIAL DIAGNOSTIC SCRIPT ---