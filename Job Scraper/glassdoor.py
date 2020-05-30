from selenium import webdriver
import time
import pymongo
from bson import ObjectId
from apply import easy_app
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

# TODO: 1. update based on applied jobs 2. MOVE INTO mian.py, break into functions,

# init db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]


def get_jobs(job_dict, jobRole, joblist):
  # this counter is to avoid duplicate keys because of same companies posting different positions
  company_counter = 0
  for job in joblist:
    try:
      # each job element gets clicked
      job.click() 
      time.sleep(2)
    except WebDriverException:
      print("MODAL APPEARED")
      modal_close = driver.find_element_by_class_name("modal_closeIcon")
      modal_close.click()
      time.sleep(2)
      job.click()
      time.sleep(2)

    # elements
    company_element = driver.find_element_by_class_name("employerName")
    title_element = driver.find_element_by_class_name("title")
    # this try catch for the time when the job has expired and the apply now button does not exist
    try:
      apply_element = driver.find_element_by_class_name("applyButton")
      link_name = apply_element.text
      apply_link = ""
    except NoSuchElementException:
      print("THE JOB HAS EXPRED")
      apply_link = "job has expired"
    
    # element manipualted
    company_name = company_element.text.split("\n")[0]
    company_name = company_name.split(".")[0]
    job_title = title_element.text

    # if the apply link name is Easy Apply then we run the function to easy apply
    if link_name != "Easy Apply":
      # only get link if the apply now button exists
      if apply_link != "job has expired":
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
      if apply_link != "job has expired":
        easy_app(apply_element)
        easy_apply_link = company_name + " " + job_title

      if company_name in job_dict.keys():
        company_counter+=1
        print("Key EXISTS ", company_name)
        job_dict["web developer"][jobRole][company_name+str(company_counter)] = { "job link": easy_apply_link, "job title": job_title }
      else:
        job_dict["web developer"][jobRole][company_name] = { "job link": easy_apply_link, "job title": job_title }
  
  return job_dict

  
def glassdoor_scrape(db_id, driver, roles):
  if db_id == '':
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

          job_dict["web developer"]["'internship'"] = {}
        elif not job_dict["web developer"]["'internship'"]:
          jobs = get_jobs(job_dict, role, job_on_page)
        else:
          jobs = get_jobs(job_dict, role, job_on_page)

        # after getting the jobs on that page clicking to next page
        page_elem.click()
        time.sleep(2)
    else:
      if not job_dict["web developer"]:
        # we change the dictionary with the role 
        job_dict = { "web developer": { role: {} } }
        job_dict = get_jobs(job_dict, role, job_on_page)
        # after I get the job dict back I insert the internship key
        job_dict["web developer"]["'internship'"] = {}
      elif not job_dict["web developer"]["'internship'"]:
        jobs = get_jobs(job_dict, role, job_on_page)
      else:
        jobs = get_jobs(job_dict, role, job_on_page)  

  job_db_id = job_coll.insert_one(jobs)
  # writing to the file the id
  with open("ids.txt", 'a') as outfile:
    outfile.write(str(job_db_id.inserted_id)+"\n")
  print("----------------------------------\nJOBS INSERTED\n----------------------------------")
  driver.close()
  else:
    job_db_id = ObjectId(db_id)
    db_query = { "_id": job_db_id }
    db_jobs = job_coll.find(db_query)

    # this list is used to check if a job has been applied to
    job_links = []
    for job in db_jobs:
      # appending the part time links to the job_links arr 
      job_links = [job["web developer"]["'parttime'"][key]['job link'] for key in job["web developer"]["'parttime'"].keys()]
      # then appending the internship links
      for key in job["web developer"]["'internship'"].keys():
        job_links.append(job["web developer"]["'internship'"][key]['job link'])

    driver.close()


