from .storage import get_snapshot, register_dog, schedule_dog, delete_dog, delete_schedule, authenticate, user_exists, add_user
from .wrappers import json_bool


# Methods start here.
def ep_action(route:str, request) -> dict:
    """
    Authenticates, then runs the requested "route" command.
    
    TODO: Make this a wrapper. The endpoint functions will return one of the
    strings in the routes table. The wrapper will automatically fetch the
    request object.
    
    TODO: Rename this function.
    """    
    routes = {
        "login"         : get_snapshot,  # TODO: Make a sep't login function anyway.
        "registerdog"   : register_dog,
        "scheduledog"   : schedule_dog,
        "snapshot"      : get_snapshot,
        "deletedog"     : delete_dog,
        "deleteschedule": delete_schedule
    }
    
    # Jsonify the request.
    req_obj = request.json
    print(req_obj)

    # If the function runs, return success.
    try:
        return routes[route](req_obj) if authenticate(req_obj) else dict(success=False)
    
    # Return false for any exception.
    except Exception as e:
        print(str(e))
        return dict(success=False)
    
@json_bool
def create(req_obj) -> dict:
    """ 
    Only create a new user if they don't exist. No authentication because the user
    doesn't yet exist.
    """
    
    return False if user_exists(req_obj['username']) else add_user(req_obj)