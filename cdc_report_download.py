import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json

# Base URL of the China CDC flu report page
base_url = "https://ivdc.chinacdc.cn/cnic/zyzx/lgzb/index.htm"

# Directory to save the downloaded PDF files
store_path = input('Enter path to store PDF files\n')
output_dir = store_path # Change directory path if needed
os.makedirs(output_dir, exist_ok=True)

# File to store metadata (publishing dates)
metadata_file = os.path.join(output_dir, "metadata.json")
metadata = {}

# Function to download PDF files using a session
def download_pdf(session, pdf_url, output_path, publish_date):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Referer': base_url  # Add referer header to indicate the source page
    }
    response = session.get(pdf_url, headers=headers)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {output_path}")
        # Store metadata for the downloaded PDF
        metadata[output_path] = {
            'publish_date': publish_date
        }
    else:
        print(f"Failed to download {pdf_url} - Status Code: {response.status_code}")

# Step 1: Create a session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
})

# Initialize current page URL and page counter for constructing URLs
current_page_url = base_url
page_counter = 0

while current_page_url:
    response = session.get(current_page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Successfully accessed page: {current_page_url}")

        # Step 2: Find all report links on the current page
        report_links = soup.find_all('li')
        for link in report_links:
            report_anchor = link.find('a', href=True)
            publish_date_span = link.find('span', class_="span_02")

            if report_anchor and publish_date_span:
                # Extract report page URL and publish date
                report_page_url = urljoin(current_page_url, report_anchor['href'])
                publish_date = publish_date_span.text.strip("()")

                # Only process reports from 2024 and 2023
                if not (publish_date.startswith("2024") or publish_date.startswith("2023")):
                # CHANGE HERE IF NEEDED OTHER YEARS
                    print(f"Skipping report from {publish_date}")
                    continue

                print(f"Accessing report page: {report_page_url}")
                report_response = session.get(report_page_url)

                if report_response.status_code == 200:
                    report_soup = BeautifulSoup(report_response.text, 'html.parser')
                    pdf_link = report_soup.find('a', href=lambda x: x and x.endswith('.pdf'))
                    if pdf_link:
                        pdf_url = urljoin(report_page_url, pdf_link['href'])
                        pdf_name = pdf_link.text.strip() or pdf_link['href'].split('/')[-1]
                        output_path = os.path.join(output_dir, pdf_name)

                        # Check if the PDF has already been downloaded
                        if os.path.exists(output_path):
                            print(f"PDF already exists: {output_path}")
                            continue

                        print(f"Found PDF link: {pdf_url}")
                        download_pdf(session, pdf_url, output_path, publish_date)
                        time.sleep(1)
                    else:
                        print(f"No PDF found on {report_page_url}")
                else:
                    print(f"Failed to access report page: {report_page_url} - Status Code: {report_response.status_code}")

        # Step 3: Increment the page counter and construct the next page URL
        page_counter += 1
        current_page_url = f"https://ivdc.chinacdc.cn/cnic/zyzx/lgzb/index_{page_counter}.htm"
        print(f"Moving to the next page: {current_page_url}")

        # Check if we've reached the end of available pages (optional limit)
        if page_counter >= 30:  # Adjust as needed
            print("Reached the last available page.")
            break

    else:
        print(f"Failed to access page: {current_page_url} - Status Code: {response.status_code}")
        break

# Save the metadata to a JSON file
with open(metadata_file, 'w', encoding='utf-8') as file:
    json.dump(metadata, file, ensure_ascii=False, indent=4)

print("Finished processing.")
print("Metadata has been saved.")
