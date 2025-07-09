import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

def send_email(subject, body):
    load_dotenv()
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())

# Set your download directory
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# Remove any old XLS files in the download directory
for f in glob.glob(os.path.join(download_dir, "*.xls*")):
    os.remove(f)

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})
# Uncomment to run headless
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize driver with webdriver-manager (cross-platform, no manual path)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

xls_file = None
html_file = None

try:
    driver.get("https://ibex.bg/данни-за-пазара/пазарен-сегмент-ден-напред/day-ahead-prices-and-volumes-v2-0/")
    
    # Accept the cookie notice if present
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Ok']"))
        )
        ok_button.click()
        time.sleep(1)
    except Exception:
        pass  # No cookie popup found

    # Find and click the download XLS button
    button_xpath = "//button[contains(translate(text(), 'xls', 'XLS'), 'XLS')]"
    download_button = driver.find_element(By.XPATH, button_xpath)
    download_button.click()

    # Wait for download to complete
    timeout = 60
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

    # --- Use your preferred logic: rename .xls to .html, use read_html ---
    html_file = xls_file + ".html"
    os.rename(xls_file, html_file)

    # Read with pandas.read_html
    tables = pd.read_html(html_file)
    df = tables[2]  # third table on the page

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
