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

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/tasks/", response_model=schema.TaskOut,dependencies=[Depends(verify_api_key)])
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    username = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])["sub"]
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    db_task = model.Task(**task.dict(), owner_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
from typing import Optional

@app.get("/tasks/", response_model=list[schema.TaskOut], dependencies=[Depends(verify_api_key)])
def get_tasks(
    last_id: Optional[int] = None,  # cursor for pagination
    limit: int = 10,
    db: Session = Depends(get_db),
    token: str = Depends(auth.oauth2_scheme)
):
    username = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])["sub"]
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    query = db.query(model.Task).filter(model.Task.owner_id == user.id)

    # If last_id is provided, fetch tasks with id greater than last_id
    if last_id:
        query = query.filter(model.Task.id > last_id)

    # Order by id ascending, so you get next batch after last_id
    tasks = query.order_by(model.Task.id.asc()).limit(limit).all()

    return tasks

@app.put("/tasks/{task_id}", response_model=schema.TaskOut, dependencies=[Depends(verify_api_key)])
def update_task(
    task_id: int,
    task_update: schema.TaskUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(auth.oauth2_scheme)
):
    payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    task = db.query(model.Task).filter(model.Task.id == task_id, model.Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task

@app.post("/logout", dependencies=[Depends(verify_api_key)])
def logout(token: str = Depends(auth.oauth2_scheme)):
    return {
        "message": "✅ You have been successfully logged out.",
        "note": "🗑️ Please delete the token on the client side (e.g., browser storage or Postman).",
        "next_step": "🔐 To log in again, send a POST request to /login with username & password.",
        "login_url": "http://127.0.0.1:8000/login"
    }


from fastapi import status

@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_api_key)])
def delete_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    task = db.query(model.Task).filter(model.Task.id == task_id, model.Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {
        "message": f"🗑️ Task with ID {task_id} has been successfully deleted."
    }
