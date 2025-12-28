from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
import models
from sqlalchemy import func
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from schemas.noteModel import NoteCreate, NoteResponse, NoteUpdateRequest
from schemas.userModel import UserCreate, UserUpdate, UserResponse, UserDB
import middleware
import encrypter
from jwt_utils import SECRET_KEY, ALGORITHM, create_access_token, oauth2scheme, get_current_user
import jwt
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def getDB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(getDB)]

@app.post("/addNote", response_model = NoteResponse)
async def add_Note(note: NoteCreate, db: db_dependency, userId: int = Depends(get_current_user)):

    new_note = models.Note(
        content = note.content,
        tags = note.tags,
        user_id = userId
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get("/getAllNotes", response_model=List[NoteResponse])
async def get_Notes(db: db_dependency, userId: int = Depends(get_current_user)):
    allNotes = db.query(models.Note).all()
    return allNotes

@app.get("/getNote", response_model=NoteResponse, dependencies= [Depends(get_current_user)])
async def get_Note(db: db_dependency, targetId: int, userId: int = Depends(get_current_user)):
    targetNote = db.query(models.Note).filter(models.Note.id == targetId).first()

    if targetNote is None:
        raise HTTPException(status_code=404, detail= "Note not Found")
    
    return targetNote

@app.delete("/deleteAll")
async def delete_all(db:db_dependency, userId: int = Depends(get_current_user)):
    deleted = db.query(models.Note).delete()
    db.commit()

    if deleted == 0:
        return {"message": "No Notes found for deletion"}

    return {"message": "All Notes Deleted Successfully!"}

@app.delete("/delete")
async def delete(db: db_dependency, targetId: int, userId: int = Depends(get_current_user)):
    count = db.query(models.Note).count()

    if count == 0:
        return {
            "message" : "No Record Found"
        }

    db.query(models.Note).filter(models.Note.id == targetId).delete()
    db.commit()

    return {
        "message": "Record Deleted Successfully!"
    }

@app.patch("/update")
async def update_record(db: db_dependency, targetId: int, note: NoteUpdateRequest, userId: int = Depends(get_current_user)):
    targetNote = db.query(models.Note).filter(models.Note.id == targetId).first()

    if targetNote is None:
        raise HTTPException(status_code=404, detail="No Note Found for Update")

    
    update_data = note.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(targetNote, field, value)
    
    db.commit()
    db.refresh(targetNote)
    
    return targetNote


@app.post("/createUser", response_model=UserResponse, dependencies=[Depends(middleware.validateUserCreation)])
async def create_user(db: db_dependency, userDetails: UserCreate):

    newUser = models.User(
        username = userDetails.username,
        password = encrypter.hash_password(userDetails.password)
    )

    print(userDetails.password)
    
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return newUser

@app.get("/getUsers", response_model= List[UserResponse])
async def get_Users(db: db_dependency):
    allUsers = db.query(models.User).all()
    
    return allUsers

@app.get("/getDBUsers", response_model=List[UserDB])
async def get_Users_db(db: db_dependency):
    allUsers = db.query(models.User).all()

    return allUsers

@app.patch("/updateUser", response_model=UserResponse, dependencies=[Depends(middleware.validateUserUpdate)])
async def update_Users(db: db_dependency, updateDetails : UserUpdate, userId: str = Depends(get_current_user)):
    targetRecord = db.query(models.User).filter(models.User.user_id == userId).first()

    if targetRecord is None:
        raise HTTPException(status_code=404, detail="No record found using the targert Id")
    

    if updateDetails.username is not None:
        targetRecord.username = updateDetails.username

    if updateDetails.password is not None:
        targetRecord.password = encrypter.hash_password(updateDetails.password)

    db.commit()
    db.refresh(targetRecord)

    return targetRecord


@app.post("/login")
async def login(db: db_dependency, formdata: OAuth2PasswordRequestForm = Depends()):
    db_user = db.query(models.User).filter(models.User.username == formdata.username).first()

    if not db_user or not encrypter.verify_password(formdata.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(
        data= {
            "sub": db_user.user_id
        },
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/searchNotes")
def search_notes(q: str, db: db_dependency, user_id: str = Depends(get_current_user)):
    query = func.plainto_tsquery("english", q)

    notes = (
        db.query(models.Note).filter(models.Note.user_id == user_id, models.Note.search_vector.op("@@")(query)).order_by(func.ts_rank(models.Note.search_vector, query).desc()).all()
    )

    return notes