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

"""
Creates a new document.
"""
@app.route('/create',methods=['POST'])
@cross_origin()
def add_document() -> dict:
    
    req_obj = request.json
    return quietcatch(_add(req_object))

"""
Attempt to add the user's data to firebase.
"""
def _add(req_obj) -> bool:  
          
    new_record = root_collection.document()
    
    salt, hash = make_auth(req_obj['username'], req_obj['password'])
    
    return new_record.set({
        'username'  : req_obj['username'],
        'salt'      : salt,
        'hash'      : hash,
        'dogs'      : []
    })
