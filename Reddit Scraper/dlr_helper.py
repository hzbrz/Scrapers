from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import threading, requests, time, pickle, datetime, os


# generating links from ids
def generate_link(url):
  return "https://i.imgur.com/"+url+".jpg"


# downloading the links and storing it to folder
def download_albums(filename):
    now = datetime.datetime.now()
    folder_name = now.strftime('%m_%d_%Y')

    # handling the "cannot make directory when it exists" error
    dir = ''
    try:
        dir = r'C:\Users\wazih\Desktop\courses\Images\%s' %(folder_name)
        os.makedirs(dir)
    except WindowsError:
        dir = r'C:\Users\wazih\Desktop\courses\Images\%s' %(folder_name)

    num_of_files = len(os.listdir(dir)) 

    # read from the pickle file
    link_file = open(filename, 'rb')
    links = pickle.load(link_file)
    link_file.close()

    for i in range(len(links)):
        res = requests.get(links[i])

        f = open(dir + '\\' + str(num_of_files+i) + ".jpg", 'wb')
        for chunk in res.iter_content(100000):
            f.write(chunk)
            
        f.close()


    print('removed', filename)
    os.remove(filename)



def get_links(url, filename):
    # reading/opening the pickle file so that I can add to the file properly
    read_file = open(filename, 'rb')
    file_content = pickle.load(read_file)
    read_file.close()

    for link in url:
        if generate_link(link.get_attribute('id')) in file_content:
            print("link already in array", generate_link(link.get_attribute('id')))
        else: 
            file_content = file_content + [generate_link(link.get_attribute('id'))]
            print("LINK ADDED", generate_link(link.get_attribute('id')))

        # writing the links to the pickle file
        write_file = open(filename, 'wb') 
        pickle.dump(file_content, write_file)
        write_file.close()
        
def scrape_album_links(album_url, filename):
    
    for i in range(len(album_url)):
        new_file_name = filename + '_' + str(i) + '.pkl'

        # Initializing link holder file wiht an empty array
        create_file = open(new_file_name, 'wb')
        pickle.dump([], create_file)
        create_file.close()

        browser = webdriver.Firefox()
        browser.get(album_url[i])  

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

        # setting initial heihgt
        height = 0
        print("end height:", end_page_height)

        # more storage vars
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
        

            get_links(url, new_file_name)

            # incrementing height
            height = height + 1000

            # breaking out of the loop after scroll reaches the end of the page
            if height >= end_page_height:
                break  

        browser.close()       
        print("\n links stored in", new_file_name)

        download_albums(new_file_name)


def download_pics(pic_urls):

    now = datetime.datetime.now()
    # folder name created as: month_day_year
    folder_name = now.strftime('%m_%d_%Y')

    # handling the "cannot make directory when it exists" error
    dir = ''
    try:
        dir = r'C:\Users\wazih\Desktop\courses\Images\%s' %(folder_name)
        os.makedirs(dir)
    except WindowsError:
        dir = r'C:\Users\wazih\Desktop\courses\Images\%s' %(folder_name)

    num_of_files = len(os.listdir(dir)) 

    for i in range(len(pic_urls)):
        res = requests.get(pic_urls[i])

        f = open(dir + '\\' + str(num_of_files+i) + ".jpg", 'wb')
        for chunk in res.iter_content(100000):
            f.write(chunk)
        
        f.close()
    
    print('finished downloading the pictures')



