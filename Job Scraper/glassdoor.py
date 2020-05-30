from selenium import webdriver
import time
import pymongo
from apply import easy_app
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

# init db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]
# job roles I am looking for
roles = ["'parttime'", "'internship'"]

# selenium driver
driver = webdriver.Chrome()
driver.get("https://www.glassdoor.com/Job/ashburn-web-developer-jobs-SRCH_IL.0,7_IC1130338_KO8,21.htm")

def get_jobs(job_dict, jobRole, joblist):
  # this counter is to avoid duplicate keys because of same companies posting different positions
  company_counter = 0
  for job in joblist[:6]:
    try:
      # each job element gets clicked
      job.click() 
      time.sleep(1)
    except WebDriverException:
      print("MODAL APPEARED")
      modal_close = driver.find_element_by_class_name("modal_closeIcon")
      modal_close.click()
      time.sleep(2)
      job.click()
      time.sleep(1)

    # elements
    company_element = driver.find_element_by_class_name("employerName")
    title_element = driver.find_element_by_class_name("title")
    apply_element = driver.find_element_by_class_name("applyButton")

    # element manipualted
    link_name = apply_element.text
    company_name = company_element.text.split("\n")[0]
    company_name = company_name.split(".")[0]
    job_title = title_element.text

    # if the apply link name is Easy Apply then we run the function to easy apply
    if link_name != "Easy Apply":
      apply_link = apply_element.get_attribute("href")
      # if the key already exists, this happens when the same company posts a different position
      if company_name in job_dict.keys():
        company_counter+=1
        print("Key EXISTS ", company_name)
        # if company name exists as a key we attach a counter to the key and then put it in the dict
        job_dict["web developer"][jobRole][company_name+str(company_counter)] = { "job link": apply_link, "job title": job_title }
      else:
        job_dict["web developer"][jobRole][company_name] = { "job link": apply_link, "job title": job_title }
    else:
      print("Easy apply")
      if company_name in job_dict.keys():
        company_counter+=1
        print("Key EXISTS ", company_name)
        job_dict["web developer"][jobRole][company_name+str(company_counter)] = { "job link": "easy", "job title": job_title }
      else:
        job_dict["web developer"][jobRole][company_name] = { "job link": "easy", "job title": job_title }
      easy_app(apply_element)
  
  return job_dict

# this dict is to check and update the dictionary
job_dict = { "web developer": {} }
for role in roles:
  # job type clicks 
  job_type_elem = driver.find_element_by_xpath("//div[@id='filter_jobType']")
  job_type_elem.click()
  time.sleep(1)

  # click on the roles
  driver.find_element_by_xpath("//li[@value="+role+"]").click()
  time.sleep(3)
  
  # job list 
  job_on_page = driver.find_elements_by_class_name("jl")

  # get pagination
  try: 
    next_page_elements = driver.find_elements_by_xpath("//li[@class='page']")
    pages = [page for page in next_page_elements]
    last_page = driver.find_element_by_xpath("//li[@class='page last']")  
    pages.append(last_page)
  except NoSuchElementException:
    print("NO PAGINATION/ ONLY 1 PAGE")

  if len(pages) > 0:
    for page_elem in pages:
      if not job_dict["web developer"]:
        job_dict = { "web developer": { role: {} } }
        job_dict = get_jobs(job_dict, role, job_on_page)
      else:
        job_dict["web developer"]["'internship'"] = {}
        jobs = get_jobs(job_dict, role, job_on_page)
      
      page_elem.click()
      time.sleep(2)
  else:
    # when the dictionary is empty, I have to do this to update the dict
    if not job_dict["web developer"]:
      # we change the dictionary with the role 
      job_dict = { "web developer": { role: {} } }
      job_dict = get_jobs(job_dict, role, job_on_page)
      # after I get the job dict back I insert the internship key
      job_dict["web developer"]["'internship'"] = {}
    elif not job_dict["web developer"]["'internship'"]:
      jobs = get_jobs(job_dict, role, job_on_page)
    else:
      # job_dict["web developer"]["'internship'"] = {}
      jobs = get_jobs(job_dict, role, job_on_page)

job_coll.insert_one(jobs)
print("----------------------------------\nJOBS INSERTED\n----------------------------------")
driver.close()