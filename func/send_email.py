import smtplib
import sqlite3
import datetime
from email.message import EmailMessage


def send_email_with_attachment(objet, filename, recipients, smtp, local_db):
    try:

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

        # Connexion à la base de données
        conn = sqlite3.connect(local_db)
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().time()

        # Enregistrement du statut de l'envoi dans la table de l'historique
        cursor.execute("""
            INSERT INTO Historique (email, data, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (str(recipients), str(objet), str(date), str(time), "Envoyé"))

        conn.commit()
        conn.close()

        print(f"Message sent to {recipients}")
    except Exception as e:
        # En cas d'erreur, enregistrez le statut "Non envoyé" dans la table de l'historique
        conn = sqlite3.connect(local_db)
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().time()

        cursor.execute("""
            INSERT INTO Historique (email, data, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (str(recipients), str(objet), str(date), str(time), "Non envoyé"))

        conn.commit()
        conn.close()

        print(f"Error sending message to {recipients}: {str(e)}")
