from app.core.config import settings
from sqlalchemy import create_engine

# Aceita tanto a DATABASE_URL completa (padrão do Neon/Render) quanto os campos individuais
DATABASE_URL = getattr(settings, "DATABASE_URL", None) or getattr(settings, "database_url", None)

if not database_url:
    DATABASE_URL = (
        f"postgresql+psycopg2://"
        f"{settings.database_user}:"
        f"{settings.database_password}@"
        f"{settings.database_host}:"
        f"{settings.database_port}/"
        f"{settings.database_name}"
    )

# Converte prefixos antigos 'postgres://' para 'postgresql://' se necessário
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True
)
