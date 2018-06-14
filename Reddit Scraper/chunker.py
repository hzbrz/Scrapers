import os, datetime, math, shutil, sys


# for Reddit scraper 
# now = datetime.datetime.now()
# root_dir = now.strftime("%m_%d_%Y")


def chunker_mech(chunk_by, path_to_root):
  now = datetime.datetime.now()
  root = now.strftime("%m_%d_%Y")

  num_of_files = len(os.listdir(root))

  num_folders_to_make = math.ceil(num_of_files / chunk_by)

  # creates all the empty folkders to hold the image chunks
  for i in range(num_folders_to_make):
    folder_name = root + "_" + str(i+1)
    try:
      os.makedirs(folder_name)   
    except FileExistsError:
      print("Folder already made and exists")  
  print("\nFolders have been made")   


  counter = 0
  # looping over the amoung of folders
  for i in range(num_folders_to_make):
    print("Chunking to ", root + "_" + str(i)) 
    # each time I loop over a folder I copy the files  
    for f in range(counter, counter+chunk_by):
      try:
        # copies file to destination and overwrites if the file already exists in destination
        shutil.copy(root + '\\' + str(f) + ".png", root + "_" + str(i+1))
      except FileNotFoundError:
        print("\n\nChuncking finished")
        break
    counter = counter + chunk_by  


