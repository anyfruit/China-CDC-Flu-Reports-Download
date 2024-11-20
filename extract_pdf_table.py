import pdfplumber
import re
import os
import pandas as pd
import json

# Directory containing the downloaded PDF reports
pdf_dir = './cdc_data_extract/CDC_Flu_Reports' # Change directory path if needed

# Path to the metadata file containing publish dates
metadata_file = './cdc_data_extract/CDC_Flu_Reports/metadata.json' # Change metadata path if needed

# Load metadata containing publish dates
with open(metadata_file, 'r', encoding='utf-8') as file:
    metadata = json.load(file)

# List to hold extracted data for each PDF
data_list = []

# Function to extract year, week, and series number from the file name
def extract_info_from_filename(filename):
    match = re.search(r'(\d{4})年第(\d{1,2})周第(\d+)期', filename)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

# Iterate over each PDF file in the directory
for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith('.pdf'):
        year, week, series_number = extract_info_from_filename(pdf_file)
        
        if not year or not week or not series_number:
            print(f"Could not extract year, week, or series number from {pdf_file}")
            continue

        # Construct the full path key as used in metadata.json
        metadata_key = f'cdc_data_extract/CDC_Flu_Reports/{pdf_file}'
        publish_date = metadata.get(metadata_key, {}).get('publish_date')
        
        # Debugging: Print to verify publish date retrieval
        print(f"Processing {pdf_file} - Metadata Key: {metadata_key} - Publish Date: {publish_date}")
        
        if not publish_date:
            print(f"Publish date not found for {pdf_file}")
            continue  # Skip if no publish date is found, or handle as needed

        file_path = os.path.join(pdf_dir, pdf_file)
        with pdfplumber.open(file_path) as pdf:
            # Extract ILI rate data from page 3
            if len(pdf.pages) >= 3:
                page_3 = pdf.pages[2]
                text_3 = page_3.extract_text()

                if text_3:
                    text_3 = ' '.join(text_3.split())
                    ili_south_match = re.search(r'南方省份哨点医院报告的ILI%为\s*(\d+\.\d+)%', text_3)
                    ili_north_match = re.search(r'北方省份哨点医院报告的ILI%为\s*(\d+\.\d+)%', text_3)

                    ili_south = ili_south_match.group(1) if ili_south_match else None
                    ili_north = ili_north_match.group(1) if ili_north_match else None
                else:
                    print(f"Could not extract ILI data from page 3 of {pdf_file}")
                    ili_south, ili_north = None, None

            # Check if the PDF has at least 4 pages for table data
            if len(pdf.pages) >= 4:
                page_4 = pdf.pages[3]
                table_data = page_4.extract_table()

                if table_data:
                    # Process the table data assuming a known structure and remove data in parentheses
                    south_data = [re.sub(r'\(.*?\)', '', row[1]) for row in table_data[2:] if row[1] is not None]
                    north_data = [re.sub(r'\(.*?\)', '', row[2]) for row in table_data[2:] if row[2] is not None]

                    # Append the data to data_list for both regions
                    for region, region_data, ili_rate in zip(['南方省份', '北方省份'], [south_data, north_data], [ili_south, ili_north]):
                        data_entry = {
                            'Year': year,
                            'Week': week,
                            'Series': series_number,
                            'Region': region,
                            'ILI_Rate': ili_rate,
                            '检测数': region_data[0] if len(region_data) > 0 else None,
                            '阳性数(%)': region_data[1] if len(region_data) > 1 else None,
                            'A型': region_data[2] if len(region_data) > 2 else None,
                            'A(H1N1)pdm09': region_data[3] if len(region_data) > 3 else None,
                            'A(H3N2)': region_data[4] if len(region_data) > 4 else None,
                            'A(unsubtyped)': region_data[5] if len(region_data) > 5 else None,
                            'B型': region_data[6] if len(region_data) > 6 else None,
                            'B未分系': region_data[7] if len(region_data) > 7 else None,
                            'Victoria': region_data[8] if len(region_data) > 8 else None,
                            'Yamagata': region_data[9] if len(region_data) > 9 else None,
                            'Publish_Date': publish_date  # Add the publish date to each entry
                        }
                        data_list.append(data_entry)
                else:
                    print(f"Table data could not be extracted from page 4 of {pdf_file}.")
            else:
                print(f"{pdf_file} does not have 4 pages.")

# Save extracted data to an Excel file if data is available
if data_list:
    df = pd.DataFrame(data_list)
    output_path = './cdc_流感周报提取数据.xlsx'
    df.to_excel(output_path, index=False)
    print(f"Data has been saved to {output_path}")
else:
    print("No data was extracted from the PDFs.")