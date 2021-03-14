import json
# -- Flask libraries --     #
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
# -- Firebase libraries --  #
import firebase_admin
from firebase_admin import credentials, firestore
# -- Internal libraries --  #
from tools.authtool import make_auth, check_hash
from tools.errtool import catchnoauth


# TODO: Remove needless print statements at the end!

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
Creates a new user document.
"""
@app.route('/create', methods=['POST'])
@cross_origin()
def create_endpoint() -> dict:
    
    return catchnoauth(_create, request.json)

"""
Adds a dog to a user's document.
"""
@app.route('/registerdog', methods=['POST'])
@cross_origin()
def register_dog() -> dict:
    
    return quietcatch(_register_dog, request)

"""
Endpoint to handle login requests.
"""
@app.route('/login', methods=['POST'])
@cross_origin()
def login() -> dict:
    
    return quietcatch(_login, request)


#   --    Private methods     -- #
"""
Use this in endpoints for authentication (better security) before running the
endpoints' functions. Note that the endpoint function should have an underscore
"_" in front of its name.

Returns True if the user authenticates, and the given function succeeds. If 
anything goes wrong, return False. 
"""
def quietcatch(function, request) -> dict:
    
    # Jsonify the request.
    req_obj = request.json
    
    # If the function runs, return success.
    try:
        stat = function(req_obj) if _authenticate(req_obj) else False 
    
    # Return false for any exception.
    except Exception as e:
        print(str(e))
        stat = False
    
    # Package the success status in JSON syntax.
    return { "success" : stat }

"""
Actual method body to handle the logins.
"""
def _login(req_obj) -> bool:
    print("Login successful")
    return True    

"""
Only create the user if they don't exist.
"""
def _create(req_obj) -> bool:
    
    return False if _user_exists(req_obj['username']) else _add_user(req_obj)

"""
Check whether or not a user exists in the database.
"""
def _user_exists(username:str) -> bool:
    
    single = [r for r in root_collection.where(
        "username", "==", username).stream()]

    print("Username is taken" if len(single) > 0 else "Creating user.")    
    
    return True if len(single) > 0 else False

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
def _register_dog(req_obj) -> bool:  
          
    # Updating above document's contact array.
    user = [r for r in root_collection.where(
        'username', '==', req_obj['username']).stream()]
    
    print("update_dog: type={}, data=<{}>".format(type(user), user))
    
    return _add_dog(user, req_obj) if len(user) == 1 else False

"""
Insert a dog to the user's document. Note that the user parameter is
a one-sized list. (Prevents an IndexError in the prev. function)
"""
def _add_dog(user, req_obj) -> bool:
    
    root_collection.document(user[0].id).update({
            
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
    single = [r for r in root_collection.where(
        "username", "==", username).stream()]
        
    num_docs = len(single)
    
    print("single: type={}, len={}".format(single, num_docs))

    # Throw an error message if more than one doc is detected.
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
    
    print("Hash from user: {}\nHash from db: {}".format(stored, req_hash))
        
    return True if req_hash == fb_hash else False