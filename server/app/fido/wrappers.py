from functools import wraps

def json_bool(f) -> dict:
    """
    Returns a boolean in the JSON frontend format.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return dict(success=f(*args, **kwargs))
    return wrapper

# TODO: Make a wrapper to print each dict to console.
