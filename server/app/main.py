import json
# -- Flask libraries --     #
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
# -- Firebase libraries --  #
import firebase_admin
from firebase_admin import credentials, firestore
# -- Internal libraries --  #
from tools.authtool import make_auth, check_hash
from tools.errtool import quietcatch


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
# @app.route('/createsnapshot', methods=['POST'])
# @cross_origin()
# def auth_snapshot():
#     print('got request')
#     req_obj = request.json
#     print(req_obj)

    

    # docs = db.collection(u'pets').where(u'username', '==', username).stream()
    # for doc in docs:

    #     _authenticate()
    #     if username == toDict['username'] and password == toDict['password']:
    #         return{
    #             "success" : True
    #             "data" : #array of dogs
    #         }

# def delete_dog()
#     print('got request')
#     req_obj = request.json
#     print(req_obj)

#     dog_name = req_obj['dog_Name']

#     _authenticate(dog_name)


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



# Documents in collection hold all data.
root_collection = db.collection('pets')


#   --  Endpoints   --  #
"""
Creates a new user document.
"""
@app.route('/create',methods=['POST'])
@cross_origin()
def create_endpoint() -> dict:
    
    req_obj = request.json
    return quietcatch(_add_user, req_obj)

"""
Adds a dog to a user's document.
"""
@app.route('/registerdog',methods=['POST'])
@cross_origin()
def register_dog() -> dict:
    
    req_obj = request.json
    return quietcatch(_add_dog, req_obj)


#   --    Private methods     -- #
"""
Attempt to add the user's data to firebase.
"""
def _add_user(req_obj) -> bool:  
          
    new_record = root_collection.document()
    
    salt, hash = make_auth(req_obj['username'], req_obj['password'])
    
    # TODO: Remove me when we test the salt and hash output.
    print("salt: {}\nhash: {}".format(salt, hash))
    
    new_record.set({
        'username'  : req_obj['username'],
        'salt'      : salt,
        'hash'      : hash,
        'dogs'      : []
    })
    
    return True

"""
Add a dog to firebase.
"""
def _add_dog(req_obj) -> bool:  
          
    # Updating above document's contact array.
    update_dog = root_collection.where(
        'username', '==', req_obj['username']).stream() # TODO: Add an AND phrase to do username and hash auth.
    
    for doc in update_dog:
        
        fb_doc_id = doc.id
        root_collection.document(fb_doc_id).update({
            
            "dogs"  : firestore.ArrayUnion([{
                "dogName"       : req_obj['dogName'],
                "dogAge"        : req_obj['dogAge'],
                "dogBio"        : req_obj['dogBio'],
                "dogSchedule"   : []
            }])
        })
            
    return True

"""
Wrapper for authentication. Input the request object. Use this to 
authenticate in each endpoint.
"""
def _authenticate(req_json) -> bool:

    username = req_json['username']
    passwd = req_json['password']
    
    # Should return either 0 or 1 documents.
    single = root_collection.where(
        "username", "==", username).stream()
    
    num_docs = len(single)
    print("WARNING: {} docs found. Address this in the database.".format(
        num_docs) if num_docs > 1 else "{} document(s) found.".format(num_docs)
    )
    
    return _compare_hash(single, username, passwd) if len(single) == 1 else False

"""
Returns True if the stored hash matches the checked hash.
Note: Do not label "single" to the data type. It's whatever
data type "single" is from _authenticate.
"""
def _compare_hash(single, username, passwd) -> bool:
    
    stored = single[0].to_dict()
        
    fb_salt = stored['salt']
    fb_hash = stored['hash']
        
    req_hash = check_hash(username, passwd, fb_salt)
        
    return True if req_hash == fb_hash else False


# More endpoints




#actual method
def _auth_snapshot(req_obj):
    print('got request')
    print(req_obj)
    username = req_json['username']

    docs = db.collection(u'pets').where(u'username', '==', username).stream()
    for doc in docs:
        new_dict = doc.to_dict()['dogs']
        #take out username and passw
        new_dict.pop(username)
        print("username gone")
        new_dict.pop(req_json['password'])
        print("password gone")

    return new_dict

@app.route('/snapshot', methods=['POST'])
@cross_origin()
def auth_snapshot():
    req_obj = request.json
    return quietcatch(_auth_snapshot, req_obj)