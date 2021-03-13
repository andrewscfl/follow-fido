"""
If all goes well, return the boolean value from the 
function. If any exception is raised, print it to the console
and return a false.
"""
def quietcatch(function) -> dict:
    try:
        return { "success" : function() }
    
    except Exception as e:
        print(e)
        return { "success" : False }