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

# Documents in collection hold all data.
root_collection = db.collection('pets')

"""
Creates a new document.
"""
@app.route('/create',methods=['POST'])
@cross_origin()
def add_document():
        
    req_obj = request.json
    new_record = root_collection.document()
    
    salt, hash = make_auth(req_obj['username'], req_obj['password'])
    
    new_record.set({
        'username'  : req_obj['username'],
        'salt'      : salt,
        'hash'      : hash,
        'dogs'      : []
    })
    
    # End code to store in firebase
    return {
        "success": True
    }