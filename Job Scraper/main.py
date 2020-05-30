# job roles I am looking for
roles = ["'parttime'", "'internship'"]

# selenium driver
driver = webdriver.Chrome()
driver.get("https://www.glassdoor.com/Job/ashburn-web-developer-jobs-SRCH_IL.0,7_IC1130338_KO8,21.htm")

with open("ids.txt", 'r') as infile:
  mongo_id = infile.read()
  ids = mongo_id.split("\n")
print("id", ids)