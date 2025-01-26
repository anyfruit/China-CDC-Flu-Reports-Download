# China CDC Flu Report Extractor  

This repository contains two Python scripts designed to automate the process of downloading flu reports from the China CDC website and extracting key data from the reports.

## Requirements and Dependencies

To use these scripts, you need the following Python packages installed:

- `requests`: For making HTTP requests.
- `beautifulsoup4`: For web scraping.
- `pdfplumber`: For reading and extracting text and tables from PDF files.
- `pandas`: For organizing and saving the extracted data into a structured format.
- `openpyxl`: For saving data to Excel files.
- `json`: For handling metadata.

Install the dependencies using:
```bash
pip install requests beautifulsoup4 pdfplumber pandas openpyxl
```

## Usage
**Script 1: cdc_report_download.py**

Purpose: This script downloads flu reports (in PDF format) from the China CDC website.

Run the script:
```bash
python cdc_report_download.py
```
When prompted, enter the directory path where you want to save the PDF files.
How it works:

- Scrapes flu report links from the China CDC website.
- Filters reports by years (default: 2023 and 2024, configurable in the script).
- Downloads PDFs and stores metadata (e.g., publish dates) in metadata.json.

**Script 2: extract_pdf_table.py**

Purpose: This script extracts specific data from the downloaded PDF reports.

Run the script:
```bash
python extract_pdf_table.py
```

Enter:
The directory containing the downloaded PDF files.

The output directory for saving the extracted data.

How it works:

- Reads metadata.json for publish dates of each report.
- Extracts:
  - Key text data (e.g., ILI rates) from specific pages.
  - Tabular data (e.g., case counts, flu subtypes) from predefined table structures.
  - Saves the extracted data to an Excel file.

## File Outputs
Downloaded PDFs: Stored in the specified directory.

Metadata: metadata.json in the PDF directory.

Extracted Data: An Excel file containing structured data from the reports.

## Notes
Ensure the China CDC website structure remains consistent. Adjust selectors in the scripts if necessary.

Modify filtering criteria for report years or file naming patterns in the scripts as needed.

Tested for flu reports from 2023 and 2024. Earlier reports might require additional adjustments.

## Contact
Feel free to reach out if you encounter any issues or have suggestions for improvements!
