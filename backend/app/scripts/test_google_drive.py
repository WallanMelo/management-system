from app.integrations.google_drive import GoogleDriveClient

def main():

    drive = GoogleDriveClient()

    dados = drive.testar_conexao()

    print(dados)


if __name__ == "__main__":
    main()