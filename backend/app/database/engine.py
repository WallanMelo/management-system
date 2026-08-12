from app.core.config import settings
from sqlalchemy import create_engine

# Aceita tanto a DATABASE_URL completa (padrão do Neon/Render) quanto os campos individuais
database_url = getattr(settings, "DATABASE_URL", None) or getattr(settings, "database_url", None)

if not database_url:
    database_url = (
        f"postgresql+psycopg2://"
        f"{settings.database_user}:"
        f"{settings.database_password}@"
        f"{settings.database_host}:"
        f"{settings.database_port}/"
        f"{settings.database_name}"
    )

# Converte prefixos antigos 'postgres://' para 'postgresql://' se necessário
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    database_url,
    echo=True,
    future=True
)
