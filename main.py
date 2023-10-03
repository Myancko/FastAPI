from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from datetime import datetime 
from pydantic import BaseModel
from typing import List, Annotated
import models
import time
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

class Log:

    def database_log_injection(self, request, db):

        rq= request.method
        db_log = models.log(data = datetime.now(), requisition = str(rq),  user = 'anon')
        db.add(db_log)
        db.commit()
        print('backgroud funcinou')
        
    
@app.middleware("http")
async def log_general(request: Request, call_next):

    method_name = request.method
    qp_map = request.query_params
    pp_map = request.path_params
    with open("request_log.txt", mode="a+") as reqfile:
        content = f"method: '{method_name}', query param: '{qp_map}', path params: '{pp_map}' received at '{datetime.now()}'\n"
        reqfile.write(content)
    response = await call_next(request)

    return response

@app.get("/cadastro/{id}")
async def read_student ( student_id: int, db: db_dependency, request : Request, bg_task: BackgroundTasks ):
    log = Log()
    bg_task.add_task(log.database_log_injection, request=request, db=db)
    result = db.query(models.Aluno).filter(models.Aluno.id == student_id).first()
    
    if not result :
        raise HTTPException(status_code=404, detail='Aluno Inexistente')
    return  result

@app.post("/cadastro/")
async def create_question (aluno: Aluno_data, db: db_dependency, request : Request, bg_task: BackgroundTasks):
    db_aluno =models.Aluno(name=aluno.name, matricula=aluno.matricula)
    db.add(db_aluno)
    
    log = Log()
    
    bg_task.add_task(log.database_log_injection, request=request, db=db)
    
    db.commit()
    print('ok')
    db.refresh(db_aluno)


@app.get("/cadastro/")
async def read_student ( db: db_dependency, request : Request, bg_task: BackgroundTasks ):
    log = Log()
    bg_task.add_task(log.database_log_injection, request=request, db=db)
    result = db.query(models.Aluno).all()
    
    if not result :
        raise HTTPException(status_code=404, detail='Não existe nem uma aluno no sistema')
    
    return result

@app.delete("/cadastro/{id}")
async def read_student ( student_id: int, db: db_dependency, request : Request, bg_task: BackgroundTasks ):
    log = Log()
    bg_task.add_task(log.database_log_injection, request=request, db=db)
    result = db.query(models.Aluno).filter(models.Aluno.id == student_id).delete()
    db.commit()
    if not result :
        raise HTTPException(status_code=404, detail='Aluno Inexistente')
    
    return  result,  '200'

@app.patch("/cadastro/{id}")
async def update_student(student_id: int, aluno_data: Aluno_data, db: db_dependency, request : Request, bg_task: BackgroundTasks):
    log = Log()
    bg_task.add_task(log.database_log_injection, request=request, db=db)
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == student_id).first()
    
    if not db_aluno:
        raise HTTPException(status_code=404, detail='Aluno não existe ou foi de b')
    
    db_aluno.name = aluno_data.name
    db_aluno.matricula = aluno_data.matricula
    
    db.commit()
    db.refresh(db_aluno)
    
    return db_aluno