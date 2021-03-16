import os
import firebase_admin as _FB_ADMIN
from firebase_admin import credentials, firestore
from tools.authtool import make_auth, check_hash


# Firebase variables (global). Look in current directory.
_CRED = credentials.Certificate(
    os.path.join(os.getcwd(), "sdkkey.json"))

_FB_ADMIN.initialize_app(_CRED)

_DB = firestore.client()

# Collections for user and schedules
_ROOT_COLLECTION = _DB.collection('pets')
_ROOT_SCHEDULE   = _DB.collection('schedule')

def quietcatch(route:str, request) -> dict:
    """
    Use this in endpoints for authentication (better security) before running the
    endpoints' functions. Note that the endpoint function should have an underscore
    "_" in front of its name.

    Returns True if the user authenticates, and the given function succeeds. If 
    anything goes wrong, return False. 
    """    
    
    routes = {
        "create"        : _create,
        "registerdog"   : _register_dog,
        "scheduledog"   : _schedule_dog,
        "deletedog"     : _delete_dog,
        "deleteschedule": _delete_schedule
    }
    
    # Jsonify the request.
    req_obj = request.json
    
    # If the function runs, return success.
    try:
        stat = routes[route](req_obj) if _authenticate(req_obj) else False 
    
    # Return false for any exception.
    except Exception as e:
        print(str(e))
        stat = False
    
    # Package the success status in JSON syntax.
    return { "success" : stat }

def snapshot(req_obj):
    """
    Get the state of the database, JSON-like.
    """
    username = req_obj['username']

    # Grabs list of docs where matching username is true. Note that there
    # should only be one username.
    docs = _ROOT_COLLECTION.where('username', '==', username).stream()
    
    print("")
    
    new_dict = doc[0].to_dict()['dogs']
        
    _sched_snapshot(req_obj)

    # Return new_dict (list of dogs) if authenticated.
    if _authenticate(req_obj):
        return {
            "success"   : True,
            "data"      : new_dict,
            "schedules" : _sched_snapshot(req_obj)
        }
            
    else:
        return { "success" : False }

"""
Only create the user if they don't exist.
"""
def _create(req_obj) -> bool:
    
    return False if _user_exists(req_obj['username']) else _add_user(req_obj)

"""
Check whether or not a user exists in the database.
"""
def _user_exists(username:str) -> bool:
    
    single = [r for r in _ROOT_COLLECTION.where(
        "username", "==", username).stream()]

    print("Username is taken" if len(single) > 0 else "Creating user.")    
    
    return True if len(single) > 0 else False

"""
Attempt to add the user's data to firebase.
"""
def _add_user(req_obj) -> bool:  
          
    new_record = _ROOT_COLLECTION.document()
    
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
    user = [r for r in _ROOT_COLLECTION.where(
        'username', '==', req_obj['username']).stream()]
    
    print("update_dog: type={}, data=<{}>".format(type(user), user))
    
    return _add_dog(user, req_obj) if len(user) == 1 else False

"""
Insert a dog to the user's document. Note that the user parameter is
a one-sized list. (Prevents an IndexError in the prev. function)
"""
def _add_dog(user, req_obj) -> bool:
    
    _ROOT_COLLECTION.document(user[0].id).update({
            
        "dogs"  : firestore.ArrayUnion([{
            "dogName"       : req_obj['dogName'],
            "dogAge"        : req_obj['dogAge'],
            "dogBio"        : req_obj['dogBio'],
            #"dogSchedule"   : []
         }])
    })
                
    print("Dog <{}> added.".format(req_obj['dogName']))
    return _create_dog_sched(req_obj)


def _create_dog_sched(req_obj) -> bool:
    
    new_record = _ROOT_SCHEDULE.document()
        
    new_record.set({
        'ownerName'   : req_obj['username'],
        'dogName'     : req_obj['dogName'],
        'dogSchedule' : []
    })
    
    return True

"""
Add a dog's event to firebase.
"""
def _schedule_dog(req_obj) -> bool:  
        
    # Updating above document's contact array.
    sched = [r for r in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).where(
            'dogName', '==', req_obj['dogName']).stream()]

    print("update_dog: type={}, data=<{}>".format(type(sched), sched))
    
    print(len(sched))
    return _add_to_schedule(sched, req_obj) if len(sched) == 1 else False

"""
Insert an event to the user's document. Note that the user parameter is
a one-sized list. (Prevents an IndexError in the prev. function)
"""
def _add_to_schedule(sched, req_obj) -> bool:
   
    print(req_obj['eventDesc']) 
    print(sched[0].id)
    _ROOT_SCHEDULE.document(sched[0].id).update({
            
        "dogSchedule"  : firestore.ArrayUnion([{
            "day"       : req_obj['day'],
            "hour"      : req_obj['hour'],
            "eventName" : req_obj['eventName'],
            "eventDesc" : req_obj['eventDesc']
         }])
    })
      
    print("Event <{}> added.".format(req_obj['eventName']))
    return True

def _delete_schedule(req_obj) -> bool:  
        
    # Updating above document's contact array.
    sched = [r for r in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).where(
            'dogName', '==', req_obj['dogName']).stream()]

    print("update_dog: type={}, data=<{}>".format(type(sched), sched))
    
    print(len(sched))
    return _delete_sched_doc(sched, req_obj) if len(sched) == 1 else False

def _delete_sched_doc(sched, req_obj) -> bool:
    
    sd = sched[0].get('dogSchedule')
    new_sched = []
    
    for e in sd:
        if e['eventName'] != req_obj['eventName']:
            new_sched.append(e)
            
    _ROOT_SCHEDULE.document(sched[0].id).update({
        "dogSchedule"   :   new_sched
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
    single = [r for r in _ROOT_COLLECTION.where(
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


def _sched_snapshot(req_obj):
        
    schedules = [s for s in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).stream()]
    
    return [s.to_dict() for s in schedules]

#delete dog method 
def _delete_dog(req_obj):
    print('got request')
    print(req_obj)
    username = req_obj['username']
    dogname = req_obj['dogName']

    #check if username matches
    docs = _ROOT_COLLECTION.where(u'username', '==', username).stream()
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
