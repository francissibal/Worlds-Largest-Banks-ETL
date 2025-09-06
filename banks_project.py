# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime

# --- Global Variables ---
URL = 'https://en.wikipedia.org/wiki/List_of_largest_banks'
EXCHANGE_RATE_CSV_PATH = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-SkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv'
OUTPUT_CSV_PATH = './Largest_banks_data.csv'
DB_NAME = 'Banks.db'
TABLE_NAME = 'Largest_banks'
LOG_FILE = 'code_log.txt'
TABLE_ATTRIBUTES = ['Name', 'MC_USD_Billion']
FINAL_TABLE_ATTRIBUTES = ['Name', 'MC_USD_Billion', 'MC_GBP_Billion', 'MC_EUR_Billion', 'MC_INR_Billion']

# --- Task 1: Logging Function ---
def log_progress(message):
    """Appends a timestamped log message to the log file."""
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Month-Day-Hour-Minute-Second
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')

# --- Task 2: Extraction Function ---
from io import StringIO # Required for the new pandas version

def extract(url, table_attribs):
    """
    Extracts the required table data from the given URL.
    This final version handles data types correctly and addresses pandas FutureWarning.
    """
    log_progress('Preliminaries complete. Initiating ETL process')
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url, headers=headers).text
    data = BeautifulSoup(page, 'html.parser')
    
    heading = data.find('h2', id='By_market_capitalization')
    table = heading.find_next('table')

    # Address the FutureWarning by wrapping the HTML string in a StringIO object
    df = pd.read_html(StringIO(str(table)))[0]
    
    df = df.head(10)
    df = df.iloc[:, [1, 2]]
    df.columns = table_attribs
    
    # --- DATA CLEANING FIX ---
    # 1. Explicitly convert the column to string type to use .str accessor
    df['MC_USD_Billion'] = df['MC_USD_Billion'].astype(str)
    
    # 2. Now, safely perform the string replacement to remove citations
    df['MC_USD_Billion'] = df['MC_USD_Billion'].str.replace(r'\[.*\]', '', regex=True)
    
    # 3. Finally, convert the cleaned strings to a numeric type
    df['MC_USD_Billion'] = pd.to_numeric(df['MC_USD_Billion'], errors='coerce')
    
    log_progress('Data extraction from HTML Webpage complete. Initiating Transformation process')
    return df

# --- Task 3: Transformation Function (UPDATED) ---
def transform(df, csv_path=None): # csv_path is no longer needed but kept for consistency
    """
    Transforms the dataframe by adding market capitalization in GBP, EUR, and INR.
    The exchange rates are now hardcoded to remove dependency on the broken URL.
    """
    # Exchange rates as of late 2024/early 2025 (for project consistency)
    exchange_rate_dict = {
        'GBP': 0.8,
        'EUR': 0.93,
        'INR': 83.33
    }

    # Get the specific exchange rates from our dictionary
    gbp_rate = exchange_rate_dict['GBP']
    eur_rate = exchange_rate_dict['EUR']
    inr_rate = exchange_rate_dict['INR']
    
    # Add new columns with converted market caps, rounded to 2 decimal places
    df['MC_GBP_Billion'] = round(df['MC_USD_Billion'] * gbp_rate, 2)
    df['MC_EUR_Billion'] = round(df['MC_USD_Billion'] * eur_rate, 2)
    df['MC_INR_Billion'] = round(df['MC_USD_Billion'] * inr_rate, 2)
    
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

    transformed_data = transform(extracted_data, EXCHANGE_RATE_CSV_PATH)
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

    print(f"\nProcess complete. Check the generated files: '{OUTPUT_CSV_PATH}', '{DB_NAME}', and '{LOG_FILE}'.")