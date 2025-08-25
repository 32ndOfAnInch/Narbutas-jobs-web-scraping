import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from webscrape_job_opening import (get_output_filename, save_to_csv,
                                   scrape_job_details)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://karjera.narbutas.lt/jobs")


def is_cyrillic(text):
    return bool(re.search(r'[\u0400-\u04FF]', text))

# Expanding load 10 more
while True:
    try:
        show_more = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#show_more_button a"))
        )

        current_count = len(driver.find_elements(By.CSS_SELECTOR, "#jobs_list_container li"))
        print(f"Jobs before click: {current_count}")

        # JS click triggers Turbo properly
        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", show_more)

        # Wait until new jobs appear
        WebDriverWait(driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#jobs_list_container li")) > current_count
        )

    except TimeoutException:
        break

# Collect links and scrape

job_links = []
for el in driver.find_elements(By.CSS_SELECTOR, "#jobs_list_container li a"):
    title_el = el.find_element(By.CSS_SELECTOR, "span.text-block-base-link")
    title = title_el.text.strip() or title_el.get_attribute("title").strip()

    # remove
    if title == "Karjeros galimybės ateityje":
        continue

    # remove jobs for foreigners
    if is_cyrillic(title):
        continue

    link = el.get_attribute("href")
    job_links.append((title, link))

# iterate over job links

output_file = get_output_filename()
job_number = 1
for title, link in job_links:
    details = scrape_job_details(driver, link)
    details["Title"] = title
    save_to_csv(details, job_number, output_file)
    job_number += 1

print(f"Saved {job_number-1} jobs into {output_file}")

driver.quit()