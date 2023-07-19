import tkinter as tk
import threading
from datetime import datetime
import configparser

from func.utils import calculate_next_thursday, calculate_time_remaining
from func.execute_query import execute_sql_query
from func.export_to_excel import export_to_excel
from func.send_email import send_email_with_attachment
from data_send import data_sent_email

# Chemin du fichier .env
env_file = '.env'

# Créer un objet ConfigParser
config = configparser.ConfigParser()

# Lire les variables d'environnement à partir du fichier .env
config.read(env_file)

# Récupérer les valeurs des variables d'environnement
server_default = config.get('DEFAULT', 'SMTP_SERVEUR')
username_default = config.get('DEFAULT', 'SMTP_USERNAME')
password_default = config.get('DEFAULT', 'SMTP_PASSWORD')
port_default = config.get('DEFAULT', 'SMTP_PORT')
recipient = config.get('USER', 'RECIPIENT')

# Informations de connexion
server_connexion = config.get('SERVER', 'SERVER_CONNEXION')
database_connexion = config.get('SERVER', 'DATABASE_CONNEXION')
username_connexion = config.get('SERVER', 'USER_CONNEXION')
password_connexion = config.get('SERVER', 'PASS_CONNEXION')

smtp = {'server': server_default,
        'username': username_default,
        'password': password_default,
        'port': port_default
        }

base = {
    'server': server_connexion,
    'database': database_connexion,
    'username': username_connexion,
    'password': password_connexion
    }


def execute_script():
    df = execute_sql_query(base)
    filename = export_to_excel(df)
    recipients = recipient.split(",")
    send_email_with_attachment(filename, recipients, smtp)
    update_time_remaining_label()


def format_time(days, hours, minutes, seconds):
    return f"{days} jours, {hours:02d} heures, {minutes:02d} minutes, {seconds:02d} secondes"


def update_label_periodically():
    update_time_remaining_label()
    window.after(1000, update_label_periodically)


def update_time_remaining_label():
    heur_rappel = calculate_time_remaining()
    if heur_rappel.days == 0 and heur_rappel.seconds == 0:
        next_thursday = calculate_next_thursday()
        query_thread()
        time_until_next_thursday = next_thursday - datetime.now()
        days = time_until_next_thursday.days
        hours = time_until_next_thursday.seconds // 3600
        minutes = (time_until_next_thursday.seconds // 60) % 60
        seconds = time_until_next_thursday.seconds % 60
        time_remaining_label["text"] = "Prochain compte à rebours avant le prochain envoi : " + \
                                       format_time(days, hours, minutes, seconds)
    else:
        days = heur_rappel.days
        hours = heur_rappel.seconds // 3600
        minutes = (heur_rappel.seconds // 60) % 60
        seconds = heur_rappel.seconds % 60
        time_remaining_label["text"] = "Temps restant jusqu'au prochain envoi : " + \
                                       format_time(days, hours, minutes, seconds)


def query_thread():
    query = threading.Thread(target=execute_script, args=())
    query.start()


if __name__ == "__main__":
    window = tk.Tk()
    window.title("Programme d'envoi de données")

    # Création de l'étiquette pour afficher le temps restant
    time_remaining_label = tk.Label(window, text="Envoi de Mail Automatique", font=("Helvetica", 30))
    time_remaining_label.pack(pady=10)

    # Mise à jour périodique de l'étiquette du temps restant
    update_label_periodically()

    # Bouton pour exécuter le script
    execute_button = tk.Button(window, text="Exécuter le script", command=query_thread)
    execute_button.pack(pady=10)

    window.mainloop()
