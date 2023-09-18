from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session 

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class Aluno_data (BaseModel):
    name: str
    matricula: str

def get_db ():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/cadastro/{id}")
async def read_student ( student_id: int, db: db_dependency ):
    result = db.query(models.Aluno).filter(models.Aluno.id == student_id).first()
    
    if not result :
        raise HTTPException(status_code=404, detail='Aluno Inexistente')
    return  result

@app.post("/cadastro/")
async def create_question (aluno: Aluno_data, db: db_dependency):
    db_aluno =models.Aluno(name=aluno.name, matricula=aluno.matricula)
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)

@app.get("/cadastro/")
async def read_student ( db: db_dependency ):
    result = db.query(models.Aluno).all()
    
    if not result :
        raise HTTPException(status_code=404, detail='Não existe nem uma aluno no sistema')
    
    return result

@app.delete("/cadastro/{id}")
async def read_student ( student_id: int, db: db_dependency ):
    result = db.query(models.Aluno).filter(models.Aluno.id == student_id).delete()
    db.commit()
    if not result :
        raise HTTPException(status_code=404, detail='Aluno Inexistente')
    
    return  result,  '200'

@app.patch("/cadastro/{id}")
async def update_student(student_id: int, aluno_data: Aluno_data, db: db_dependency):
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == student_id).first()
    
    if not db_aluno:
        raise HTTPException(status_code=404, detail='Aluno não existe ou foi de b')
    
    db_aluno.name = aluno_data.name
    db_aluno.matricula = aluno_data.matricula
    
    db.commit()
    db.refresh(db_aluno)
    
    return db_aluno
