from app.core.config import settings
from sqlalchemy import create_engine


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True, # exibe as consutas sql no terminal
    future=True #compatibilidade com o sqlalchemy 2.x
)