import pyrebase, firebase_config, os, datetime, random, shutil

config = {
  "apiKey": firebase_config.api_key,
  "authDomain": firebase_config.auth_domain, 
  "databaseURL": firebase_config.database_URL,
  "storageBucket": firebase_config.storage_bucket, 
}

firebase = pyrebase.initialize_app(config)

# generates a key for firebase
letters_for_key = '!abcdefghijklmanopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
def key_gen(key_length):
  str = ""
  counter = 0
  
  while counter < key_length:
    rand = random.randint(1, len(letters_for_key)-1)  
    str = str + letters_for_key[rand]

    counter = counter + 1

  return str  
  

def upload_to_storage_db():   
  dir = "C:\\Users\\wazih\\Desktop\\courses\\Images"
  folders = os.listdir(dir)

  # authentication for writing purposes
  auth = firebase.auth()
  # auth.create_user_with_email_and_password(firebase_config.email, firebase_config.password)
  user = auth.sign_in_with_email_and_password(firebase_config.email, firebase_config.password)

  # regfreshing token because of 1hr expiry limit
  user = auth.refresh(user['refreshToken'])

  # init firebase vars
  db = firebase.database()
  storage = firebase.storage()



  # prepping for image counting and getting the length of db for db count
  len_db = 0
  next_folder_count = 0

  for folder in folders:
    try:
        images_from_db = db.child(folder).get()
        len_db = len(images_from_db.val())
    except TypeError:
        len_db = 0

    for i in range(len(os.listdir(dir + "\\" + folder))):
        # storing to firebase 
        key = key_gen(5)
        # they key is the download link and it will be unqiue so there is no download link overlap on phone
        try:
          upload_image = storage.child(folder + '/' + key + '.jpg').put(dir + '\\' + folder + '\\' + str(i+next_folder_count) + '.jpg', user['idToken'])
        except FileNotFoundError:
          upload_image = storage.child(folder + '/' + key + '.jpg').put(dir + '\\' + folder + '\\' + str(i) + '.jpg', user['idToken'])
        
        # printing a tracking message
        print('File uploaded', i+1, '/', len(os.listdir(dir + "\\" + folder)))

        # getting the download url and passing a token to the get_url() function from the upload
        data_url = storage.child(folder + '/' + key + '.jpg').get_url(upload_image['downloadTokens'])
        # print(data_url)

        # # prepping the data to upload to the database with the download link from storage
        data = {str(len_db+i) : data_url}

        db.child(folder).update(data, user['idToken'])

    next_folder_count = next_folder_count + 100

    # deleting folder after upload, so that it does not reupload next time bot runs
    # shutil.rmtree(dir + '\\' + folder)

  print("Finished uploading to firebase")    