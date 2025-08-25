# Narbutas Jobs Web Scraping
Web scraping project for the Narbutas careers page using Python and Selenium.

## Main Goal
To practice using the Selenium library for scraping a large company's careers page.

## What's Inside?
- The program loads all job opening links and titles from [Narbutas Careers](https://karjera.narbutas.lt/jobs), including those revealed by the *"Load 10 more"* button.  
- It then loops through the list of jobs and scrapes all necessary information from each individual job page.  
- All job openings are saved into a CSV file with a unique filename (containing the current date and an incremental number if a file with the same date already exists).  
- Data is written using the **pandas** library.  
