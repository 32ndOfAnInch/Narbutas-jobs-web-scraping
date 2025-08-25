import datetime
import os

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# generate unique filenames
def get_output_filename(base="darbo_skelbimai"):
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{base}_{today}.csv"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base}_{today}_{counter}.csv"
        counter += 1
    return filename

# scrape a single job opening
def scrape_job_details(driver, url):
    driver.get(url)

    # Wait until job content loads
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "p strong"))
    )

    job_info = {
        "Pavadinimas": driver.title,
        "Pagrindinės atsakomybės": [],
        "Reikalavimai": [],
        "Ką siūlo įmonė": [],
        "Atlyginimas": ""
    }

    sections = driver.find_elements(By.CSS_SELECTOR, "p strong")
    for strong_tag in sections:
        title = strong_tag.text.strip().upper()

        # Responsibilities
        if title.startswith("PAGRINDINĖS ATSAKOMYBĖS"):
            uls = strong_tag.find_elements(By.XPATH, "./ancestor::p/following-sibling::ul")
            for ul in uls:
                lis = ul.find_elements(By.TAG_NAME, "li")
                if lis:
                    job_info["Pagrindinės atsakomybės"] = [li.text.strip() for li in lis if li.text.strip()]
                    break

        # Requirements
        elif title.startswith("SĖKMINGAM DARBUI"):
            uls = strong_tag.find_elements(By.XPATH, "./ancestor::p/following-sibling::ul")
            for ul in uls:
                lis = ul.find_elements(By.TAG_NAME, "li")
                if lis:
                    job_info["Reikalavimai"] = [li.text.strip() for li in lis if li.text.strip()]
                    break

        # Offer
        elif title.startswith("KOMPANIJA SIŪLO"):
            uls = strong_tag.find_elements(By.XPATH, "./ancestor::p/following-sibling::ul")
            for ul in uls:
                lis = ul.find_elements(By.TAG_NAME, "li")
                if lis:
                    job_info["Ką siūlo įmonė"] = [li.text.strip() for li in lis if li.text.strip()]
                    break

        # Salary
        elif title.startswith("ATLYGINIMAS"):
            salary_p = strong_tag.find_element(By.XPATH, "./ancestor::p")
            following_ps = salary_p.find_elements(By.XPATH, "./following-sibling::p")
            for p in following_ps:
                text = p.text.strip()
                if text and text[0].isdigit():  # starts with a number
                    job_info["Atlyginimas"] = text
                    break

    return job_info

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

# For testing
if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    test_link = "https://karjera.narbutas.lt/jobs/6276158-projektu-vadovas-e"  # test link
    filename = get_output_filename()
    details = scrape_job_details(driver, test_link)
    save_to_csv(details, job_number=1, filename=filename)
    driver.quit()
