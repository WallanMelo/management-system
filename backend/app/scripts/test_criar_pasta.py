from app.services.google_drive_service import google_drive_service


def main():

    pasta_id = google_drive_service.criar_pasta_cliente("PASTA DE Teste")

    print()

    print("=" * 50)
    print("Pasta criada!")
    print(f"ID: {pasta_id}")
    print("=" * 50)

if __name__ == "__main__":
    main()