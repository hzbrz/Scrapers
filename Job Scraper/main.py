from selenium import webdriver
from glassdoor import glassdoor_scrape

# job roles I am looking for
job_types = ["'parttime'", "'internship'"]

with open("ids.txt", 'r') as infile:
  mongo_id = infile.read()
  ids = mongo_id.split("\n")
print("id", ids)

# selenium driver
driver1 = webdriver.Chrome()
web_id = ids[0]

glassdoor_scrape(web_id, driver1, job_types, 
                 "web developer", "https://www.glassdoor.com/Job/ashburn-web-developer-jobs-SRCH_IL.0,7_IC1130338_KO8,21.htm")