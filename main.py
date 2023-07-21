import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import threading
from datetime import datetime
import configparser

from func.utils import calculate_next_month_day, calculate_time_remaining
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

smtp = {'server': server_default,
        'username': username_default,
        'password': password_default,
        'port': port_default
        }


def create_historique_table():
    try:
        conn = sqlite3.connect('./DB_TEST.sqlite3')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historique (
                email TEXT,
                data TEXT,
                date DATE,
                time TIME,
                status TEXT
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        # Handle the error if the table creation fails
        messagebox.showerror("Error", f"An error occurred while creating the 'historique' table: {str(e)}")


def data_sent_email():
    try:
        conn = sqlite3.connect('./DB_TEST.sqlite3')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Societes.name, Societes.server, Societes.username, Societes.password, Emails.email
            FROM EmailSociete
            INNER JOIN Societes ON EmailSociete.id_societe = Societes.id
            INNER JOIN Emails ON EmailSociete.id_email = Emails.id
        """)
        rows = cursor.fetchall()
        print(rows)

        for row in rows:
            # Traitez chaque ligne de données ici
            name, server, username, password, email = row
            print()
            print("----------------------")
            print("Société Name:", name)
            print("Société Server:", server)
            print("Société Username:", username)
            print("Société Password:", password)
            print("Email:", email)
            print("----------------------")
            print()

            base = {
                'server': server,
                'database': name,
                'username': username,
                'password': password
            }
            recipient = email

            df = execute_sql_query(base)
            filename = export_to_excel(df=df, objet=name)
            send_email_with_attachment(objet=name, filename=filename, recipients=recipient, smtp=smtp)

        cursor.close()
        conn.close()

        return rows

    except Exception as e:
        # You can customize the error message as per your requirement
        messagebox.showerror("Error", f"An error occurred: {str(e)} ")


def execute_script():
    try:
        create_historique_table()
        data_sent_email()
        update_time_remaining_label()
    except Exception as e:
        # You can customize the error message as per your requirement
        messagebox.showerror("Error", f"An error occured : {str(e)} ")


def format_time(days, hours, minutes, seconds):
    return f"{days} jours, {hours:02d} heures, {minutes:02d} minutes, {seconds:02d} secondes"


def update_history_table(order_by=None):
    try:
        conn = sqlite3.connect('./DB_TEST.sqlite3')
        cursor = conn.cursor()

        # Requête de base pour récupérer les données de l'historique
        query = "SELECT email, data, date, time, status FROM historique"

        # Ajouter la clause ORDER BY si une colonne de tri est spécifiée
        if order_by:
            query += f" ORDER BY {order_by}"

        cursor.execute(query)
        rows = cursor.fetchall()

        history_tree.delete(*history_tree.get_children())

        for row in rows:
            history_tree.insert("", "end", values=row)

        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error",
                             f"An error occurred while fetching data from the 'historique' table: {str(e)}")


def sort_column(col):
    # Appeler la fonction de mise à jour du tableau avec la colonne sur laquelle trier
    update_history_table(order_by=col)


def update_label_periodically():
    update_time_remaining_label()
    window.after(1000, update_label_periodically)
    window.after(2000, update_history_table)  # Update every 1 seconds


def update_time_remaining_label():
    heur_rappel = calculate_time_remaining()
    if heur_rappel.days == 0 and heur_rappel.seconds == 0:
        next_month_day = calculate_next_month_day()
        query_thread()
        time_until_next_month_day = next_month_day - datetime.now()
        days = time_until_next_month_day.days
        hours = time_until_next_month_day.seconds // 3600
        minutes = (time_until_next_month_day.seconds // 60) % 60
        seconds = time_until_next_month_day.seconds % 60
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
    window.geometry("800x500")  # Set a default window size

    # Set a custom style for widgets
    style = ttk.Style()
    style.configure('Custom.TLabel', font=('Helvetica', 20), padding=10)
    style.configure('Custom.TButton', font=('Helvetica', 16), padding=10)
    style.configure('Custom.Treeview', font=('Helvetica', 12))

    # Create a frame to organize widgets
    content_frame = ttk.Frame(window)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Création de l'étiquette pour afficher le temps restant
    time_remaining_label = ttk.Label(content_frame, text="Envoi de Mail Automatique", style='Custom.TLabel')
    time_remaining_label.pack(pady=10)

    # Bouton pour exécuter le script
    execute_button = ttk.Button(content_frame, text="Exécuter le script", command=query_thread, style='Custom.TButton')
    execute_button.pack(pady=10)

    # Créer une Treeview widget pour afficher la table historique
    history_tree = ttk.Treeview(content_frame, columns=("Email", "Data", "Date", "Time", "Statut"), show="headings", style='Custom.Treeview')
    history_tree.heading("Email", text="Email", anchor=tk.CENTER, command=lambda: sort_column("email"))
    history_tree.heading("Data", text="Data", anchor=tk.CENTER, command=lambda: sort_column("data"))
    history_tree.heading("Date", text="Date", anchor=tk.CENTER, command=lambda: sort_column("date"))
    history_tree.heading("Time", text="Time", anchor=tk.CENTER, command=lambda: sort_column("time"))
    history_tree.heading("Statut", text="Statut", anchor=tk.CENTER, command=lambda: sort_column("status"))
    history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Appeler la fonction pour mettre à jour la table et activer le tri initial (sans tri)
    update_history_table()

    # Call the function to update the label and history table periodically
    update_label_periodically()

    # Call the function to update the history table periodically
    update_history_table()

    # Start the tkinter main loop
    window.mainloop()
