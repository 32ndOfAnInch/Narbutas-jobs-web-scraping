import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://karjera.narbutas.lt/jobs")


def is_cyrillic(text):
    return bool(re.search(r'[\u0400-\u04FF]', text))

def scrape_job_details(driver, url):
    driver.get(url)

    job_info = {
        "Responsibilities": [],
        "Requirements": [],
        "Offer": [],
        "Salary": ""
    }

    # Find all strong tags
    sections = driver.find_elements(By.CSS_SELECTOR, "p strong")

    for strong_tag in sections:
        title = strong_tag.text.strip()

        if title.startswith("PAGRINDINĖS ATSAKOMYBĖS"):
            ul = strong_tag.find_element(By.XPATH, "./ancestor::p/following-sibling::ul[1]")
            job_info["Responsibilities"] = [li.text.strip() for li in ul.find_elements(By.TAG_NAME, "li")]

        elif title.startswith("SĖKMINGAM DARBUI"):
            ul = strong_tag.find_element(By.XPATH, "./ancestor::p/following-sibling::ul[1]")
            job_info["Requirements"] = [li.text.strip() for li in ul.find_elements(By.TAG_NAME, "li")]

        elif title.startswith("KOMPANIJA SIŪLO"):
            ul = strong_tag.find_element(By.XPATH, "./ancestor::p/following-sibling::ul[1]")
            job_info["Offer"] = [li.text.strip() for li in ul.find_elements(By.TAG_NAME, "li")]

        elif title.startswith("Atlyginimas"):
            # Salary text is in the same <p>
            salary_text = strong_tag.find_element(By.XPATH, "./ancestor::p").text
            job_info["Salary"] = salary_text.replace("Atlyginimas", "").strip()

    return job_info

# --- 1. Expansion phase ---
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

# --- 2. Scraping phase ---
jobs_data = []
for el in driver.find_elements(By.CSS_SELECTOR, "#jobs_list_container li a"):
    title_el = el.find_element(By.CSS_SELECTOR, "span.text-block-base-link")
    title = title_el.text.strip() or title_el.get_attribute("title").strip()

    if title == "Karjeros galimybės ateityje":
        continue

    if is_cyrillic(title):
        continue

    link = el.get_attribute("href")
    jobs_data.append({"Title": title, "Link": link})

print(len(jobs_data), "jobs found")
print(jobs_data)
driver.quit()