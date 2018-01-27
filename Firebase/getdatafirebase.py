import pyrebase
import os
import ast
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
val
Queries return a PyreResponse object. Calling val() on these objects returns the query data.
'''
# users = db.child("hivec83a35cdbeab").child("daily_energy").child("gridimportenergy").get()
# print(users.val()) # {"Morty": {"name": "Mortimer 'Morty' Smith"}, "Rick": {"name": "Rick Sanchez"}}

'''
key
Calling key() returns the key for the query data.
'''
# user = db.child("hivec83a35cdbeab").child("daily_energy").get()
# print(user.key()) # users

'''
each
Returns a list of objects on each of which you can call val() and key().
'''
daily_energy = db.child("hivec83a35cdbeab").child("daily_energy").get()
for item in daily_energy.each():
    print(item.key()) # Morty
    print(item.val()) # {name": "Mortimer 'Morty' Smith"}

'''
get
To return data from a path simply call the get() method.
'''
# all_users = db.child("users").get()
# print(all_users)

'''
shallow
To return just the keys at a particular path use the shallow() method.
'''
# all_user_ids = db.child("users").shallow().get()
# print(all_user_ids)

'''
streaming
You can listen to live changes to your data with the stream() method.
'''

# def stream_handler(message):
#     print(message["event"]) # put
#     print(message["path"]) # /-K7yGTTEp7O549EzTYtI
#     print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
#
# my_stream = db.child("posts").stream(stream_handler)


# test = db.child("react")
# print(test.child("speed").get().val())
#
# print(test.get().key())
# test = db.child("test2").get().val()
# test = ast.literal_eval(test)
# print(test)
# print(type(test))