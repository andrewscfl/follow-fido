import json
import os
import firebase_admin as _FB_ADMIN
from firebase_admin import credentials, firestore
from .auth import get_hash, check_hash
from functools import wraps


# Firebase variables (global). Look in current directory.
_CRED = credentials.Certificate(
    os.path.join(os.getcwd(), "sdkkey.json"))

_FB_ADMIN.initialize_app(_CRED)

_DB = firestore.client()

# Collections for user and schedules
_ROOT_COLLECTION = _DB.collection('pets')
_ROOT_SCHEDULE   = _DB.collection('schedule')

# Methods start here.
def ep_action(route:str, request) -> dict:
    """
    Authenticates, then runs the requested "route" command. Returns a boolean
    dict structure based on the given function's return value.
    
    TODO: Break this into its own "api.py" script, with snapshot being an entry
    in the routes dict. (This will also mean cleaning up the way it returns 
    data.)
    
    TODO: Make this a wrapper. The endpoints functions will return one of the
    strings in the routes table. The wrapper will automatically fetch the
    request object.
    """    
    routes = {
        "login"         : _get_snapshot,
        "registerdog"   : _register_dog,
        "scheduledog"   : _schedule_dog,
        "snapshot"      : _get_snapshot,
        "deletedog"     : _delete_dog,
        "deleteschedule": _delete_schedule
    }
    
    # Jsonify the request.
    req_obj = request.json
    print(req_obj)

    # If the function runs, return success.
    try:
        return routes[route](req_obj) if _authenticate(req_obj) else dict(success=False)
    
    # Return false for any exception.
    except Exception as e:
        print(str(e))
        return dict(success=False)

# TODO: Convert this into a private method within storage.
def _get_snapshot(req_obj) -> dict:
    """
    Get the state of the database, JSON-like.
    """
    docs = _get_user_doc(req_obj['username'])

    # Return new_dict (list of dogs) if authenticated.
    if docs:
        return {
            "success"   : True,
            "data"      : docs.to_dict(),
            "schedules" : _sched_snapshot(req_obj)
        }
            
    else:
        return { "success" : False }

def _get_user_doc(username:str):
    """
    Get the user's document (one doc per user). This is used in nearly every
    function in this module.
    """
    return _get_user_docs(username)[0] if _get_user_docs(username) else None

def _get_user_docs(username:str) -> list:
    
    """ Only get docs where the username is true. """
    
    return [d for d in _ROOT_COLLECTION.where('username', '==', username).stream()]

# TODO: Use this above every True/False return value (to the server).
# TODO: Move this to a separate module.
# TODO: Make a wrapper to print each dict to console.
def json_bool(f) -> dict:
    """
    Returns a boolean in the JSON frontend format.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return dict(success=f(*args, **kwargs))
    return wrapper

@json_bool
def create(req_obj) -> dict:
    
    """ Only create a new user if they don't exist. """
    
    return False if _user_exists(req_obj['username']) else _add_user(req_obj)

def _user_exists(username:str) -> bool:
    """
    Check whether or not a user exists in the database.
    """    
    single = _get_user_docs(username)

    print("Username is taken" if single else "Creating user.")    
    
    return True if single else False

def _add_user(req_obj) -> bool:  
    """
    Attempt to add the user's data to firebase.
    """          
    new_record = _ROOT_COLLECTION.document()
    
    hash = get_hash(req_obj['username'], req_obj['password'])
    print("{} created.".format(req_obj['username']))
        
    new_record.set({
        'username'  : req_obj['username'],
        'hash'      : hash,
        'dogs'      : []
    })
    
    return True

@json_bool
def _register_dog(req_obj) -> bool:  
    """ 
    Add a dog to firebase. 
    """
              
    user = _get_user_doc(req_obj['username'])
    
    return _add_dog(user, req_obj) if user else False

def _add_dog(user, req_obj) -> bool:
    """ Insert a dog to the user's document. """  
      
    _ROOT_COLLECTION.document(user.id).update({
            
        "dogs"  : firestore.ArrayUnion([{
            "dogName"       : req_obj['dogName'],
            "dogAge"        : req_obj['dogAge'],
            "dogBio"        : req_obj['dogBio'],
         }])
    })
                
    print("Dog <{}> added.".format(req_obj['dogName']))
    return _create_dog_sched(req_obj)

# Todo: figure out if this should just integrate with the previous method.
def _create_dog_sched(req_obj) -> bool:
    
    new_record = _ROOT_SCHEDULE.document()
        
    new_record.set({
        'ownerName'   : req_obj['username'],
        'dogName'     : req_obj['dogName'],
        'dogSchedule' : []
    })
    
    return True

@json_bool
def _schedule_dog(req_obj) -> bool:  
    """ Add a dog's event to firebase. """
            
    # Updating above document's contact array. 
    # TODO: Move to a helper method. 
    # TODO: Rework the len() == 1 thing.
    sched = [r for r in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).where(
            'dogName', '==', req_obj['dogName']).stream()]

    print("update_dog: type={}, data=<{}>".format(type(sched), sched))
    
    print(len(sched))
    return _add_to_schedule(sched, req_obj) if len(sched) == 1 else False

def _add_to_schedule(sched, req_obj) -> bool:
    """
    Insert an event to the user's document. Note that the user parameter is
    a one-sized list. (Prevents an IndexError in the prev. function)
    """   
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

@json_bool
def _delete_schedule(req_obj) -> bool:  
        
    # Updating above document's contact array.
    sched = [r for r in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).where(
            'dogName', '==', req_obj['dogName']).stream()]

    print("update_dog: type={}, data=<{}>".format(type(sched), sched))
    
    print(len(sched))
    return _delete_sched_doc(sched, req_obj) if len(sched) == 1 else False

def _delete_sched_doc(sched, req_obj) -> bool:
    """
    Deletes an event from a dog's schedule.
    """
    sd = sched[0].get('dogSchedule')
    new_sched = []
    
    # Rebuild the event array.
    for e in sd:
        
        # Rebuild by appending all except the "deleted" event.
        if e['eventName'] != req_obj['eventName']:
            new_sched.append(e)
    
    # Update ONLY the event array in the collection.     
    _ROOT_SCHEDULE.document(sched[0].id).update({
        "dogSchedule"   :   new_sched
    })
        
    return True

# TODO: Rename this (something like "authenticate user hash.")
def _authenticate(req_json) -> bool:
    """
    Use this to authenticate every endpoint except /create.
    """
    username = req_json['username']
    passwd = req_json['password']

    single = _get_user_doc(username)
        
    return check_hash(
        username, passwd, single.to_dict()['hash']) if single else False

def _sched_snapshot(req_obj):
        
    schedules = [s for s in _ROOT_SCHEDULE.where(
        'ownerName', '==', req_obj['username']).stream()]
    
    return [s.to_dict() for s in schedules]

@json_bool
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
                temp = _ROOT_COLLECTION.document(doc.id)
                temp.update({'dogs' : obj_ref['dogs']})
                print('updated')
                return True
