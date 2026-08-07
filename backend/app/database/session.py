from sqlalchemy.orm import sessionmaker
from app.database.engine import engine
from typing import Generator

SessionLocal = sessionmaker(
    bind=engine, #faz a  ligação entre o session.py e o engine.py
    autoflush=False, #não deixa fazer o envio de alterações automaticamente
    autocommit=False, #Nada vai ser ssalvo de forma automatica, o controle fica  com o desenvolvedor no arquivo de controle do DB
    expire_on_commit=False
)

def get_db() -> Generator: #função para fornecer para as rotas a sessão ao fastAPI
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        