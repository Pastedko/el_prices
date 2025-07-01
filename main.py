import os
import time
import glob
import sys
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# Print output immediately (helpful for Railway logs)
sys.stdout.reconfigure(line_buffering=True)
print("start script")

def send_email(subject, body):
    load_dotenv()
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("Starting the script...")

    # Set your download directory
    download_dir = os.path.abspath("downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Remove any old XLS files in the download directory
    for f in glob.glob(os.path.join(download_dir, "*.xls*")):
        os.remove(f)

    # Configure Selenium for Railway (Chromium & Chromedriver)
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    })
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    html_file = None

    try:
        print("Opening the website...")
        driver.get("https://ibex.bg/данни-за-пазара/пазарен-сегмент-ден-напред/day-ahead-prices-and-volumes-v2-0/")

        print("Clicking the download button...")
        button_xpath = "//button[contains(text(), 'XLS')]"
        download_button = driver.find_element(By.XPATH, button_xpath)
        download_button.click()

        # Wait for download to complete
        timeout = 40  # seconds
        xls_file = None
        for _ in range(timeout):
            xls_files = glob.glob(os.path.join(download_dir, "*.xls*"))
            if xls_files:
                xls_file = xls_files[0]
                if not xls_file.endswith(".crdownload"):
                    break
            time.sleep(1)
        else:
            raise Exception("Download did not complete in time.")

        print(f"Downloaded file: {xls_file}")

        # Rename to .html for pandas.read_html (works for IBEX export)
        html_file = xls_file
        if not xls_file.endswith('.html'):
            html_file = xls_file + ".html"
            os.rename(xls_file, html_file)

        print("Reading table from downloaded file...")
        tables = pd.read_html(html_file)
        df = tables[2]

        # Select only even rows (starting from 0), last column
        even_index_dict = {i: val for i, val in enumerate(df[df.columns[-1]][::2])}
        body = f"Ceni na toka za utre:\n{even_index_dict}"

        print("Preparing to send email...")
        send_email(
            subject="Electricity prices for tomorrow",
            body=body,
        )
        print("Data sent:", even_index_dict)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()
        if html_file and os.path.exists(html_file):
            os.remove(html_file)
            print(f"Deleted: {html_file}")

if __name__ == "__main__":
    main()
