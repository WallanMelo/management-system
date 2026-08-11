import os
from urllib.parse import urlencode
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.configuracao import Configuracao

router = APIRouter(prefix="/integracoes/google", tags=["Google OAuth"])

SCOPES = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "https://management-system-6bb0.onrender.com/integracoes/google/callback"


def get_client_credentials():
    """Busca as credenciais das variáveis do settings ou os.getenv."""
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

    return client_id, client_secret


@router.get("/login")
def login_google():
    """Gera a URL direta de autorização OAuth2 do Google."""
    client_id, _ = get_client_credentials()

    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback_google(code: str, db: Session = Depends(get_db)):
    """Recebe o código do Google e troca diretamente pelo refresh_token."""
    client_id, client_secret = get_client_credentials()

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)
        data = response.json()

        if response.status_code != 200 or "refresh_token" not in data:
            erro_detalhe = data.get("error_description") or data.get("error") or "Sem refresh_token."
            raise HTTPException(
                status_code=400,
                detail=f"Não foi possível obter o refresh_token do Google: {erro_detalhe}"
            )

        refresh_token = data["refresh_token"]

        # Salva no banco de dados Neon PostgreSQL
        config = db.query(Configuracao).first()
        if not config:
            config = Configuracao()
            db.add(config)

        config.google_refresh_token = refresh_token
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