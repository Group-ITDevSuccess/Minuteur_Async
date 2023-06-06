from email.message import EmailMessage
import smtplib

def send_email_with_attachment(filename, recipient):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "muriel.raharison@inviso-group.com"
    smtp_password = "DzczeHgosm"

    message = EmailMessage()
    message["Subject"] = "Données de requête SQL"
    message["From"] = smtp_username
    message["To"] = recipient

    message.set_content("Veuillez trouver ci-joint le fichier Excel contenant les résultats de la requête SQL.")

    with open(filename, "rb") as file:
        content = file.read()
        message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

