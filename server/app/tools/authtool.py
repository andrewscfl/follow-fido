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

# Convert the concatenated user-pass to bytes-like object.
def _to_bytes(username:str, password:str) -> bytes:
    
    return (username + password).encode('utf-8')

''' Do NOT use the crypt library (more secure) on Windows. It will break.
import crypt
from hmac import compare_digest

"""
Generates a new salt, hash tuple.
"""
def make_auth(username:str, passwd:str) -> tuple:

    userpass = username + passwd
    
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    pwhash = crypt.crypt(userpass, salt)
    
    return salt, pwhash

"""
username and passwd should come from the frontend request.
salt should come from the document field ("salt").
"""
def check_hash(username:str, passwd:str, salt:str) -> str:
    
    return crypt.crypt(username + passwd, salt)

# Convert the concatenated user-pass to bytes-like object.
def _to_bytes(username:str, password:str) -> bytes:
    
    return (username + password).encode('utf-8')
'''