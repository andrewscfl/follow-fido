import json
# -- Flask libraries --     #
from server.app.errtool import simple_catch
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
# -- Firebase libraries --  #
import firebase_admin
from firebase_admin import credentials, firestore
# -- Internal libraries --  #
from authtool import make_auth, check_hash
from errtool import quietcatch

# Firebase variables (global).
cred = credentials.Certificate(".\sdkkey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Flask variables (global).
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Documents in collection hold all data.
root_collection = db.collection('pets')

#   --  Endpoints   --  #
"""
Creates a new document.
"""
@app.route('/create',methods=['POST'])
@cross_origin()
def add_document() -> dict:
    
    req_obj = request.json
    return quietcatch(_add_user, req_obj)

"""
Adds a dog to a user's document.
"""
@app.route('/registerdog',methods=['POST'])
@cross_origin()
def add_document() -> dict:
    
    req_obj = request.json
    return quietcatch(_add_dog, req_obj)

#   --    Private methods     -- #
"""
Attempt to add the user's data to firebase.
"""
def _add_user(req_obj) -> bool:  
          
    new_record = root_collection.document()
    
    salt, hash = make_auth(req_obj['username'], req_obj['password'])
    
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
            
            "dogs" : firestore.ArrayUnion([{
                "dogName"       : req_obj['dogName'],
                "dogAge"        : req_obj['dogAge'],
                "dogBio"        : req_obj['dogBio'],
                "dogSchedule"   : []
            }])
        })
            
    return True
