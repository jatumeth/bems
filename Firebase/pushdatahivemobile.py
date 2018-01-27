import pyrebase
import os
import ast
import random
import time
# see https://github.com/thisbejim/Pyrebase for reference

config = {
  "apiKey": "AIzaSyD4QZ7ko7uXpNK-VBF3Qthhm3Ypzi_bxgQ",
  "authDomain": "hive-rt-mobile-backend.firebaseapp.com",
  "databaseURL": "https://hive-rt-mobile-backend.firebaseio.com",
  "storageBucket": "bucket.appspot.com",
  "serviceAccount": os.getcwd()+"/hive-rt-mobile-backend-firebase-adminsdk-zk9mz-12e98d22ca.json"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Save Data

'''
set
To create your own keys use the set() method. The key in the example below is "Morty".
'''
for i in range(100):
    data = random.randint(1, 100)
    db.child("react").child("speed").set(data)
    time.sleep(1)
