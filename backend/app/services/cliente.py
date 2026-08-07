from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.cliente import cliente_repository
from app.schemas.cliente import ClienteCreate, ClienteUpdate

class ClienteService:

    def listar(self, db: Session):
        return cliente_repository.listar(db)

    def buscar(self, db: Session, cliente_id: int):

        cliente = cliente_repository.buscar_por_id(db,cliente_id)

        if not cliente:
            raise ValueError("Cliente não encontrado.")

        return cliente

    def criar(self,db: Session,dados: ClienteCreate,):
        cliente = Cliente(
            nome=dados.nome,
            cpf_cnpj=dados.cpf_cnpj,
            telefone=dados.telefone,
            email=dados.email,
            observacao=dados.observacao,
            ativo=dados.ativo,
        )
        return cliente_repository.criar(db,cliente,)

    def atualizar(self,db: Session,cliente: Cliente,dados: ClienteUpdate,):

        if dados.nome is not None:
            cliente.nome = dados.nome

        if dados.cpf_cnpj is not None:
            cliente.cpf_cnpj = dados.cpf_cnpj

        if dados.telefone is not None:
            cliente.telefone = dados.telefone

        if dados.email is not None:
            cliente.email = dados.email

        if dados.observacao is not None:
            cliente.observacao = dados.observacao

        if dados.ativo is not None:
            cliente.ativo = dados.ativo

        return cliente_repository.atualizar(db,cliente,)

    def excluir(self, db: Session, cliente: Cliente):
        cliente_repository.excluir(db, cliente)


cliente_service = ClienteService()