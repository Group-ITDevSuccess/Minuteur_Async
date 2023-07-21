import smtplib
import sqlite3
import datetime
from email.message import EmailMessage


def send_email_with_attachment(objet, filename, recipients, smtp):
    # Vérifiez si les variables d'environnement sont définies
    if smtp.get('username') is None or smtp.get('password') is None or smtp.get('port') is None:
        raise ValueError("Les variables d'environnement doivent être définies.")

    message = EmailMessage()
    message["Subject"] = f"Données de {objet}"
    message["From"] = smtp.get('username')
    message["To"] = recipients  # Concaténer les adresses e-mail avec une virgule

    message.set_content("Veuillez trouver ci-joint le fichier Excel contenant les résultats de la requête SQL.")

    with open(filename, "rb") as file:
        content = file.read()
        message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

    with smtplib.SMTP(smtp.get('server'), int(smtp.get('port'))) as server:
        server.starttls()
        server.login(smtp.get('username'), smtp.get('password'))
        server.send_message(message)
        print(f"Message sent to {recipients}")

    conn = sqlite3.connect('./DB_TEST.sqlite3')
    cursor = conn.cursor()
    date = date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().time()
    cursor.execute("""
        INSERT INTO historique (email, data, date, time)
        VALUES (?, ?, ?, ?)
        """, (str(recipients), objet, date, time))
    conn.commit()
    conn.close()
