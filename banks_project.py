# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- Global Variables ---
URL = 'https://en.wikipedia.org/wiki/List_of_largest_banks'

# use a subfolder for all generated files
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, 'largest_banks_data.csv')
DB_NAME = os.path.join(OUTPUT_DIR, 'banks.db')
TABLE_NAME = 'Largest_banks'
LOG_FILE = os.path.join(OUTPUT_DIR, 'code_log.txt')

TABLE_ATTRIBUTES = ['Name', 'MC_USD_Billion']
FINAL_TABLE_ATTRIBUTES = ['Name', 'MC_USD_Billion', 'MC_GBP_Billion', 'MC_EUR_Billion', 'MC_PHP_Billion']



# --- Task 1: Logging Function ---
def log_progress(message):
    """Appends a timestamped log message to the log file."""
    timestamp_format = '%Y-%m-%d-%H:%M:%S'  # corrected format
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')



# --- Task 2: Extraction Function ---
from io import StringIO  # Required for the new pandas version

def extract(url, table_attribs):
    """Extracts and cleans the required table data from the URL."""
    log_progress('Preliminaries complete. Initiating ETL process')
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(url, headers=headers).text
    data = BeautifulSoup(page, 'html.parser')
    
    heading = data.find('h2', id='By_market_capitalization')
    table = heading.find_next('table')

    df = pd.read_html(StringIO(str(table)))[0]
    
    df = df.head(10)
    # Correctly select the 1st (Bank Name) and 3rd (Market Cap) columns
    df = df.iloc[:, [0, 2]] 
    df.columns = table_attribs
    
    df['MC_USD_Billion'] = df['MC_USD_Billion'].astype(str)
    df['MC_USD_Billion'] = df['MC_USD_Billion'].str.replace(r'\[.*\]', '', regex=True)
    df['MC_USD_Billion'] = pd.to_numeric(df['MC_USD_Billion'], errors='coerce')
    
    log_progress('Data extraction from HTML Webpage complete. Initiating Transformation process')
    return df




# --- Task 3: Transformation Function ---
def transform(df):
    """
    Transforms the dataframe by adding market capitalization in GBP, EUR, and PHP.
    The exchange rates are now hardcoded to remove dependency on external CSV.
    """
    exchange_rate_dict = {
        'GBP': 0.8,     # 1 USD ≈ 0.80 GBP
        'EUR': 0.93,    # 1 USD ≈ 0.93 EUR
        'PHP': 58     # 1 USD ≈ 58 PHP (approx early 2025 rate)
    }

    df['MC_GBP_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['GBP'], 2)
    df['MC_EUR_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['EUR'], 2)
    df['MC_PHP_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['PHP'], 2)
    
    log_progress('Data transformation complete. Initiating loading process')
    return df




# --- Task 4: Loading to CSV Function ---
def load_to_csv(df, output_path):
    """Saves the dataframe to a CSV file."""
    df.to_csv(output_path, index=False)
    log_progress('Data saved to CSV file')



# --- Task 5: Loading to Database Function ---
def load_to_db(df, conn, table_name):
    """Loads the dataframe into an SQLite database table."""
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    log_progress('Data loaded to Database as table. Running the query')



# --- Task 6: Querying Database Function ---
def run_queries(query_statement, conn):
    """Runs a query on the database and prints the output."""
    print(f"Executing query: {query_statement}")
    query_output = pd.read_sql(query_statement, conn)
    print(query_output)
    print("-" * 30)
    log_progress(f'Query executed: {query_statement}')



# --- Main Execution Block ---
if __name__ == '__main__':
    log_progress('ETL Job Started')

    extracted_data = extract(URL, TABLE_ATTRIBUTES)
    print("--- Extracted Data (Top 10 Banks) ---")
    print(extracted_data)
    print("-" * 30)

    transformed_data = transform(extracted_data)
    print("\n--- Transformed Data (with additional currencies) ---")
    print(transformed_data)
    print("-" * 30)
    
    load_to_csv(transformed_data, OUTPUT_CSV_PATH)
    
    conn = sqlite3.connect(DB_NAME)
    log_progress('SQL Connection initiated')
    
    load_to_db(transformed_data, conn, TABLE_NAME)
    
    print("\n--- Running Queries on the Database ---")
    run_queries(f'SELECT * FROM {TABLE_NAME}', conn)
    run_queries(f'SELECT AVG(MC_GBP_Billion) FROM {TABLE_NAME}', conn)
    run_queries(f'SELECT Name FROM {TABLE_NAME} LIMIT 5', conn)
    
    conn.close()
    log_progress('SQL Connection closed')
    
    log_progress('ETL Job Ended')

    print(f"\nProcess complete. Check the generated files inside '{OUTPUT_DIR}':")
    print(f" - {OUTPUT_CSV_PATH}")
    print(f" - {DB_NAME}")
    print(f" - {LOG_FILE}")