from selenium import webdriver
from glassdoor import glassdoor_scrape
import time

# job roles I am looking for
job_types = ["'parttime'", "'internship'"]

# have to read file each time after updating
with open("ids.txt", 'r') as infile:
  mongo_id = infile.read()
  ids = mongo_id.split("\n")
print("id", ids)

# selenium driver specific to the job role
driver1 = webdriver.Chrome()
web_id = ids[0]
glassdoor_scrape(web_id, driver1, job_types, 
                 "web developer", "https://www.glassdoor.com/Job/herndon-web-developer-jobs-SRCH_IL.0,7_IC1130374_KO8,21.htm")

with open("ids.txt", 'r') as infile:
  mongo_id = infile.read()
  ids = mongo_id.split("\n")
print("id", ids)
driver2 = webdriver.Chrome()
software_id = ids[1]
glassdoor_scrape(software_id, driver2, job_types, 
                 "software engineer", "https://www.glassdoor.com/Job/herndon-software-development-engineer-intern-jobs-SRCH_IL.0,7_IC1130374_KO8,44.htm")

with open("ids.txt", 'r') as infile:
  mongo_id = infile.read()
  ids = mongo_id.split("\n")
print("id", ids)
driver3 = webdriver.Chrome()
data_entry_id = ids[2]
glassdoor_scrape(data_entry_id, driver3, job_types, 
                 "data entry", "https://www.glassdoor.com/Job/herndon-data-entry-jobs-SRCH_IL.0,7_IC1130374_KO8,18.htm")
                 