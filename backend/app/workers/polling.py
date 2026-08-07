import logging
import time

from app.core.config import settings
from app.database.session import SessionLocal
from app.services.sync_service import sync_service

logger = logging.getLogger(__name__)

def executar():
    logger.info("=" * 60)
    logger.info("WORKER DE SINCRONIZAÇÃO INICIADO")
    logger.info("=" * 60)

    while True:
        db = SessionLocal()
        try:
            logger.info("Verificando alterações no Google Drive...")
            sync_service.sincronizacao_incremental(db)
            logger.info("Sincronização concluída.")

        except Exception as e:
            logger.exception(f"Erro durante sincronização: {e}")

        finally:
            db.close()

        time.sleep(settings.polling_interval)


if __name__ == "__main__":
    executar()