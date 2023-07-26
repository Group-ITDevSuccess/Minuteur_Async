import sqlite3
import tkinter.messagebox as messagebox
import threading
import configparser
import os
import datetime
from func.utils import calculate_next_month_day, calculate_time_remaining, EnvFileHandler, update_config_from_env, \
    get_env_variable
from func.execute_query import execute_sql_query
from func.export_to_excel import export_to_excel
from func.send_email import send_email_with_attachment
from watchdog.observers import Observer
from PIL import Image, ImageTk

# Chemin du fichier config.ini
config_file = 'config.ini'

# Charger les variables d'environnement à partir du fichier config.ini
config = configparser.ConfigParser()
config.read(config_file)

database_name = config.get('LOCAL', 'DATABASE_NAME')
database_path = os.path.join(os.path.dirname(__file__), database_name)

smtp = {
    'server': config.get('DEFAULT', 'SMTP_SERVEUR'),
    'username': config.get('DEFAULT', 'SMTP_USERNAME'),
    'password': config.get('DEFAULT', 'SMTP_PASSWORD'),
    'port': config.getint('DEFAULT', 'SMTP_PORT')
}


def watch_env_file():
    calculate_time_remaining()
    calculate_next_month_day()
    update_time_remaining_label()
    update_history_table()
    update_label_periodically()
    event_handler = EnvFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()


def create_historique_table():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Historique (
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
        messagebox.showerror("Error", f"An error occurred while creating the 'Historique' table: {str(e)}")


def data_sent_email():
    try:
        conn = sqlite3.connect(database_path)
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
            base = {
                'server': server,
                'database': name,
                'username': username,
                'password': password
            }

            df = execute_sql_query(base)
            filename = export_to_excel(df=df, objet=name)
            objet = get_env_variable(config, 'MAIL', 'OBJET_MAIL')
            message = get_env_variable(config, 'MAIL', 'MESSAGE_MAIL')
            send_email_with_attachment(data=name, filename=filename, objet_mail=objet,
                                       message_mail=message, recipients=email, smtp=smtp,
                                       local_db=database_path)

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


def update_history_table():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch data from the 'Historique' table in descending order based on 'date' and 'time'
        cursor.execute("""
            SELECT date, time, email, data, status FROM Historique
            ORDER BY date DESC, time DESC
        """)
        rows = cursor.fetchall()

        history_tree.delete(*history_tree.get_children())

        for row in rows:
            # Rearrange the order of data to match the column order (Date, Heure, Email, Donnée)
            data_in_order = [row[0], row[1], row[2], row[3], row[4]]
            history_tree.insert("", "end", values=data_in_order)

        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error",
                             f"An error occurred while fetching data from the 'Historique' table: {str(e)}")


def update_label_periodically():
    # Update the configuration from environment variables
    update_config_from_env()

    # Update the time remaining label
    update_time_remaining_label()

    # Update the history table
    update_history_table()

    # Update the label periodically
    window.after(1000, update_label_periodically)


def update_time_remaining_label():
    heur_rappel = calculate_time_remaining()
    if heur_rappel.days == 0 and heur_rappel.seconds == 0:
        next_month_day = calculate_next_month_day()
        query_thread()
        time_until_next_month_day = next_month_day - datetime.datetime.now()
        seconds_remaining = time_until_next_month_day.total_seconds()
    else:
        seconds_remaining = heur_rappel.total_seconds()

    days = int(seconds_remaining // (24 * 3600))
    seconds_remaining %= (24 * 3600)
    hours = int(seconds_remaining // 3600)
    seconds_remaining %= 3600
    minutes = int(seconds_remaining // 60)
    seconds = int(seconds_remaining % 60)

    # Format the time as a string
    formatted_time = format_time(days, hours, minutes, seconds)
    time_remaining_var.set(formatted_time)


def get_unique_dates():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM Historique ORDER BY date DESC")
        dates = cursor.fetchall()
        conn.close()
        return [date[0] for date in dates]
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while fetching unique dates: {str(e)}")
        return []


def query_thread():
    query = threading.Thread(target=execute_script, args=())
    query.start()


