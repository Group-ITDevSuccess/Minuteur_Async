import smtplib
import sqlite3
import datetime
from email.message import EmailMessage


def send_email_with_attachment(data, filename, recipients, smtp, local_db, objet_mail, message_mail, copy):
    try:

        # Vérifiez si les variables d'environnement sont définies
        if smtp.get('username') is None or smtp.get('password') is None or smtp.get('port') is None:
            raise ValueError("Les variables d'environnement doivent être définies.")

        # Convertir la variable "copy" en une liste si elle n'est pas déjà une liste
        if not isinstance(copy, list):
            copy = [copy]

        # Utiliser la liste "copy" pour l'attribut "Cc" de l'objet "message"

        message = EmailMessage()
        message["Subject"] = f"{objet_mail}, {data}"
        message["From"] = smtp.get('username')
        message["To"] = recipients  # Concaténer les adresses e-mail avec une virgule
        message["Cc"] = ", ".join(copy)

        message.set_content(message_mail)

        with open(filename, "rb") as file:
            content = file.read()
            message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

        with smtplib.SMTP(smtp.get('server'), int(smtp.get('port'))) as server:
            server.starttls()
            server.login(smtp.get('username'), smtp.get('password'))
            server.send_message(message)
            print(f"Message sent to {recipients}")

        # Connexion à la base de données
        conn = sqlite3.connect(local_db)
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().time()

        # Enregistrement du statut de l'envoi dans la table de l'historique
        cursor.execute("""
            INSERT INTO Historique (email, data, objet, message, date, time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(recipients), str(data), str(objet_mail), str(message_mail), str(date), str(time), "Envoyé"))

        conn.commit()
        conn.close()

        print(f"{objet_mail}, {recipients}")
    except Exception as e:
        # En cas d'erreur, enregistrez le statut "Non envoyé" dans la table de l'historique
        conn = sqlite3.connect(local_db)
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().time()

        cursor.execute("""
            INSERT INTO Historique (email, data, objet, message,  date, time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(recipients), str(data), str(objet_mail), str(message_mail), str(date), str(time), "Non envoyé"))

        conn.commit()
        conn.close()

        print(f"Error sending message to {recipients}: {str(e)}")
