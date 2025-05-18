from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db_connection import Base, engine, SessionLocal
import model, schema, auth
from fastapi import Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

model.Base.metadata.create_all(bind=engine)
app = FastAPI()

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the Task API!",
    "author": "Nitesh Upadhyay",
    "email": "upadhyay02nitesh@gmail.com",
    "advice":"https://fastapi-with-streamlit-r66r.onrender.com/docs  for test api",
    "secret_api":"tracker626453"}

@app.post("/register", response_model=schema.UserOut,dependencies=[Depends(verify_api_key)])
def register(user: schema.UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.hash_password(user.password)
    db_user = model.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login",dependencies=[Depends(verify_api_key)])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/tasks/", response_model=schema.TaskOut,dependencies=[Depends(verify_api_key)])
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])["sub"]
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    db_task = model.Task(**task.dict(), owner_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[schema.TaskOut],dependencies=[Depends(verify_api_key)])
def get_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])["sub"]
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    tasks = db.query(model.Task).filter(model.Task.owner_id == user.id).offset(skip).limit(limit).all()
    return tasks