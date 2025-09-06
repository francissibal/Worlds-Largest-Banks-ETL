# ETL Project: World's Largest Banks by Market Capitalization

## 📂 Project Overview

This project is an automated ETL (Extract, Transform, Load) pipeline that scrapes data on the world's top 10 largest banks by market capitalization from Wikipedia. The script extracts the data, converts the market capitalization from USD to other major currencies (GBP, EUR, INR), and then saves the final dataset into a CSV file and a SQLite database. The entire process is logged for monitoring and verification.

This project demonstrates skills in web scraping, data cleaning and transformation with Pandas, data storage with SQLite, and process logging.

## Data Source

* **Webpage:** [List of largest banks - Wikipedia](https://en.wikipedia.org/wiki/List_of_largest_banks)
* **Target Table:** The data is extracted from the table under the "By market capitalization" section.

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
  
## 💻 Code Implementation Walkthrough
This section provides a detailed breakdown of the banks_project.py script, explaining each component of the ETL pipeline step-by-step.

### Preliminaries: Imports and Global Variables
First, we import the necessary libraries and define our global variables. This keeps the script organized and makes it easy to update paths or URLs in one place.

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
from io import StringIO

# --- Global Variables ---
URL = 'https://en.wikipedia.org/wiki/List_of_largest_banks'
OUTPUT_CSV_PATH = './output/largest_banks_data.csv'
DB_NAME = './output/banks.db'
TABLE_NAME = 'Largest_banks'
LOG_FILE = './output/code_log.txt'
TABLE_ATTRIBUTES = ['Name', 'MC_USD_Billion']
```
### Task 1: The Logging Function (log_progress)
This utility function takes a message string, adds a current timestamp, and appends it to the log file. It's used at every stage to track progress.

```python
def log_progress(message):
    """Appends a timestamped log message to the log file."""
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(LOG_FILE, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')
```
### Task 2: The Extraction Function (extract)
This is the core of the Extract phase. It sends an HTTP request, parses the HTML with BeautifulSoup, locates the correct table, reads it into a Pandas DataFrame, and performs crucial data cleaning.

```python
from io import StringIO # Required for the new pandas version

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
This Transform function enriches the data. It uses a hardcoded dictionary of exchange rates to calculate and add new columns for the market cap in GBP, EUR, and INR.

```python
def transform(df):
    """Transforms the dataframe by adding market capitalization in GBP, EUR, and INR."""
    exchange_rate_dict = {
        'GBP': 0.8,
        'EUR': 0.93,
        'INR': 83.33
    }

    df['MC_GBP_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['GBP'], 2)
    df['MC_EUR_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['EUR'], 2)
    df['MC_INR_Billion'] = round(df['MC_USD_Billion'] * exchange_rate_dict['INR'], 2)
    
    log_progress('Data transformation complete. Initiating loading process')
    return df
```
### Tasks 4 & 5: The Loading Functions (load_to_csv & load_to_db)
These two functions handle the Load phase. load_to_csv() saves the data to a CSV file, and load_to_db() saves it to a SQLite database table.

```python
def load_to_csv(df, output_path):
    """Saves the dataframe to a CSV file."""
    df.to_csv(output_path, index=False)
    log_progress('Data saved to CSV file')

def load_to_db(df, conn, table_name):
    """Loads the dataframe into an SQLite database table."""
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    log_progress('Data loaded to Database as table. Running the query')
```

### Task 6: The Query Function (run_queries)
To verify the data in the database, this function executes a given SQL query and prints the results to the console.

```python
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
if __name__ == '__main__':
    log_progress('ETL Job Started')

    # Extract, Transform, Load
    extracted_data = extract(URL, TABLE_ATTRIBUTES)
    transformed_data = transform(extracted_data)
    load_to_csv(transformed_data, OUTPUT_CSV_PATH)
    
    # Connect to DB and Load
    conn = sqlite3.connect(DB_NAME)
    log_progress('SQL Connection initiated')
    load_to_db(transformed_data, conn, TABLE_NAME)
    
    # Run Verification Queries
    run_queries(f'SELECT * FROM {TABLE_NAME}', conn)
    run_queries(f'SELECT AVG(MC_GBP_Billion) FROM {TABLE_NAME}', conn)
    
    conn.close()
    log_progress('SQL Connection closed')
    log_progress('ETL Job Ended')
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
| Rank | Name                                    | MC_USD_Billion | MC_GBP_Billion | MC_EUR_Billion | MC_INR_Billion |
|------|-----------------------------------------|----------------|----------------|----------------|----------------|
| 1    | JPMorgan Chase                          | 599.931        | 479.94         | 557.94         | 49992.25       |
| 2    | Bank of America                         | 307.900        | 246.32         | 286.35         | 25657.31       |
| 3    | Industrial and Commercial Bank of China | 303.543        | 242.83         | 282.29         | 25294.24       |
| 4    | Agricultural Bank of China              | 232.836        | 186.27         | 216.54         | 19402.22       |
| 5    | Bank of China                           | 209.295        | 167.44         | 194.64         | 17440.55       |
| 6    | China Construction Bank                 | 192.715        | 154.17         | 179.22         | 16058.94       |
| 7    | Wells Fargo                             | 192.279        | 153.82         | 178.82         | 16022.61       |
| 8    | HSBC                                    | 163.544        | 130.84         | 152.10         | 13628.12       |
| 9    | Commonwealth Bank                       | 156.639        | 125.31         | 145.67         | 13052.73       |
| 10   | Goldman Sachs                           | 156.356        | 125.08         | 145.41         | 13029.15       |


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

## Troubleshooting Note

During development, the target webpage's HTML structure, as seen by the script, was different from the browser's view. A diagnostic script (`troubleshooting/diagnostics.py`) was created to save the raw HTML received by Python. This allowed for accurate analysis and the creation of a robust final parser.
