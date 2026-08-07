from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    """Responsável exclusivamente pelo acesso à tabela de usuários."""

    def buscar_por_id(self, db: Session, usuario_id: int) -> Usuario | None:
        """Busca um usuário pelo ID."""
        stmt = select(Usuario).where(Usuario.id == usuario_id)

        return db.scalar(stmt)

    def buscar_por_email(self, db: Session, email: str) -> Usuario | None:
        """Busca um usuário pelo e-mail."""
        stmt = select(Usuario).where(Usuario.email == email)

        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Usuario]:
        """
        Retorna todos os usuários.
        """
        stmt = select(Usuario).order_by(Usuario.nome)

        return list(db.scalars(stmt).all())

    def criar(self, db: Session, usuario: Usuario) -> Usuario:
        """
        Salva um novo usuário.
        """
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        return usuario

    def atualizar(self, db: Session, usuario: Usuario) -> Usuario:
        """
        Atualiza um usuário existente.
        """
        db.commit()
        db.refresh(usuario)

        return usuario

    def excluir(self, db: Session, usuario: Usuario) -> None:
        """
        Remove um usuário.
        """
        db.delete(usuario)
        db.commit()

usuario_repository = UsuarioRepository()