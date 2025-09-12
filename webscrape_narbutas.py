from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from scraping_utils import (collect_job_links, expand_all_jobs,
                            get_output_filename, save_to_csv)
from webscrape_job_opening import scrape_job_details


def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://karjera.narbutas.lt/jobs")

    expand_all_jobs(driver)
    job_links = collect_job_links(driver)

    # iterate over job links
    output_file = get_output_filename()
    job_number = 1
    for title, link in job_links:
        details = scrape_job_details(driver, link)
        details["Pavadinimas"] = title  # keep naming consistent with Lithuanian CSV
        save_to_csv(details, job_number, output_file)
        job_number += 1

    print(f"Saved {job_number-1} jobs into {output_file}")
    driver.quit()


if __name__ == "__main__":
    main()