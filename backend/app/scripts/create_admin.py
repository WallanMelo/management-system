from app.database.session import SessionLocal
from app.models.usuario import Usuario
from app.models.enums import PerfilUsuario

from app.repositories.usuario import usuario_repository
from app.core.security import gerar_hash_senha


def main():

    db = SessionLocal()

    try:

        email = "admin@documentos.com"

        usuario = usuario_repository.buscar_por_email(
            db,
            email
        )

        if usuario:
            print("Administrador já existe.")
            return

        admin = Usuario(
            nome="Administrador",
            email=email,
            senha_hash=gerar_hash_senha("123456"),
            perfil=PerfilUsuario.ADMIN,
            ativo=True
        )

        usuario_repository.criar(
            db,
            admin
        )

        print("=" * 50)
        print("Administrador criado com sucesso!")
        print()
        print(f"Email : {email}")
        print("Senha : 123456")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    main()