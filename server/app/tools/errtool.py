"""
If all goes well, return the boolean value from the 
function. If any exception is raised, print it to the console
and return a false. This should match the style that the
frontend requires to determine success or failure.
"""
def catchnoauth(function, req_obj) -> dict:
    
    # If the function runs, return success.
    try:
        return { "success" : function(req_obj) }
    
    # Return false for any exception.
    except Exception as e:
        print(e)
        return { "success" : False }