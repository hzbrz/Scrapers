import time
import pymongo
from bson import ObjectId
from apply import easy_app
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

# init db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jobDB"]
job_coll = mydb["jobs"]


def get_jobs(job_dict, jobType, joblist, jobRole, driver, db_links):
  # this counter is to avoid duplicate keys because of same companies posting different positions
  company_counter = 0
  for job in joblist[:3]:
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

        # removing the GUID so that the links can be checked again to see if applied
        guid_removed = apply_link.split("&guid=")
        src_removed = guid_removed[1].split("&src")[1]
        # apply link with unique guid removed
        apply_link = guid_removed[0] + "&src" + src_removed

        # removing the 'cs=' part from the link
        cs_removed = apply_link.split("&cs=")
        # getting the first part of the link constant
        first_part_link = cs_removed[0].split("?")[0]
        # removing the 'pos=' part from the link
        pos_removed = "?&ao" + cs_removed[0].split("?")[1].split("&ao")[1]
        # removing the 'cb=' part from the link
        cb_removed = guid_removed[1].split("&cb")[1].split("&")
        # actual apply link
        apply_link = first_part_link + pos_removed + "&" + cb_removed[1]

      if apply_link in db_links:
        print("JOB HAS BEEN ALREADY APPLIED")
      else:
        # if the key already exists, this happens when the same company posts a different position
        if company_name in job_dict.keys():
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

      if easy_apply_link in db_links:
        print("JOB HAS BEEN ALREADY APPLIED")
      else:
        if company_name in job_dict.keys():
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

      print(pages)

      if len(pages) > 0:
        page_counter = 0
        while page_counter <= len(pages):
          # job list 
          job_on_page = driver.find_elements_by_class_name("jl")
          if not job_dict[job_role]:
            job_dict = { job_role: { job_type: {} } }
            job_dict = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])

            job_dict[job_role]["'internship'"] = {}
          elif not job_dict[job_role][job_type]:
            jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])
          else:
            jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])

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
          job_dict = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])
          # after I get the job dict back I insert the internship key
          job_dict[job_role]["'internship'"] = {}
        elif not job_dict[job_role][job_type]:
          jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])
        else:
          jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, [])  

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
        driver.find_element_by_xpath("//li[@value="+job_type+"]").click()
        time.sleep(2)
        job_on_page = driver.find_elements_by_class_name("jl")

        job_dict = { job_role: { job_type: {} } }

        job_links = [job[job_role][job_type][key]['job link'] for key in job[job_role][job_type].keys()]
        
        jobs = get_jobs(job_dict, job_type, job_on_page, job_role, driver, job_links)
        print(job_links, "\n\n")
        print(jobs)

        # TODO: update db with jobs that has not been applied to

    driver.close()