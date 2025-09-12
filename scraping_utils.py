import datetime
import os
import re

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def is_cyrillic(text):
    return bool(re.search(r'[\u0400-\u04FF]', text))


def expand_all_jobs(driver):
    while True:
        try:
            show_more = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#show_more_button a"))
            )
            current_count = len(driver.find_elements(By.CSS_SELECTOR, "#jobs_list_container li"))
            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", show_more)
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "#jobs_list_container li")) > current_count
            )
        except TimeoutException:
            break


def collect_job_links(driver):
    job_links = []
    for el in driver.find_elements(By.CSS_SELECTOR, "#jobs_list_container li a"):
        title_el = el.find_element(By.CSS_SELECTOR, "span.text-block-base-link")
        title = title_el.text.strip() or title_el.get_attribute("title").strip()
        if title == "Karjeros galimybės ateityje":
            continue
        if is_cyrillic(title):
            continue
        job_links.append((title, el.get_attribute("href")))
    return job_links


# generate unique filenames
def get_output_filename(base="darbo_skelbimai"):
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{base}_{today}.csv"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base}_{today}_{counter}.csv"
        counter += 1
    return filename


# Save to CSV
def save_to_csv(job_data, job_number, filename):
    numbered_title = f"{job_number}. {job_data.get('Pavadinimas','')}"
    df = pd.DataFrame({
        "Pavadinimas": [numbered_title],
        "Pagrindinės atsakomybės": ["\n".join(job_data.get("Pagrindinės atsakomybės", []))],
        "Reikalavimai": ["\n".join(job_data.get("Reikalavimai", []))],
        "Ką siūlo įmonė": ["\n".join(job_data.get("Ką siūlo įmonė", []))],
        "Atlyginimas": [job_data.get("Atlyginimas", "")],
        "Komentarai": [""],  # empty column for notes
    })

    write_header = not os.path.exists(filename)
    df.to_csv(filename, mode="a", index=False, header=write_header, encoding="utf-8-sig")
