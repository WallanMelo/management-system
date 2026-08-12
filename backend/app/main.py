import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Banco de Dados e Segurança (Importados primeiro para evitar importação circular)
from app.database.engine import engine 
from app.database.base import Base 
from app.database.session import SessionLocal 
from app.core.security import gerar_hash_senha

# 2. Modelos
from app.models.usuario import Usuario 
from app.models.enums import PerfilUsuario

# 3. Rotas da API
from app.api.routes import (
    auth,
    usuario,
    cliente,
    diretorio,
    documento,
    compartilhamento,
    configuracao,
    auditoria,
    sincronizacao,
    google_auth
)

# Cria as tabelas no banco caso não existam
Base.metadata.create_all(bind=engine)

def criar_admin_inicial():
    db = SessionLocal()
    try:
        if not db.query(Usuario).first():
            admin = Usuario(
                nome="Administrador",
                email="admin@sistema.com",
                senha_hash=gerar_hash_senha("admin123"),
                perfil=PerfilUsuario.ADMIN,
                ativo=True
            )
            db.add(admin)
            db.commit()
            print(">>> Usuário admin inicial criado no Neon!")
    except Exception as e:
        print(f">>> Erro ao criar admin inicial: {e}")
        db.rollback()
    finally:
        db.close()

criar_admin_inicial()

app = FastAPI(
    title="Sistema de Gestão de Documentos",
    description="""
API desenvolvida para gerenciamento de documentos utilizando:

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT
- Google Drive (integração)
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(cliente.router)
app.include_router(diretorio.router)
app.include_router(documento.router)
app.include_router(compartilhamento.router)
app.include_router(configuracao.router)
app.include_router(auditoria.router)
app.include_router(sincronizacao.router)
app.include_router(google_auth.router)

@app.get("/", tags=["Home"])
def home():
    return {"status": "online", "mensagem": "Sistema de Gestão de Documentos", "versao": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "database": "online", "api": "running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
