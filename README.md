# World's Largest Banks Automated Data Pipeline





## Business Scenario & Problem Statement
**Scenario:** A strategic consulting firm that advises financial institutions needs to provide its clients with regular, up-to-date competitive intelligence. A key metric for this analysis is the market capitalization of the world's top banks.





## Executive Summary
This project successfully developed an automated ETL (Extract, Transform, Load) pipeline to address the firm's need for competitive financial data. The solution automatically extracts data on the world's top 10 largest banks from Wikipedia, transforms the market capitalization into key international currencies (GBP, EUR, PHP), and loads it into both a flexible CSV file and a structured SQLite database. This provides the consulting team with a reliable, queryable, and up-to-date dataset, saving significant manual effort and ensuring data accuracy for strategic analysis. The entire process is logged to guarantee data integrity and traceability.

**Problem:** Manually tracking this data is time-consuming, prone to human error, and inefficient. The firm needs an automated solution to gather, process, and store this data reliably, enabling analysts to access clean, multi-currency financial data on demand for their reports and client presentations.





## Project Objectives & Business Requirements
**Objective:** To create a repeatable, automated process for collecting and preparing data on the world's largest banks to support competitive analysis.

**Business Requirements:**
* **Data Source:** The system must extract data from the "By market capitalization" table on the designated Wikipedia page.
* **Data Scope:** The pipeline must capture the bank's name and its market capitalization in USD for the top 10 institutions listed.
* **Data Enrichment:** The market capitalization must be converted from USD to three additional currencies: British Pound (GBP), Euro (EUR), and Philippine Peso (PHP) to serve international stakeholders.
* **Data Accessibility:** The final, processed data must be delivered in two formats:
    * A **CSV file** for quick, ad-hoc analysis by analysts using tools like Excel.
    * A **SQLite database** to serve as a stable, queryable source for potential future dashboards or applications.
* **Data Quality & Governance:** The entire ETL process must be logged with timestamps to ensure traceability and allow for easy troubleshooting. The data loaded into the database must be verifiable through standard SQL queries.





## Data Sourcing
* **Source:** Wikipedia - List of largest banks
* **Specific Data Point:** The HTML table under the "By market capitalization" section.
Rationale: This publicly available source provides a regularly updated, structured list suitable for automated extraction, meeting the business need for timely competitive intelligence without requiring costly data subscriptions.





## ETL Process
The technical ETL pipeline is designed to directly meet the defined business requirements.
* **Extraction:** This phase fulfills the requirement of sourcing the data. The script targets the specific HTML table containing the relevant financial information, ensuring only the required data points (Bank Name, Market Cap) are captured.
* **Transformation:** This is the data enrichment phase. It applies the core business logic by converting the USD market cap into GBP, EUR, and PHP. This step adds value by making the data immediately usable for analysts working with different regional clients without needing manual conversions.
* **Loading:** This phase focuses on data delivery. By creating both a CSV and a database table, we serve two different user needs. The CSV offers flexibility, while the database provides structure and scalability for more advanced analytics.





## Data Validation & Quality Assurance
To ensure the integrity of the final dataset, several validation checks were implemented. After loading the data into the database, a series of SQL queries are automatically run to verify the process:
* Full Data Load Confirmation: SELECT * FROM Largest_banks is run to confirm that all records and columns were loaded correctly.
* Data Integrity Check: SELECT AVG(MC_GBP_Billion) is run to perform a calculation on the transformed data, ensuring the numeric conversions were successful.
* Record Spot-Check: SELECT Name FROM Largest_banks LIMIT 5 is run to quickly verify that the bank names were extracted and loaded as expected.
These queries serve as an automated quality assurance step, confirming the pipeline is functioning as intended.





## Project Deliverables
The project delivered the following key assets:
* **Automated Python Script (banks_project.py):** The core engine that performs the ETL process.
* **Formatted CSV File (largest_banks_data.csv):** The deliverable for analysts requiring flexible data access.
* **SQLite Database (banks.db):** The structured data source for robust, long-term analysis.
* **Process Log File (code_log.txt):** A complete audit trail of the pipeline's execution for governance and troubleshooting.





## Business Value
**Value Delivered:**
* **Increased Efficiency:** Eliminates hours of manual data collection and processing.
* **Improved Data Accuracy:** Reduces the risk of human error in data entry and currency conversion.
* **Enhanced Decision-Making:** Provides analysts with timely, reliable data to support client recommendations.





  
## 💻 Code Implementation Walkthrough
This section provides a detailed breakdown of the banks_project.py script, explaining each component of the ETL pipeline step-by-step.





### Preliminaries: Imports and Global Variables
First, we import the necessary libraries and define our global variables. This keeps the script organized and makes it easy to update paths or URLs in one place.

```python
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
```





### Task 1: The Logging Function (log_progress)
This utility function takes a message string, adds a current timestamp, and appends it to the log file. It's used at every stage to track progress.

```python
# --- Task 1: Logging Function ---
def log_progress(message):
    """Appends a timestamped log message to the log file."""
    timestamp_format = '%Y-%m-%d-%H:%M:%S'  # corrected format
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')
```





### Task 2: The Extraction Function (extract)
This is the core of the Extract phase. It sends an HTTP request, parses the HTML with BeautifulSoup, locates the correct table, reads it into a Pandas DataFrame, and performs crucial data cleaning.

```python
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
```





### Task 3: The Transformation Function (transform)
This Transform function enriches the data. It uses a hardcoded dictionary of exchange rates to calculate and add new columns for the market cap in GBP, EUR, and PHP.

```python
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
```





### Tasks 4 & 5: The Loading Functions (load_to_csv & load_to_db)
These two functions handle the Load phase. load_to_csv() saves the data to a CSV file, and load_to_db() saves it to a SQLite database table.

```python
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
```





### Task 6: The Query Function (run_queries)
To verify the data in the database, this function executes a given SQL query and prints the results to the console.

```python
# --- Task 6: Querying Database Function ---
def run_queries(query_statement, conn):
    """Runs a query on the database and prints the output."""
    print(f"Executing query: {query_statement}")
    query_output = pd.read_sql(query_statement, conn)
    print(query_output)
    print("-" * 30)
    log_progress(f'Query executed: {query_statement}')
```





### Orchestrating the ETL Pipeline
Finally, the main execution block calls each function in the correct ETL order and runs sample queries to demonstrate the final result.

```python
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
```





### 📊 Final Output
Running the script produces the following output in the console, showing the successful extraction, transformation, and querying of the data.


#### Extracted Data (Top 10 Banks)
| Rank | Name                                    | MC_USD_Billion |
|------|-----------------------------------------|----------------|
| 1    | JPMorgan Chase                          | 599.931        |
| 2    | Bank of America                         | 307.900        |
| 3    | Industrial and Commercial Bank of China | 303.543        |
| 4    | Agricultural Bank of China              | 232.836        |
| 5    | Bank of China                           | 209.295        |
| 6    | China Construction Bank                 | 192.715        |
| 7    | Wells Fargo                             | 192.279        |
| 8    | HSBC                                    | 163.544        |
| 9    | Commonwealth Bank                       | 156.639        |
| 10   | Goldman Sachs                           | 156.356        |



#### Transformed Data (with additional currencies) 
| Rank | Name                                    | MC_USD_Billion | MC_GBP_Billion | MC_EUR_Billion | MC_PHP_Billion |
|------|-----------------------------------------|----------------|----------------|----------------|----------------|
| 1    | JPMorgan Chase                          | 599.931        | 479.94         | 557.94         | 34796.00       |
| 2    | Bank of America                         | 307.900        | 246.32         | 286.35         | 17858.20       |
| 3    | Industrial and Commercial Bank of China | 303.543        | 242.83         | 282.29         | 17605.49       |
| 4    | Agricultural Bank of China              | 232.836        | 186.27         | 216.54         | 13504.49       |
| 5    | Bank of China                           | 209.295        | 167.44         | 194.64         | 12139.11       |
| 6    | China Construction Bank                 | 192.715        | 154.17         | 179.22         | 11177.47       |
| 7    | Wells Fargo                             | 192.279        | 153.82         | 178.82         | 11152.18       |
| 8    | HSBC                                    | 163.544        | 130.84         | 152.10         | 9485.55        |
| 9    | Commonwealth Bank                       | 156.639        | 125.31         | 145.67         | 9085.06        |
| 10   | Goldman Sachs                           | 156.356        | 125.08         | 145.41         | 9068.65        |





### Running Queries on the Database 



#### Query 1:
```SQL
SELECT * FROM Largest_banks
```
(Output is identical to the Transformed Data table above)



#### Query 2:
```SQL
SELECT AVG(MC_GBP_Billion) FROM Largest_banks
```
| AVG(MC_GBP_Billion) |
|----------------------|
| 201.202              |



#### Query 3:
```SQL
SELECT Name FROM Largest_banks LIMIT 5
```
| Name                                    |
|-----------------------------------------|
| JPMorgan Chase                          |
| Bank of America                         |
| Industrial and Commercial Bank of China |
| Agricultural Bank of China              |
| Bank of China                           |





## Project Outputs

* **`banks_project.py`:** The main Python script containing the full ETL logic.
* **`/output/largest_banks_data.csv`:** The final dataset in CSV format.
* **`/output/banks.db`:** The SQLite database containing the final dataset.
* **`/output/code_log.txt`:** A log file detailing the execution flow of the script.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/francissibal/Worlds-Largest-Banks-ETL.git](https://github.com/francissibal/Worlds-Largest-Banks-ETL.git)
    cd Worlds-Largest-Banks-ETL
    ```

2.  **Install dependencies:**
    ```bash
    pip install requests beautifulsoup4 pandas
    ```

3.  **Run the script:**
    ```bash
    python banks_project.py
    ```

4.  **Verify the output:**
    * Check for the creation of `largest_banks_data.csv` and `banks.db` in the `/output/` directory.
    * Review the `code_log.txt` file for a step-by-step log of the successful execution.






## Troubleshooting Note
During development, the target webpage's HTML structure, as seen by the script, was different from the browser's view. A diagnostic script (`troubleshooting/diagnostics.py`) was created to save the raw HTML received by Python. This allowed for accurate analysis and the creation of a robust final parser.
