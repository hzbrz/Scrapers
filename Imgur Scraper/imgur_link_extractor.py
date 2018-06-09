from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time, requests, pickle, sys 


print("name the file you want to store the links in:")     
file_name = input()

# initialize and create file for all other functions 
create_file = open(file_name + '.pkl', 'wb')
pickle.dump([], create_file)
create_file.close()


imgur_url = ''
if len(sys.argv) > 1:
  imgur_url = ' '.join(sys.argv[1:])

# method to get the end of an imgur link for comparison,, not used
def base_name(link):
  link_2 = link.split('/')
  ''.join(link_2)

  base = link_2[3].split('.') 
  base = base[0] 

  return base  

# generating links from ids
def generate_link(url):
  return "https://i.imgur.com/"+url+".jpg"

# downloading links  
def dl_image(url):
  # looping thorught the url list and putting the links in the .pkl file 
  for link in url:
    read_file = open(file_name + '.pkl', 'rb')
    file_content = pickle.load(read_file)
    read_file.close()

    if generate_link(link.get_attribute('id')) in file_content:
      print("link already in array", generate_link(link.get_attribute('id')))
    else: 
      file_content = file_content + [generate_link(link.get_attribute('id'))]
      print("LINK ADDED", generate_link(link.get_attribute('id')))

    write_file = open(file_name + '.pkl', 'wb') 
    pickle.dump(file_content, write_file)
    write_file.close()


browser = webdriver.Firefox()
browser.get(imgur_url)  


# max height based on button click
end_page_height = 0
try:
  button = browser.find_element_by_class_name('post-loadall')
  button.click()

  # getting the max height of the page
  end_page_height = browser.execute_script("return document.body.scrollHeight")
except NoSuchElementException:
  print('no such element')
  end_page_height = browser.execute_script("return document.body.scrollHeight")


height = 0
print("end height:", end_page_height)

# url checking - line 84
url = ''

# having to make an interctive scroll loop becuase imgur.com loads images based on screen focus
while True:
    print(height) 
    browser.execute_script("window.scrollTo(0, arguments[0]);", height)

    # pausing the scrolling 
    time.sleep(2)

    # doing this to capture both classes of the div tags in imgur
    if len(browser.find_elements_by_xpath("//div[@class='post-image-container']")) == 0:
      url = browser.find_elements_by_xpath("//div[@class='post-image-container post-image-container--spacer']")
    elif len(browser.find_elements_by_xpath("//div[@class='post-image-container']")) > 0:
      url = browser.find_elements_by_xpath("//div[@class='post-image-container']")
    else:
      url = browser.find_elements_by_xpath("//div[@class='post-image-container post-image-container--spacer']")
  
    # passing url list[] to function
    dl_image(url)

    # incrementing height
    height = height + 1000


    # breaking out of the loop after scroll reaches the end of the page
    if height >= end_page_height:
        break  

browser.close()       

print("\nDone Downloading")

