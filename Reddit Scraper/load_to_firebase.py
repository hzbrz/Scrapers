import pyrebase, firebase_config, os, datetime, random

config = {
  "apiKey": firebase_config.api_key,
  "authDomain": firebase_config.auth_domain,
  "databaseURL": firebase_config.database_URL,
  "storageBucket": firebase_config.storage_bucket
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

  # init firebase vars
  db = firebase.database()
  storage = firebase.storage()


  # prepping for image counting and getting the length of db for db count
  db_len = 0
  next_folder_count = 0

  for folder in folders:
    try:
        images_from_db = db.child(folder).get()
        db_len = len(images_from_db.val())
    except TypeError:
        db_len = 0

    for i in range(len(os.listdir(dir + "\\" + folder))):
        # storing to firebase
        upload_image = storage.child(folder + '/' + str(i) + '.jpg').put(dir + '\\' + folder + '\\' + str(i+next_folder_count) + '.jpg')
        # printing a tracking message
        print('File uploaded', i+1, '/', len(os.listdir(dir + "\\" + folder)))

        # getting the download url and passing a token to the get_url() function from the upload
        data_url = storage.child(folder + '/' + str(i) + '.jpg').get_url(upload_image['downloadTokens'])

        # prepping the data to upload to the database with the download link from storage
        key = key_gen(4)
        data = {key : data_url}

        db.child(folder).update(data)

    next_folder_count = next_folder_count + 100

  print("Finished uploading to firebase")    