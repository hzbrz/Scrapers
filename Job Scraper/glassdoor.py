import time
import pymongo
import uuid
from bson import ObjectId
from apply import easy_app
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

# init db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]


def get_jobs(job_dict, jobType, joblist, jobRole, driver, db_companies, db_titles):
  # this counter is to avoid duplicate keys because of same companies posting different positions
  company_counter = 0
  for job in joblist[:5]:
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
    # this try catch for the time when the 'job has expired' and the apply now button does not exist
    try:
      apply_element = driver.find_element_by_class_name("applyButton")
      link_name = apply_element.text
      apply_link = ""
    except NoSuchElementException:
      print("THE JOB HAS EXPRED")
      # if the 'job has expired' then the apply link & link name is:
      link_name = ""
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

      # print("CONDITION FOR JOB APPLIED: ", company_name in db_companies and job_title in db_titles, "\n")
      # print(company_name, job_title, "\n")
      if company_name in db_companies and job_title in db_titles:
        print("JOB HAS BEEN ALREADY APPLIED")
      else:
        # if the key already exists, this happens when the same company posts a different position
        if company_name in  job_dict[jobRole][jobType].keys():
          company_counter+=1
          print("Key EXISTS ", company_name)
          # if company name exists as a key we attach a counter to the key and then put it in the dict
          job_dict[jobRole][jobType][company_name+str(company_counter)] = { "job link": apply_link, "job title": job_title }
        else:
          job_dict[jobRole][jobType][company_name] = { "job link": apply_link, "job title": job_title }
    else:
      print("Easy apply")
      if apply_link != "job has expired":
        easy_apply_link = company_name + " " + job_title

      if company_name in db_companies and job_title in db_titles:
        print("EASY JOB HAS BEEN ALREADY APPLIED")
      else:
        if company_name in  job_dict[jobRole][jobType].keys():
          company_counter+=1
          print("Key EXISTS ", company_name)
          job_dict[jobRole][jobType][company_name+str(company_counter)] = { "job link": easy_apply_link, "job title": job_title }
        else:
          job_dict[jobRole][jobType][company_name] = { "job link": easy_apply_link, "job title": job_title }
        # if the job is not expired and has not already been applied to
        easy_app(apply_element)

  return job_dict

  
def glassdoor_scrape(db_id, driver, job_types, job_role, glassdoor_link):
  driver.get(glassdoor_link)
  if db_id == '':
    # this dict is to check and update the dictionary
    job_dict = { job_role: {} }

    # going through each jpb type for ex: part time or internship etc.
    for job_type in job_types:
      # job type clicks 
      job_type_elem = driver.find_element_by_xpath("//div[@id='filter_jobType']")
      job_type_elem.click()
      time.sleep(1)

      # click on the roles
      driver.find_element_by_xpath("//li[@value="+job_type+"]").click()
      time.sleep(2)

      # get pagination
      try: 
        next_page_elements = driver.find_elements_by_xpath("//li[@class='page']")
        pages = [page for page in next_page_elements]
        last_page = driver.find_element_by_xpath("//li[@class='page last']")  
        pages.append(last_page)
      except NoSuchElementException:
        print("NO PAGINATION/ ONLY 1 PAGE")

      if len(pages) > 0:
        page_counter = 0
        while page_counter <= len(pages):
          # job list 
          job_on_page = driver.find_elements_by_class_name("jl")
          if not job_dict[job_role]:
            job_dict = { job_role: { job_type: {} } }
            job_dict = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])

            job_dict[job_role]["'internship'"] = {}
            # print("IN If: ", job_dict, "PAGE COUNTER", page_counter)
          elif not job_dict[job_role][job_type]:
            # print("IN ELIF: ", job_dict, "PAGE COUNTER", page_counter)
            jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])
          else:
            # print("IN ELSE: ", job_dict, "PAGE COUNTER", page_counter)
            jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])
            print("AFTER ELSE: ", jobs)

          if page_counter != len(pages):
            # after getting the jobs on that page clicking to next page
            pages[page_counter].click()
            time.sleep(2)
            page_counter = page_counter + 1
          else:
            print("end of pages")
            page_counter = page_counter + 1
      else:
        # job list 
        job_on_page = driver.find_elements_by_class_name("jl")
        if not job_dict[job_role]:
          # we change the dictionary with the role 
          job_dict = { job_role: { job_type: {} } }
          job_dict = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])
          # after I get the job dict back I insert the internship key
          job_dict[job_role]["'internship'"] = {}
        elif not job_dict[job_role][job_type]:
          jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])
        else:
          jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [], [])  

    job_db_id = job_coll.insert_one(jobs)
    # writing to the file the id
    with open("ids.txt", 'a') as outfile:
      outfile.write(str(job_db_id.inserted_id)+"\n")
    print("----------------------------------\nJOBS INSERTED\n----------------------------------")
    driver.close()
  else:
    # db query
    job_db_id = ObjectId(db_id)
    db_query = { "_id": job_db_id }
    db_jobs = job_coll.find(db_query)

    # this list is used to check if a job has been applied to
    job_links = []
    for job in db_jobs:
      for job_type in job_types:
        job_type_elem = driver.find_element_by_xpath("//div[@id='filter_jobType']")
        job_type_elem.click()
        time.sleep(1)
        # click on the job type
        driver.find_element_by_xpath("//li[@value="+job_type+"]").click()
        time.sleep(2)

        try: 
          next_page_elements = driver.find_elements_by_xpath("//li[@class='page']")
          pages = [page for page in next_page_elements]
          last_page = driver.find_element_by_xpath("//li[@class='page last']")  
          pages.append(last_page)
        except NoSuchElementException:
          print("UPDATE: NO PAGINATION/ ONLY 1 PAGE")

        # company names and job titles from db
        company_names = [key for key in job[job_role][job_type].keys()]
        print(company_names)
        job_titles = [job[job_role][job_type][key]['job title'] for key in job[job_role][job_type].keys()]
        print(job_titles)

        # the dict has to be init here so that it gets rewrote every loop and this way the database is updated correctly
        job_dict = { job_role: { job_type: {} } }
        if len(pages) > 0:
          page_counter = 0
          while page_counter <= len(pages):
            # job list 
            job_on_page = driver.find_elements_by_class_name("jl")
            jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, company_names, job_titles)

            if page_counter != len(pages):
              # after getting the jobs on that page clicking to next page
              pages[page_counter].click()
              time.sleep(2)
              page_counter = page_counter + 1
            else:
              print("end of pages")
              page_counter = page_counter + 1
        else:
          # job list 
          job_on_page = driver.find_elements_by_class_name("jl")
          jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, company_names, job_titles)
        
        # looping through keys and checking 
        keys_from_update = jobs[job_role][job_type].keys()
        for job_key in keys_from_update:
          if job_key in company_names:
            # updating the old key with the new key
            unique_id = str(uuid.uuid4()).split("-")[0]
            jobs[job_role][job_type][job_key+"-"+unique_id] = jobs[job_role][job_type][job_key]
            # then deleting the old key
            del jobs[job_role][job_type][job_key]
        
        job[job_role][job_type].update(jobs[job_role][job_type])
        # print("AFTER JOB: ", job, "\n\n")
        # print("AFTER JOB ROLE: ", job[job_role], "\n\n")
        update = job_coll.find_one_and_update(
          {"_id": job_db_id},
          {"$set": { job_role: job[job_role] } }
        )

    driver.close()