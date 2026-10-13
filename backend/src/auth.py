from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta 
import os

SECRET_KEY=os.environ["JWT_SECRET_KEY"]
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_crypt=CryptContext(
    schemes=['bcrypt'],
    deprecated="auto"
)

def encrypt_password(password:str)-> str:
    return pwd_crypt.hash(password)

def decrypt_password(password: str, hash_pwd: str)-> bool:
    return pwd_crypt.verify(password, hash_pwd)

def create_access_token(user_id:int, username: str):
    exp=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload={
            "username": username,
            "user_id": user_id,
            "expire": int(exp.timestamp())
        }
    
    return jwt.encode (
        payload,
        SECRET_KEY,
        ALGORITHM
    )
# if __name__=="__main__":
#     pwd="pass@123"
#     hash_pwd=encrypt_password(pwd)
#     print("hash: ", hash_pwd)
#     print("check pass: ", decrypt_password(pwd, hash_pwd))
#     print("check false: ", decrypt_password("abc@123", hash_pwd))