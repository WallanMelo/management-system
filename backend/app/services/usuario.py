from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate
)

from datetime import datetime

from app.repositories.usuario import usuario_repository

from app.core.security import (
    gerar_hash_senha,
    verificar_senha
)


class UsuarioService:

    def listar(self, db: Session):
        return usuario_repository.listar(db)

    def buscar(self, db: Session, usuario_id: int):

        usuario = usuario_repository.buscar_por_id(
            db,
            usuario_id
        )

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        return usuario

    def criar(
        self,
        db: Session,
        dados: UsuarioCreate
    ):

        if usuario_repository.buscar_por_email(
            db,
            dados.email
        ):
            raise ValueError("Email já cadastrado.")

        usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha_hash=gerar_hash_senha(dados.senha),
            perfil=dados.perfil
        )

        return usuario_repository.criar(db, usuario)

    def atualizar(self,db: Session,usuario: Usuario,dados: UsuarioUpdate):

        for campo, valor in dados.model_dump(
            exclude_unset=True
        ).items():

            if campo == "senha":
                usuario.senha_hash = gerar_hash_senha(valor)

            else:
                setattr(usuario, campo, valor)

        return usuario_repository.atualizar(db,usuario)

    def excluir(self,db: Session,usuario: Usuario):
        usuario_repository.excluir(db,usuario)

    def autenticar(self,db: Session,email: str,senha: str):
        usuario = usuario_repository.buscar_por_email(db,email)

        if not usuario:
            return None

        if not verificar_senha(senha,usuario.senha_hash):
            return None
        return usuario

    def atualizar_ultimo_login(self,db: Session,usuario: Usuario):
        usuario.ultimo_login = datetime.utcnow()
        db.commit()

    def alterar_senha(self, db: Session, usuario: Usuario, senha_atual: str, nova_senha: str):
            # 1. Valida se a senha atual informada bate com a do banco
            if not verificar_senha(senha_atual, usuario.senha_hash):
                raise ValueError("A senha atual está incorreta.")

            # 2. Gera o hash da nova senha
            usuario.senha_hash = gerar_hash_senha(nova_senha)

            # 3. Persiste a alteração no banco
            return usuario_repository.atualizar(db, usuario)

usuario_service = UsuarioService()