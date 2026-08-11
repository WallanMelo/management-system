import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    usuario,
    cliente,
    diretorio,
    documento,
    compartilhamento,
    configuracao,
    auditoria,
    sincronizacao
)


from fastapi import FastAPI
from app.database.engine import engine  
from app.database.base import Base  
from app.database.session import SessionLocal    # Ajuste o import do seu SessionLocal
from app.models.usuario import Usuario          # Ajuste o import do seu Model de Usuario
from app.core.security import gerar_hash_senha
from app.models.enums import PerfilUsuario
from app.api.routes import google_auth

# Esta linha instrui o SQLAlchemy a criar todas as tabelas caso não existam
Base.metadata.create_all(bind=engine)

def criar_admin_inicial():
    db = SessionLocal()
    try:
        if not db.query(Usuario).first():
            admin = Usuario(
                nome="Administrador",
                email="admin@sistema.com",
                senha_hash=gerar_hash_senha("admin123"),
                perfil=PerfilUsuario.ADMIN,  # Atenção: Ajuste para o nome do item no seu Enum (ex: PerfilUsuario.ADMINISTRADOR)
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

# Executa a criação do primeiro usuario no carregamento do backend
criar_admin_inicial()

app = FastAPI(
    title="Sistema de Gestão de Documentos",
    description="""
API desenvolvida para gerenciamento de documentos utilizando:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT
- Google Drive (integração)
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# =====================================================================
# CORS (Permite acesso de qualquer IP/Origem)
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Libera para o Electron
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# Rotas
# =====================================================================
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
# =====================================================================
# Home
# =====================================================================
@app.get("/", tags=["Home"])
def home():
    return {"status": "online","mensagem": "Sistema de Gestão de Documentos","versao": "1.0.0",}

# =====================================================================
# Health Check
# =====================================================================
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok","database": "online","api": "running",}

# =====================================================================
# EXECUÇÃO (Escuta em 0.0.0.0 + Porta Dinâmica da Nuvem)
# =====================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

