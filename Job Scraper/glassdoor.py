from selenium import webdriver
import time
import pymongo
from apply import easy_app
from selenium.common.exceptions import WebDriverException

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]


driver = webdriver.Chrome()
driver.get("https://www.glassdoor.com/Job/ashburn-junior-web-developer-jobs-SRCH_IL.0,7_IC1130338_KO8,28.htm")
job_on_page = driver.find_elements_by_class_name("jl")

# get pagination
next_page_element = driver.find_element_by_xpath("//li[@class='page']/a")
next_page = next_page_element.get_attribute("href")
print(next_page)
next_page_number = next_page.split("=")
print(next_page_number)
next_page.click()

# job_dict = {}
# for job in job_on_page:
#   try:
#     # each job element gets clicked
#     job.click()
#     time.sleep(3)

#     # elements
#     company_element = driver.find_element_by_class_name("employerName")
#     title_element = driver.find_element_by_class_name("title")
#     apply_element = driver.find_element_by_class_name("applyButton")

#     # element manipualted
#     link_name = apply_element.text
#     company_name = company_element.text.split("\n")[0]
#     company_name = company_name.split(".")[0]
#     job_title = title_element.text

#     # print(company_name)
#     # if the apply link name is Easy Apply then we run the function to easy apply
#     if link_name != "Easy Apply":
#       apply_link = apply_element.get_attribute("href")
#       job_dict[company_name] = { "job link": apply_link, "job title": job_title }
#     else:
#       print("Easy apply")
#       job_dict[company_name] = { "job link": "easy", "job title": job_title }
#       easy_app(apply_element)
    
#   except WebDriverException:
#     print("MODAL APPEARED")
#     modal_close = driver.find_element_by_class_name("modal_closeIcon")
#     modal_close.click()

# job_coll.insert_one(job_dict)
# print("----------------------------------\nJOBS INSERTED\n----------------------------------")
# driver.close()