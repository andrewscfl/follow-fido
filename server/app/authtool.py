import bcrypt

"""
Generates a new salt, hash tuple.
"""
def make_auth(username:str, passwd:str) -> tuple:

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_to_bytes(username, passwd), salt)
    
    return salt, hashed

"""
username and passwd should come from the frontend request.
salt should come from the document field ("salt").
"""
def check_hash(username:str, passwd:str, salt:str) -> str:
    
    return bcrypt.hashpw(_to_bytes(username, passwd), salt)

def _to_bytes(username:str, password:str) -> bytes:
    
    return (username + password).encode('utf-8')