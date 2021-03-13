import bcrypt

"""
Generates a new salt, hash tuple.
"""
def make_auth(username:str, passwd:str) -> tuple:

    # Concatenate the username and password.
    userpass = bytes(username + passwd)

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(userpass, salt)
    
    return salt, hashed

"""
username and passwd should come from the frontend request.
salt should come from the document field ("salt").
"""
def check_hash(username:str, passwd:str, salt:str) -> str:
    
    userpass = bytes(username + passwd)
    return bcrypt.hashpw(userpass, salt)
