# ETL Project: World's Largest Banks by Market Capitalization

## Project Overview

This project is an automated ETL (Extract, Transform, Load) pipeline that scrapes data on the world's top 10 largest banks by market capitalization from Wikipedia. The script extracts the data, converts the market capitalization from USD to other major currencies (GBP, EUR, INR), and then saves the final dataset into a CSV file and a SQLite database. The entire process is logged for monitoring and verification.

This project demonstrates skills in web scraping, data cleaning and transformation with Pandas, data storage with SQLite, and process logging.

## Data Source

* **Webpage:** [List of largest banks - Wikipedia](https://en.wikipedia.org/wiki/List_of_largest_banks)
* **Target Table:** The data is extracted from the table under the "By market capitalization" section.

## ETL Pipeline Summary

1.  **Extract:** The script sends an HTTP request to the Wikipedia page and parses the HTML content using BeautifulSoup. It identifies the correct table, extracts the top 10 rows, and loads the data into a Pandas DataFrame.

2.  **Transform:** The initial DataFrame (containing Bank Name and Market Cap in USD) is transformed by:
    * Cleaning the market capitalization column to handle non-numeric characters (e.g., citation brackets).
    * Calculating and adding new columns for market capitalization in British Pounds (GBP), Euros (EUR), and Indian Rupees (INR) based on a predefined exchange rate dictionary.
    * Ensuring all currency values are rounded to 2 decimal places.

3.  **Load:** The final, transformed DataFrame is loaded into two destinations:
    * A local CSV file named `largest_banks_data.csv`.
    * A SQLite database table named `Largest_banks` inside `Banks.db`.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Worlds-Largest-Banks-ETL.git](https://github.com/YOUR_USERNAME/Worlds-Largest-Banks-ETL.git)
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

## Project Outputs

* **`banks_project.py`:** The main Python script containing the full ETL logic.
* **`/output/largest_banks_data.csv`:** The final dataset in CSV format.
* **`/output/banks.db`:** The SQLite database containing the final dataset.
* **`/output/code_log.txt`:** A log file detailing the execution flow of the script.

## Troubleshooting Note

During development, the target webpage's HTML structure, as seen by the script, was different from the browser's view. A diagnostic script (`troubleshooting/diagnostics.py`) was created to save the raw HTML received by Python. This allowed for accurate analysis and the creation of a robust final parser. This process highlights a common real-world challenge in web scraping.
