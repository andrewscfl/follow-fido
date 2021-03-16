"""
Send the standard success dict/json, but don't perform
authentication. (Useful for user creation, for example.)
"""
def catchnoauth(function, req_obj) -> dict:
    
    # If the function runs, return success.
    try:
        return { "success" : function(req_obj) }
    
    # Return false for any exception.
    except Exception as e:
        print(e)
        return { "success" : False }