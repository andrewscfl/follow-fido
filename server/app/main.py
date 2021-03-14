import os
# -- Flask libraries --     #
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
# -- Firebase libraries --  #
import firebase_admin
from firebase_admin import credentials, firestore
# -- Internal libraries --  #
from tools.authtool import make_auth, check_hash
from tools.errtool import catchnoauth


# Firebase variables (global). Look in current directory.
cred = credentials.Certificate(
    os.path.join(os.getcwd(), "sdkkey.json"))

firebase_admin.initialize_app(cred)
db = firestore.client()

# Flask variables (global).
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#you can use this in place of db.collection('pets') since everything is in pets
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
    
    #return quietcatch(_login, request)
    snap = _snapshot(request.json)
    print(snap)
    return snap

"""
Endpoint to add a schedule to a dog.
"""
@app.route('/scheduledog', methods=['POST'])
@cross_origin()
def schedule_dog() -> dict:
    
    return quietcatch(_schedule_dog, request)


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
    
    print("Dog <{}> added.".format(req_obj['dogName']))
    return True

"""
Add a dog's event to firebase.
"""
def _schedule_dog(req_obj) -> bool:  
          
    # Updating above document's contact array.
    user = [r for r in root_collection.where(
        'username', '==', req_obj['username']).stream()]
    
    print("update_dog: type={}, data=<{}>".format(type(user), user))
    
    return _add_to_schedule(user, req_obj) if len(user) == 1 else False

"""
Insert an event to the user's document. Note that the user parameter is
a one-sized list. (Prevents an IndexError in the prev. function)
"""
def _add_to_schedule(user, req_obj) -> bool:
    
    dogs = user[0].to_dict()['dogs']
    
    key = -1
    i = 0
    while (key < 0):
        key = i if dogs[i]['dogName'] == req_obj['dogName'] else -1
        i += 1
    
    print(req_obj['newEvent'])
    dogs[key]['dogSchedule'].append(req_obj['newEvent'])
    print(dogs[key]['dogSchedule'])
    
    root_collection.document(user[0].id).update({
            
        "dogs"  : firestore.ArrayUnion([{
            "dogName"       : req_obj['dogName'],
            "dogAge"        : req_obj['dogAge'],
            "dogBio"        : req_obj['dogBio'],
            "dogSchedule"   : req_obj['dogSchedule']
         }])
    })
    
    print("Dog <{}> added.".format(req_obj['dogName']))
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
Note: Leave "single" unlabeled.
"""
def _compare_hash(single, username, passwd) -> bool:
    
    stored = single[0].to_dict()
        
    fb_salt = stored['salt']
    fb_hash = stored['hash']
        
    req_hash = check_hash(username, passwd, fb_salt)
    
    print("Hash from user: {}\nHash from db: {}".format(stored, req_hash))
        
    return True if req_hash == fb_hash else False


# More endpoints




#actual method
def _snapshot(req_obj):
    print('got request')
    print(req_obj)
    username = req_obj['username']

    # Grabs list of docs where matching username is true
    docs = db.collection(u'pets').where(u'username', '==', username).stream()
    for doc in docs:
        new_dict = doc.to_dict()['dogs']

        # Return new_dict (list of dogs) if authenticated
        if _authenticate(req_obj):
            return {
                "success": True,
                "data" : new_dict
            }
            
        else:
            return { "success" : False }

@app.route('/snapshot', methods=['POST'])
@cross_origin()
def snapshot():
    return _snapshot(request.json)


#delete dog method 
def _delete_dog(req_obj):
    print('got request')
    print(req_obj)
    username = req_obj['username']
    dogname = req_obj['dogName']

    #check if username matches
    docs = db.collection(u'pets').where(u'username', '==', username).stream()
    for doc in docs:
        obj_ref = doc.to_dict()
        print('for loop here')
        #loop thru array of 'dogs'
        for i in range(len(obj_ref['dogs'])):
            print('running 2nd for loop')
            #if dog name matches, delet the doge from array
            if dogname == obj_ref['dogs'][i]['dogName']:
                print('found')
                obj_ref['dogs'].pop(i)
                print("doge is delet")
                # print(doc.id)
                temp = db.collection(u'pets').document(doc.id)
                temp.update({'dogs' : obj_ref['dogs']})
                print('updated')
                return True


#extra thing for quietcatch
@app.route('/deletedog', methods=['POST'])
@cross_origin()
def delete_dog():
    return quietcatch(_delete_dog, request)

#THIS IS UNFINISHED, UPDATE TOMORROW
#delete SCHEDULE method 
def _delete_schedule(req_obj):
    print('got request')
    print(req_obj)
    username = req_obj['username']
    dogname = req_obj['dogName']
    eventname = req_obj['eventName']

    #check if username matches
    docs = db.collection(u'pets').where(u'username', '==', username).stream()
    for doc in docs:
        obj_ref = doc.to_dict()
        print('for loop here')
        #loop thru array of 'dogs'
        for i in range(len(obj_ref['dogSchedule'])):
            print('running 2nd for loop')
            #if EVENT name matches, delet the thing from array
            if eventname == obj_ref['dogSchedule'][i]['eventName']:
                print('found')
                obj_ref['dogSchedule'].pop(i)
                print("EVENT is delet")
                # print(doc.id)
                temp = db.collection(u'pets').document(doc.id)
                temp.update({'dogSchedule' : obj_ref['dogSchedule']})
                print('updated')
                return True


#extra thing for quietcatch
@app.route('/deleteschedule', methods=['POST'])
@cross_origin()
def delete_schedule():
    return quietcatch(_delete_schedule, request)