from datetime import datetime
import zoneinfo
from sqlalchemy.orm import Session
from app.models.documento import Documento
from app.models.diretorio import Diretorio
from app.services.google_drive_service import google_drive_service
from app.core.config import settings


def _converter_data_drive(data_str: str | None) -> datetime | None:
    """Converte a data ISO do Google Drive (UTC) para o fuso de Brasília (UTC-3)."""
    if not data_str:
        return None
    try:
        # Parse da string UTC enviada pelo Drive (ex: 2026-08-05T15:00:00.000Z)
        dt_utc = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        fuso_br = zoneinfo.ZoneInfo("America/Sao_Paulo")
        dt_br = dt_utc.astimezone(fuso_br)
        # Remove a informação de fuso para salvar como Naive no SQLAlchemy
        return dt_br.replace(tzinfo=None)
    except Exception:
        return None


class SyncService:

    def sincronizacao_completa(self, db: Session):
        print("🔄 Iniciando sincronização e conciliação completa com o Google Drive...")

        # 1. Busca a lista plana de todos os itens ativos no Google Drive
        itens_drive = google_drive_service.listar_arvore_root()

        # Mapeia IDs ativos no Google Drive
        drive_file_ids_ativos = set()
        drive_folder_ids_ativos = set()

        for item in itens_drive:
            file_id = item.get("id")
            mime_type = item.get("mimeType", "")

            if mime_type == "application/vnd.google-apps.folder":
                drive_folder_ids_ativos.add(file_id)
            else:
                drive_file_ids_ativos.add(file_id)

        # =========================================================================
        # 🧹 2. CONCILIAÇÃO DE EXCLUSÃO (DOCUMENTOS)
        # =========================================================================
        documentos_locais = db.query(Documento).all()
        removidos_docs_count = 0

        for doc in documentos_locais:
            if doc.drive_file_id and doc.drive_file_id not in drive_file_ids_ativos:
                db.delete(doc)
                removidos_docs_count += 1

        print(f"🗑️ Documentos removidos do banco local: {removidos_docs_count}")

        # =========================================================================
        # 🧹 3. CONCILIAÇÃO DE EXCLUSÃO (PASTAS / DIRETÓRIOS)
        # =========================================================================
        try:
            diretorios_locais = db.query(Diretorio).all()
            removidos_pastas_count = 0
            for pasta in diretorios_locais:
                if pasta.drive_folder_id and pasta.drive_folder_id not in drive_folder_ids_ativos:
                    db.delete(pasta)
                    removidos_pastas_count += 1
            print(f"🗑️ Pastas removidas do banco local: {removidos_pastas_count}")
        except Exception as e:
            print(f"⚠️ Aviso na conciliação de pastas: {e}")

        # Timestamp atual para registrar o momento exato do sync local
        agora = datetime.now()

        # =========================================================================
        # 🔄 4. ATUALIZAÇÃO E INSERÇÃO DE PASTAS (DIRETÓRIOS)
        # =========================================================================
        for item in itens_drive:
            mime_type = item.get("mimeType")
            if mime_type == "application/vnd.google-apps.folder":
                file_id = item.get("id")
                nome = item.get("name")
                parents = item.get("parents", [])
                parent_id = parents[0] if parents else None
                modified_time = _converter_data_drive(item.get("modifiedTime"))
                created_time = _converter_data_drive(item.get("createdTime"))

                pasta_db = db.query(Diretorio).filter(Diretorio.drive_folder_id == file_id).first()
                if pasta_db:
                    pasta_db.nome = nome
                    pasta_db.modified_time = modified_time
                    if hasattr(pasta_db, "ultima_sincronizacao"):
                        pasta_db.ultima_sincronizacao = agora
                    if hasattr(pasta_db, "drive_parent_id"):
                        pasta_db.drive_parent_id = parent_id
                    if hasattr(pasta_db, "created_at") and created_time:
                        pasta_db.created_at = created_time
                else:
                    nova_pasta = Diretorio(
                        nome=nome,
                        drive_folder_id=file_id,
                        drive_parent_id=parent_id if hasattr(Diretorio, "drive_parent_id") else None,
                        modified_time=modified_time,
                        sincronizado=True,
                    )
                    if hasattr(nova_pasta, "ultima_sincronizacao"):
                        nova_pasta.ultima_sincronizacao = agora
                    if hasattr(nova_pasta, "created_at") and created_time:
                        nova_pasta.created_at = created_time
                    db.add(nova_pasta)

        db.flush()  # Garante que as pastas existam antes dos arquivos

        # =========================================================================
        # 🔄 5. ATUALIZAÇÃO E INSERÇÃO DE ARQUIVOS (DOCUMENTOS)
        # =========================================================================
        for item in itens_drive:
            mime_type = item.get("mimeType")
            if mime_type != "application/vnd.google-apps.folder":
                file_id = item.get("id")
                nome = item.get("name")
                tamanho = item.get("size", 0)
                parents = item.get("parents", [])
                parent_id = parents[0] if parents else None

                # Converte as duas datas do Drive para o fuso local (UTC-3)
                modified_time = _converter_data_drive(item.get("modifiedTime"))
                created_time = _converter_data_drive(item.get("createdTime"))

                doc = db.query(Documento).filter(Documento.drive_file_id == file_id).first()
                if doc:
                    doc.nome_original = nome
                    doc.nome_sistema = nome
                    doc.drive_parent_id = parent_id
                    doc.mime_type = mime_type
                    doc.tamanho = int(tamanho) if tamanho else 0
                    if hasattr(doc, "modified_time"):
                        doc.modified_time = modified_time
                    if hasattr(doc, "created_at") and created_time:
                        doc.created_at = created_time
                    if hasattr(doc, "ultima_sincronizacao"):
                        doc.ultima_sincronizacao = agora
                else:
                    novo_doc = Documento(
                        nome_original=nome,
                        nome_sistema=nome,
                        drive_file_id=file_id,
                        drive_parent_id=parent_id,
                        tamanho=int(tamanho) if tamanho else 0,
                        mime_type=mime_type,
                        sincronizado=True,
                        created_at=created_time or agora,
                    )
                    if hasattr(novo_doc, "modified_time"):
                        novo_doc.modified_time = modified_time
                    if hasattr(novo_doc, "ultima_sincronizacao"):
                        novo_doc.ultima_sincronizacao = agora
                    db.add(novo_doc)

        db.commit()
        print("✅ Sincronização e conciliação concluídas com sucesso!")


sync_service = SyncService()