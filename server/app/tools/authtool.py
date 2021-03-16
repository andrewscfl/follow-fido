from passlib import pbkdf2_sha256 as sha256


def get_hash(username:str, passwd:str) -> str:
    """
    Passlib generates a random salt for every hash. So, you don't have to store
    or manage a separate "salt" field in the database.
    """
    return sha256.hash(username + passwd)

def check_hash(username:str, passwd:str, sha_hash:str) -> bool:
    """
    Compare the stored hash versus the user/pass combination given by the user.
    """
    return sha256.hash(str(username)+str(passwd), str(sha_hash))