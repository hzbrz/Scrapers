import requests, pickle, os

name_dir = input("name your folder ")  

file_name = input("name the file to copy links from ")

# handling the "cannot make directory when it exists" error
dir = ''
try:
  dir = r'C:\Users\bhalocomputer\Desktop\coirses\Images\%s' %(name_dir)
  os.makedirs(dir)
except WindowsError:
  dir = r'C:\Users\bhalocomputer\Desktop\coirses\Images\%s' %(name_dir)


num_of_files = len(os.listdir(dir)) 

# read from the pickle file
link_file = open(file_name + '.pkl', 'rb')
links = pickle.load(link_file)
link_file.close()


for i in range(len(links)):
  res = requests.get(links[i])

  f = open(dir + '\\' + str(num_of_files+i) + ".jpg", 'wb')
  for chunk in res.iter_content(100000):
    f.write(chunk)
    
  f.close()


print('removed', file_name + '.pkl')
os.remove(file_name + '.pkl')