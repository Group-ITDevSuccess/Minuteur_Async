import smtplib
from email.message import EmailMessage


def send_email_with_attachment(objet, filename, recipients, smtp):
    # Vérifiez si les variables d'environnement sont définies
    if smtp['username'] is None or smtp['password'] is None or smtp['port'] is None:
        raise ValueError("Les variables d'environnement doivent être définies.")

    message = EmailMessage()
    message["Subject"] = f"Données de {objet}"
    message["From"] = smtp['username']
    message["To"] = ", ".join(recipients)

    message.set_content("Veuillez trouver ci-joint le fichier Excel contenant les résultats de la requête SQL.")

    with open(filename, "rb") as file:
        content = file.read()
        message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

    with smtplib.SMTP(smtp['server'], int(smtp['port'])) as server:
        server.starttls()
        server.login(smtp['username'], smtp['password'])
        server.send_message(message)
        print(f"Message sent to {', '.join(recipients)}")
