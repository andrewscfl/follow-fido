import json
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import firebase_admin
from firebase_admin import credentials, firestore
from authtool import make_auth, check_hash

# Firebase variables (global).
cred = credentials.Certificate(".\sdkkey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Flask variables (global).
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#you can use this in place of db.collection('pets') since everything is in pets
root_collection = db.collection(u'pets')

#TODO comment here
@app.route('/createsnapshot', methods=['POST'])
@cross_origin()
def auth_snapshot():
    print('got request')
    req_obj = request.json
    print(req_obj)

    username = req_obj['username']
    password = req_obj['password']
    salt = db.collection(u'pets').get()['hash']

    docs = db.collection(u'pets').where(u'username', '==', username).stream()
    for doc in docs:
        toDict = doc.to_dict()
        make_auth(username, password, salt)
        if username == toDict['username'] and password == toDict['password']:
            return{
                "success" : True
                "data" : #array of dogs
            }

def delete_dog()
    print('got request')
    req_obj = request.json
    print(req_obj)

    dog_name = req_obj['dog_Name']

#for excersise, meds, feeding, walks...
# def schedule_dog():
#     print('got request')
#     req_obj = request.json
#     print(req_obj)

# # #if houry
# #     #make new
# #     new_schedule = root_collection.document()
# #     new_schedule.set({
# #         'dogName' : req_obj['eventName'],
# #         'dogAge' : req_obj['eventDesc'],
# #         'dogBio' : req_obj['dogBio'],
# #         "dogSchedule":[]
# #     })

# #     return{
# #         try:
# #             "success" : True
# #         except:
# #             "success" : False
# #     }



