from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import DOCUMENTS_DIR
from database import save_data, create_user, get_user, get_query_history
from auth import encrypt_password, decrypt_password, create_access_token
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM
from combine import gen_ans
from parent_child_app import build_parent_child_index_uploaded_pdf
from fastapi.middleware.cors import CORSMiddleware

security=HTTPBearer()

app = FastAPI(
    title="smartDocs API",
    description="AI-powered document intelligence API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query:str
    document:str | None=None

class RegisterUser(BaseModel):
    username:str
    password:str
    
class GetUser(BaseModel):
    username:str
    password:str

def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security)):
    
    try:
        token=credentials.credentials
        payload=jwt.decode(
            token, 
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return {
            "username": payload.get("sub"),
            "user_id": payload.get("user_id")
        }
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

@app.get("/")
def home():
    return {
        "message":"SmartDocs API is running"
    }
    
@app.post("/query")
def query_document(request: QueryRequest, current_user: dict=Depends(get_current_user)):
    res=gen_ans(request.query, request.document)
    save_data(request.query, res["answer"], request.document, current_user["user_id"])
    return res

@app.post("/uploadFile")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return{
            "Error": "Only PDF files are supported"
        }
    
    file_path=DOCUMENTS_DIR/file.filename
    
    contents=await file.read()
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # count_chunks=ingest_pdf(file_path)
        count_child=build_parent_child_index_uploaded_pdf(file_path)
        return{
            "message": "File uploaded and indexed successfully.",
            "filename": file.filename,
            "chunks": count_child
        }
    except Exception as ex:
        
        return {
            "message": "File uploaded successfully but indexing failed",
            "filename": file.filename,
            "error": str(ex)
        }

@app.get("/documents")
def get_documents(current_user: dict=Depends(get_current_user)):
    doc=sorted(DOCUMENTS_DIR.glob("*.pdf"))
    
    return{
        "documents":[
            {
                "filename": file.name
            }
            for file in doc
        ]
        
    }
    
@app.post("/register")
def register_user(user: RegisterUser):
    try:
        encrypted_pwd=encrypt_password(user.password)
        create_user(user.username, encrypted_pwd)
        return {
            "message": "User saved successfully"
        }
    except Exception as ex:
        return{
            "message": "Error occured while registering: "+str(ex)
        }

@app.post("/login") 
def login(user: GetUser):
    try:
        user1=get_user(user.username)
        if user1 is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        verified = decrypt_password(user.password, user1["passwordHash"])
        # print("sanika---api: " + verified)
        if verified:
            token=create_access_token(user1["id"], user1["username"])
            # print("sanika--token: "+ token)
            return {
                "message": "User verified successfully",
                "token": token,
                "token_type":"bearer"
            }
            
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    except Exception as ex:
        return {
            "message": "Error in login: " + str(ex)
        }
        
@app.get("/getHistory")
def get_history(curr_user: dict=Depends(get_current_user)):
    hist=get_query_history(curr_user["user_id"])
    if not hist:
        return {
            "message": "No history available"
        }
        
    return {
        "history": hist
    }
    