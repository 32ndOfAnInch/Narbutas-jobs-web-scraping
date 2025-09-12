from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from scraping_utils import get_output_filename, save_to_csv


def extract_list_items(strong_tag):
    uls = strong_tag.find_elements(By.XPATH, "./ancestor::p/following-sibling::ul")
    for ul in uls:
        lis = ul.find_elements(By.TAG_NAME, "li")
        if lis:
            return [li.text.strip() for li in lis if li.text.strip()]
    return []


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
            job_info["Pagrindinės atsakomybės"] = extract_list_items(strong_tag)

        # Requirements
        elif title.startswith("SĖKMINGAM DARBUI"):
            job_info["Reikalavimai"] = extract_list_items(strong_tag)

        # Offer
        elif title.startswith("KOMPANIJA SIŪLO"):
            job_info["Ką siūlo įmonė"] = extract_list_items(strong_tag)

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


# For testing
if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        test_link = "https://karjera.narbutas.lt/jobs/6276158-projektu-vadovas-e"
        filename = get_output_filename()
        details = scrape_job_details(driver, test_link)
        save_to_csv(details, job_number=1, filename=filename)
        print(f"Saved test job to {filename}")
    finally:
        driver.quit()