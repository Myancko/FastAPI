from sqlalchemy import Column, Boolean, String, ForeignKey, Integer
from database import Base

class Aluno (Base):
    
    __tablename__ = 'aluno'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    matricula = Column(String, index=True)