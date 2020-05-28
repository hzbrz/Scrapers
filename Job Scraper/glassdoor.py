from selenium import webdriver
import time
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]


driver = webdriver.Chrome()
driver.get("https://www.glassdoor.com/Job/ashburn-junior-web-developer-jobs-SRCH_IL.0,7_IC1130338_KO8,28.htm")
job_on_page = driver.find_elements_by_class_name("jl")
# print(type(job_on_page))
# job_list = job_on_page[:5]
# print(job_list)

job_dict = {}
for job in job_on_page[:5]:
  try:
    job.click()
    
    company_element = driver.find_element_by_class_name("employerName")
    title_element = driver.find_element_by_class_name("title")
    apply_element = driver.find_element_by_class_name("applyButton")
    apply_link = apply_element.get_attribute("href")
    print(apply_link)
    print(apply_element.text)

    company_name = company_element.text.split("\n")[0]
    job_title = title_element.text

    job_dict[company_name] = { "job title": job_title }
    time.sleep(3)
  except:
    print("MODAL APPEARED")
    modal_close = driver.find_element_by_class_name("modal_closeIcon")
    modal_close.click()

print(job_dict)
# driver.close()