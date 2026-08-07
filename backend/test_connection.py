from sqlalchemy import text

from app.database.engine import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        print(result.fetchone())

        print("Conexão com PostgreSQL realizada com sucesso!")

except Exception as e:
    print("Erro ao conectar:")
    print(e)