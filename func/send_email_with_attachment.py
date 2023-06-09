from email.message import EmailMessage
import smtplib
import configparser

# Chemin du fichier .env
env_file = '.env'

# Créer un objet ConfigParser
config = configparser.ConfigParser()

# Lire les variables d'environnement à partir du fichier .env
config.read(env_file)

# Récupérer les valeurs des variables d'environnement
smtp_server = config.get('DEFAULT', 'SMTP_SERVEUR')
smtp_username = config.get('DEFAULT', 'SMTP_USERNAME')
smtp_password = config.get('DEFAULT', 'SMTP_PASSWORD')
smtp_port = config.get('DEFAULT', 'SMTP_PORT')

# Vérifiez si les variables d'environnement sont définies
if smtp_username is None or smtp_password is None or smtp_password is None or smtp_port is None:
    raise ValueError("Les variables d'environnements doivent être définies.")


def send_email_with_attachment(filename, recipient):
    message = EmailMessage()
    message["Subject"] = "Données de requête SQL"
    message["From"] = smtp_username
    message["To"] = recipient

    message.set_content("Veuillez trouver ci-joint le fichier Excel contenant les résultats de la requête SQL.")

    with open(filename, "rb") as file:
        content = file.read()
        message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

    with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)
        print(f"Message sent to {recipient}")
