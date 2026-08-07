from sqlalchemy.orm import Session

from app.models.configuracao import Configuracao
from app.repositories.configuracao import configuracao_repository
from app.schemas.configuracao import ConfiguracaoUpdate


class ConfiguracaoService:

    def obter(self, db: Session):
        configuracao = configuracao_repository.obter(db)

        if not configuracao:
            raise ValueError("Configuração não encontrada.")

        return configuracao

    def criar(
        self,
        db: Session,
        dados: ConfiguracaoUpdate,
    ):

        if configuracao_repository.obter(db):
            raise ValueError(
                "Já existe uma configuração cadastrada."
            )

        configuracao = Configuracao(
            nome_empresa=dados.nome_empresa,
            cnpj=dados.cnpj,
            telefone=dados.telefone,
            email=dados.email,
            logo=dados.logo,
            pasta_drive=dados.pasta_drive,
            tema=dados.tema,
            backup_automatico=dados.backup_automatico,
        )

        return configuracao_repository.criar(
            db,
            configuracao,
        )

    def atualizar(
        self,
        db: Session,
        configuracao: Configuracao,
        dados: ConfiguracaoUpdate,
    ):

        configuracao.nome_empresa = dados.nome_empresa
        configuracao.cnpj = dados.cnpj
        configuracao.telefone = dados.telefone
        configuracao.email = dados.email
        configuracao.logo = dados.logo
        configuracao.pasta_drive = dados.pasta_drive
        configuracao.tema = dados.tema
        configuracao.backup_automatico = dados.backup_automatico

        return configuracao_repository.atualizar(
            db,
            configuracao,
        )


configuracao_service = ConfiguracaoService()