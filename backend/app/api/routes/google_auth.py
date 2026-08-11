import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.configuracao import Configuracao

router = APIRouter(prefix="/integracoes/google", tags=["Google OAuth"])

SCOPES = ["https://www.googleapis.com/auth/drive"]
REDIRECT_URI = "https://management-system-6bb0.onrender.com/integracoes/google/callback"

def get_client_config():
    """Busca do Pydantic ou diretamente do sistema operacional (Render)."""
    client_id = (
        getattr(settings, "google_client_id", None)
        or os.getenv("GOOGLE_CLIENT_ID")
        or os.getenv("google_client_id")
    )
    client_secret = (
        getattr(settings, "google_client_secret", None)
        or os.getenv("GOOGLE_CLIENT_SECRET")
        or os.getenv("google_client_secret")
    )

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="Variáveis GOOGLE_CLIENT_ID ou GOOGLE_CLIENT_SECRET não configuradas no backend."
        )

    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

@router.get("/login")
def login_google():
    """O Admin clica no app e é redirecionado para a tela de autorização do Google."""
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )
    return RedirectResponse(authorization_url)


@router.get("/callback")
def callback_google(code: str, db: Session = Depends(get_db)):
    """Google redireciona de volta com o código para trocar pelo refresh_token."""
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.refresh_token:
            raise HTTPException(
                status_code=400,
                detail="O Google não retornou o refresh_token. Remova o aplicativo da sua conta Google e tente novamente."
            )

        # Salva ou atualiza no banco de dados
        config = db.query(Configuracao).first()
        if not config:
            config = Configuracao()
            db.add(config)

        config.google_refresh_token = credentials.refresh_token
        db.commit()

        return {
            "status": "sucesso",
            "mensagem": "Google Drive conectado com sucesso! O sistema já está sincronizado."
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao autenticar com o Google: {str(e)}"
        )