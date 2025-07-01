import os
import time
import glob
import shutil
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    # Set up the MIMEText object
    msg = MIMEText(body)
    msg['Subject'] = subject

    load_dotenv() 
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECEIVER_EMAIL=os.getenv("RECEIVER_EMAIL")
    # Connect to Gmail SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())

# Set your download directory
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# Remove any old XLS files in the download directory
for f in glob.glob(os.path.join(download_dir, "*.xls*")):
    os.remove(f)

# Configure Chrome options for Selenium
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})
#chrome_options.add_argument("--headless")  # Uncomment if you want headless

# Initialize driver
chrome_options.binary_location = "/usr/bin/chromium"
chrome_options.add_argument("--headless")  # Always headless in CI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

try:
    # Step 1: Open the website
    driver.get("https://ibex.bg/данни-за-пазара/пазарен-сегмент-ден-напред/day-ahead-prices-and-volumes-v2-0/")  # CHANGE TO YOUR URL

    # Step 2: Find and click the download button (edit the selector as needed!)
    button_xpath = "//button[contains(text(), 'XLS')]"  # CHANGE THIS IF NEEDED!
    download_button = driver.find_element(By.XPATH, button_xpath)
    download_button.click()

    # Step 3: Wait for download to complete
    timeout = 30  # seconds
    xls_file = None
    for _ in range(timeout):
        xls_files = glob.glob(os.path.join(download_dir, "*.xls*"))
        if xls_files:
            xls_file = xls_files[0]
            # Check if the download is complete (not a .crdownload)
            if not xls_file.endswith(".crdownload"):
                break
        time.sleep(1)
    else:
        raise Exception("Download did not complete in time.")

    print(f"Downloaded file: {xls_file}")

    # --- CHANGES START HERE ---
    # Optionally, rename file extension to .html for clarity
    html_file = xls_file
    if not xls_file.endswith('.html'):
        html_file = xls_file + ".html"
        os.rename(xls_file, html_file)

    # Step 4: Read the file using pandas.read_html
    tables = pd.read_html(html_file)

    # Get Table 2
    df = tables[2]
    even_index_dict = {i: val for i, val in enumerate(df[df.columns[-1]][::2])}
    body = f"Ceni na toka za utre:\n{even_index_dict}"
    send_email(
    subject="Electricity prices for tomorrow",
    body=body,
    )
    print(even_index_dict)



finally:
    driver.quit()
    if html_file and os.path.exists(html_file):
        os.remove(html_file)
        print(f"Deleted: {html_file}")
