import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import threading
from datetime import datetime
import configparser
import os  # Import the os module to get the path of the script directory

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


def update_history_table():
    try:
        conn = sqlite3.connect('./DB_TEST.sqlite3')
        cursor = conn.cursor()

        # Fetch data from the 'historique' table in descending order based on 'date' and 'time'
        cursor.execute("""
            SELECT date, time, email, data, status FROM historique
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
                             f"An error occurred while fetching data from the 'historique' table: {str(e)}")


def update_label_periodically():
    update_time_remaining_label()
    window.after(1000, update_label_periodically)
    window.after(1500, update_history_table)  # Update every 1 seconds


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


def get_unique_dates():
    try:
        conn = sqlite3.connect('./DB_TEST.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM historique ORDER BY date DESC")
        dates = cursor.fetchall()
        conn.close()
        return [date[0] for date in dates]
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while fetching unique dates: {str(e)}")
        return []


def filter_by_date():
    selected_date = date_combobox.get()
    if selected_date:
        history_tree.delete(*history_tree.get_children())
        try:
            conn = sqlite3.connect('./DB_TEST.sqlite3')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM historique WHERE date=?", (selected_date,))
            rows = cursor.fetchall()
            for row in rows:
                history_tree.insert("", "end", values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred while fetching data for the selected date: {str(e)}")
        update_history_table()  # Update the history table after filtering


def query_thread():
    query = threading.Thread(target=execute_script, args=())
    query.start()


def set_window_icon(window, icon_path):
    if os.path.exists(icon_path):
        window.iconbitmap(icon_path)


if __name__ == "__main__":
    window = tk.Tk()
    window.title("Programme d'envoi de données")
    window.geometry("800x500")  # Set a default window size

    # Set a custom style for widgets
    style = ttk.Style()
    style.configure('Custom.TLabel', font=('Helvetica', 20), padding=10)
    style.configure('Custom.TButton', font=('Helvetica', 16), padding=10)
    style.configure('Custom.Treeview', font=('Helvetica', 12))
    style.configure('Custom.Treeview.Heading', font=('Helvetica', 14, 'bold'), background='#dcdcdc', foreground='black')
    style.configure('Custom.Treeview', background='#f0f0f0')  # Set Treeview background color

    # Define the layout for the 'Custom.TLabel.Colored' style
    style.layout('Custom.TLabel.Colored',
                 [('Label.border', {'sticky': 'nswe', 'children':
                     [('Label.padding', {'sticky': 'nswe', 'children':
                         [('Label.label', {'sticky': 'nswe'})],
                                         'border': '2'})],
                                    'border': '2'})])

    content_frame = ttk.Frame(window, padding=20)
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Create the colored label using the 'Custom.TLabel.Colored' style
    time_remaining_label = ttk.Label(content_frame, text="Envoi de Mail Automatique", font=('Helvetica', 20),
                                     style='Custom.TLabel.Colored')
    time_remaining_label.pack(pady=10)

    # Bouton pour exécuter le script
    execute_button = ttk.Button(content_frame, text="Exécuter le script", command=query_thread, style='Custom.TButton')
    execute_button.pack(pady=10)

    # Create a Combobox widget to select dates
    date_combobox = ttk.Combobox(content_frame, values=get_unique_dates(), state="readonly")
    date_combobox.bind("<<ComboboxSelected>>", lambda event: filter_by_date())
    date_combobox.pack(pady=10)

    # Create a Treeview widget to display the history table
    history_tree = ttk.Treeview(content_frame, columns=("Date", "Heure", "Email", "Donnée", "Statut"), show="headings",
                                style='Custom.Treeview')
    history_tree.heading("Date", text="Date", anchor=tk.CENTER)
    history_tree.heading("Heure", text="Heure", anchor=tk.CENTER)
    history_tree.heading("Email", text="Email", anchor=tk.CENTER)
    history_tree.heading("Donnée", text="Donnée", anchor=tk.CENTER)
    history_tree.heading("Statut", text="Statut", anchor=tk.CENTER)

    # Add a vertical scrollbar to the right of the table
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=history_tree.yview)
    history_tree.configure(yscrollcommand=scrollbar.set)

    history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    scrollbar.place(relx=1, rely=0, relheight=1)  # Place the scrollbar on the right side

    # Set a custom background color for the window
    window.configure(bg='#ffffff')

    # Set a window icon (change 'icon.ico' to the path of your icon file)
    # set_window_icon(window, 'logo-inviso.ico')

    # Call the function to update the label and history table periodically
    update_label_periodically()

    get_unique_dates()

    # Start the tkinter main loop
    window.mainloop()
