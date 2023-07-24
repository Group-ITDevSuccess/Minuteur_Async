import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import threading
from datetime import datetime
import configparser
import os  # Import the os module to get the path of the script directory

from func.utils import calculate_next_month_day, calculate_time_remaining, EnvFileHandler
from func.execute_query import execute_sql_query
from func.export_to_excel import export_to_excel
from func.send_email import send_email_with_attachment
from data_send import data_sent_email
from dotenv import load_dotenv

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
database_name = config.get('LOCAL', 'DATABASE_NAME')

database_path = os.path.join(os.path.dirname(__file__), database_name)

smtp = {'server': server_default,
        'username': username_default,
        'password': password_default,
        'port': port_default
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
            recipient = email

            df = execute_sql_query(base)
            filename = export_to_excel(df=df, objet=name)
            send_email_with_attachment(objet=name, filename=filename, recipients=recipient, smtp=smtp,
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
    window.after(1000, watch_env_file)

    # window.after(2000, update_history_table)  # Update every 1 seconds


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


def update_config():
    # Create the popup window
    config_popup = tk.Toplevel(window)
    config_popup.title("Modifier les configurations")
    config_popup.geometry("400x400")
    config_popup.resizable(False, False)

    # Create a frame for all the configuration widgets
    config_frame = ttk.Frame(config_popup, padding=20)
    config_frame.pack(fill=tk.BOTH, expand=True)

    # Create labels and entry fields to display and modify the config data
    server_label = ttk.Label(config_frame, text="SMTP Serveur:")
    server_entry = ttk.Entry(config_frame)
    server_entry.insert(tk.END, smtp['server'])

    username_label = ttk.Label(config_frame, text="SMTP Username:")
    username_entry = ttk.Entry(config_frame)
    username_entry.insert(tk.END, smtp['username'])

    password_label = ttk.Label(config_frame, text="SMTP Password:")
    password_entry = ttk.Entry(config_frame, show="*")
    password_entry.insert(tk.END, smtp['password'])

    port_label = ttk.Label(config_frame, text="SMTP Port:")
    port_entry = ttk.Entry(config_frame)
    port_entry.insert(tk.END, smtp['port'])

    # Entry fields for [SETTINGS] section
    set_hour_label = ttk.Label(config_frame, text="Heure:")
    set_hour_entry = ttk.Entry(config_frame)
    set_hour_entry.insert(tk.END, config.get('SETTINGS', 'set_hour'))

    set_minute_label = ttk.Label(config_frame, text="Minute:")
    set_minute_entry = ttk.Entry(config_frame)
    set_minute_entry.insert(tk.END, config.get('SETTINGS', 'set_minute'))

    set_second_label = ttk.Label(config_frame, text="Seconde:")
    set_second_entry = ttk.Entry(config_frame)
    set_second_entry.insert(tk.END, config.get('SETTINGS', 'set_second'))

    set_microsecond_label = ttk.Label(config_frame, text="Microseconde:")
    set_microsecond_entry = ttk.Entry(config_frame)
    set_microsecond_entry.insert(tk.END, config.get('SETTINGS', 'set_microsecond'))

    set_day_label = ttk.Label(config_frame, text="Jour:")
    set_day_entry = ttk.Entry(config_frame)
    set_day_entry.insert(tk.END, config.get('SETTINGS', 'set_day'))

    # Entry fields for [USER] section
    recipient_label = ttk.Label(config_frame, text="Recipient:")
    recipient_entry = ttk.Entry(config_frame)
    recipient_entry.insert(tk.END, config.get('USER', 'RECIPIENT'))

    # Entry fields for [LOCAL] section
    database_name_label = ttk.Label(config_frame, text="Nom de la base de données:")
    database_name_entry = ttk.Entry(config_frame)
    database_name_entry.insert(tk.END, config.get('LOCAL', 'DATABASE_NAME'))

    # Function to save the modified data to the .env file
    def save_config():
        try:
            config.set('DEFAULT', 'SMTP_SERVEUR', server_entry.get())
            config.set('DEFAULT', 'SMTP_USERNAME', username_entry.get())
            config.set('DEFAULT', 'SMTP_PASSWORD', password_entry.get())
            config.set('DEFAULT', 'SMTP_PORT', port_entry.get())

            # Save the new settings in the [SETTINGS] section
            config.set('SETTINGS', 'set_hour', set_hour_entry.get())
            config.set('SETTINGS', 'set_minute', set_minute_entry.get())
            config.set('SETTINGS', 'set_second', set_second_entry.get())
            config.set('SETTINGS', 'set_microsecond', set_microsecond_entry.get())
            config.set('SETTINGS', 'set_day', set_day_entry.get())

            # Save the new recipient in the [USER] section
            config.set('USER', 'RECIPIENT', recipient_entry.get())

            # Save the new database name in the [LOCAL] section
            config.set('LOCAL', 'DATABASE_NAME', database_name_entry.get())

            with open(env_file, 'w') as configfile:
                config.write(configfile)

            # Mettez à jour toutes les données après avoir sauvegardé les configurations
            refresh_all_data()

            config_popup.destroy()  # Close the popup after saving
            messagebox.showinfo("Success", "Configurations saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving configurations: {str(e)}")

    # Create a save button to save the changes
    save_button = ttk.Button(config_frame, text="Enregistrer", command=save_config)

    # Grid layout for the popup widgets
    server_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    server_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    username_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    password_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    port_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    port_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    # Grid layout for the [SETTINGS] section
    set_hour_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
    set_hour_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    set_minute_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    set_minute_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

    set_second_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
    set_second_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

    set_microsecond_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
    set_microsecond_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

    set_day_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
    set_day_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

    # Grid layout for the [USER] section
    recipient_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
    recipient_entry.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

    # Grid layout for the [LOCAL] section
    database_name_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")
    database_name_entry.grid(row=10, column=1, padx=10, pady=5, sticky="ew")

    save_button.grid(row=11, column=0, columnspan=2, pady=10)


def refresh_all_data():
    # Mettez à jour toutes les données nécessaires à partir du fichier .env
    load_dotenv()

    global set_hour, set_minute, set_second, set_microsecond, set_day

    set_hour = int(os.getenv("SET_HOUR", 11))
    set_minute = int(os.getenv("SET_MINUTE", 30))
    set_second = int(os.getenv("SET_SECOND", 0))
    set_microsecond = int(os.getenv("SET_MICROSECOND", 0))
    set_day = int(os.getenv("SET_DAY", 25))

    # Vous pouvez également mettre à jour d'autres données à partir du fichier .env si nécessaire

    window.after(1000, calculate_time_remaining)
    window.after(1000, calculate_next_month_day)
    window.after(1000, update_time_remaining_label)
    window.after(1000, update_history_table)


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

    # Create a "Config" button to modify the configurations
    config_button = ttk.Button(content_frame, text="Configuration", command=update_config, style='Custom.TButton')
    config_button.pack(pady=10)

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
