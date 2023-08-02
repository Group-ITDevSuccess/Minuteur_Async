import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
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
            copy = get_env_variable(config, 'MAIL', 'COPY')
            send_email_with_attachment(data=name, filename=filename, objet_mail=objet,
                                       message_mail=message, recipients=email, smtp=smtp,
                                       local_db=database_path, copy=copy)

            # Update the history table
            update_history_table()

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
    if minutes % 5 == 0:
        # Update the history table
        update_history_table()
    return f"{days} jours, {hours:02d} heures, {minutes:02d} minutes, {seconds:02d} secondes"


def update_history_table():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch data from the 'Historique' table in descending order based on 'date' and 'time'
        cursor.execute("""
            SELECT date, time, email, objet, message, data, status FROM Historique
            ORDER BY date DESC, time DESC
        """)
        rows = cursor.fetchall()

        history_tree.delete(*history_tree.get_children())

        for row in rows:
            # Rearrange the order of data to match the column order (Date, Heure, Email, Donnée)
            data_in_order = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
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


def update_config():
    def save_config():
        # Get the values from the entry fields
        smtp_serveur = smtp_serveur_entry.get()
        smtp_username = smtp_username_entry.get()
        smtp_password = smtp_password_entry.get()
        smtp_port = smtp_port_entry.get()
        set_hour = set_hour_entry.get()
        set_minute = set_minute_entry.get()
        set_second = set_second_entry.get()
        set_microsecond = set_microsecond_entry.get()
        set_day = set_day_entry.get()
        database_name = database_name_entry.get()
        objet_mail = objet_mail_entry.get()
        message_mail = message_mail_entry.get()
        copy_mail = copy_mail_entry.get()

        # Update the config object with the new values
        config['DEFAULT']['smtp_serveur'] = smtp_serveur
        config['DEFAULT']['smtp_username'] = smtp_username
        config['DEFAULT']['smtp_password'] = smtp_password
        config['DEFAULT']['smtp_port'] = smtp_port
        config['SETTINGS']['set_hour'] = set_hour
        config['SETTINGS']['set_minute'] = set_minute
        config['SETTINGS']['set_second'] = set_second
        config['SETTINGS']['set_microsecond'] = set_microsecond
        config['SETTINGS']['set_day'] = set_day
        config['LOCAL']['database_name'] = database_name
        config['MAIL']['objet_mail'] = objet_mail
        config['MAIL']['message_mail'] = message_mail
        config['MAIL']['copy'] = copy_mail

        # Save the new values in the config.ini file
        with open(config_file, 'w') as configfile:
            config.write(configfile)

        messagebox.showinfo("Success", "Configurations saved successfully.")
        config_popup.destroy()

    # Create the popup window
    config_popup = tk.Toplevel()
    config_popup.title("Modifier les configurations")

    # Function to create entry fields
    def create_entry(parent, label_text, default_value, row):
        label = ttk.Label(parent, text=label_text)
        entry = ttk.Entry(parent)
        entry.insert(tk.END, default_value)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    # Create a frame to hold the configuration widgets
    config_frame = ttk.Frame(config_popup, padding=20)
    config_frame.grid(row=0, column=0, sticky="nsew")

    # Make the rows and columns in the frame expandable
    config_frame.columnconfigure(0, weight=1)
    config_frame.rowconfigure(0, weight=1)

    # Entry fields for [DEFAULT] section
    default_label_frame = ttk.LabelFrame(config_frame, text="DEFAULT")
    default_label_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    smtp_serveur_entry = create_entry(default_label_frame, "SMTP Serveur", config['DEFAULT']['smtp_serveur'], 0)
    smtp_username_entry = create_entry(default_label_frame, "SMTP Username", config['DEFAULT']['smtp_username'], 1)
    smtp_password_entry = create_entry(default_label_frame, "SMTP Password", config['DEFAULT']['smtp_password'], 2)
    smtp_port_entry = create_entry(default_label_frame, "SMTP Port", config['DEFAULT']['smtp_port'], 3)

    # Entry fields for [SETTINGS] section
    settings_label_frame = ttk.LabelFrame(config_frame, text="SETTINGS")
    settings_label_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    set_hour_entry = create_entry(settings_label_frame, "Set Hour", config['SETTINGS']['set_hour'], 0)
    set_minute_entry = create_entry(settings_label_frame, "Set Minute", config['SETTINGS']['set_minute'], 1)
    set_second_entry = create_entry(settings_label_frame, "Set Second", config['SETTINGS']['set_second'], 2)
    set_microsecond_entry = create_entry(settings_label_frame, "Set Microsecond", config['SETTINGS']['set_microsecond'], 3)
    set_day_entry = create_entry(settings_label_frame, "Set Day", config['SETTINGS']['set_day'], 4)

    # Entry fields for [LOCAL] section
    local_label_frame = ttk.LabelFrame(config_frame, text="LOCAL")
    local_label_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    database_name_entry = create_entry(local_label_frame, "Database Name", config['LOCAL']['database_name'], 0)

    # Entry fields for [MAIL] section
    mail_label_frame = ttk.LabelFrame(config_frame, text="MAIL")
    mail_label_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    objet_mail_entry = create_entry(mail_label_frame, "Objet Mail", config['MAIL']['objet_mail'], 0)
    message_mail_entry = create_entry(mail_label_frame, "Message Mail", config['MAIL']['message_mail'], 1)
    copy_mail_entry = create_entry(mail_label_frame, "Copy Mail", config['MAIL']['copy'], 2)

    # Create a save button to save the changes
    save_button = ttk.Button(config_frame, text="Enregistrer", command=save_config)
    save_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

    # Make the "Enregistrer" button align to the bottom of the frame
    config_frame.rowconfigure(4, weight=1)

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Programme d'envoi de données")
    window.geometry("800x600")  # Increase the window height to accommodate the additional widgets

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

    # Create a frame for the header
    header_frame = ttk.Frame(window)
    header_frame.pack(fill=tk.X, pady=10)

    # Load your company logo and add it to the header
    logo_img = Image.open("logo-inviso.ico")  # Replace "path_to_your_logo.png" with the path to your logo
    logo_img = logo_img.resize((70, 70), Image.LANCZOS)  # Resize the logo as needed
    logo_img = ImageTk.PhotoImage(logo_img)

    # Create a StringVar to hold the formatted time for the countdown
    time_remaining_var = tk.StringVar()

    # Create the colored label using the 'Custom.TLabel.Colored' style for the timer section
    time_remaining_label = ttk.Label(window, textvariable=time_remaining_var, font=('Courier', 48),
                                     style='Custom.TLabel.Colored')
    time_remaining_label.pack(pady=10)

    logo_label = ttk.Label(header_frame, image=logo_img)
    logo_label.pack(side=tk.LEFT, padx=10)

    # Create a separator line for visual separation
    separator = ttk.Separator(header_frame, orient=tk.VERTICAL)
    separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

    # Create a frame to hold the "Execute" and "Config" buttons
    buttons_frame = ttk.Frame(header_frame)
    buttons_frame.pack(side=tk.RIGHT, padx=10)

    # Load the icons for buttons
    execute_icon_img = Image.open("execute_icon.png")  # Replace with the path to your execute icon
    execute_icon_img = execute_icon_img.resize((30, 30), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
    execute_icon = ImageTk.PhotoImage(execute_icon_img)

    config_icon_img = Image.open("config_icon.png")  # Replace with the path to your config icon
    config_icon_img = config_icon_img.resize((30, 30), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
    config_icon = ImageTk.PhotoImage(config_icon_img)

    # Bouton pour exécuter le script
    execute_button = ttk.Button(buttons_frame, command=query_thread, image=execute_icon, style='Custom.TButton')
    execute_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Create a "Config" button to modify the configurations
    config_button = ttk.Button(buttons_frame, command=update_config, image=config_icon, style='Custom.TButton')
    config_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Create the colored label using the 'Custom.TLabel.Colored' style for the timer section
    time_remaining_label = ttk.Label(window, text="Envoi de Mail Automatique", font=('Helvetica', 20),
                                     style='Custom.TLabel.Colored')
    time_remaining_label.pack(pady=10)

    # Create a Treeview widget to display the history table
    history_tree = ttk.Treeview(window, columns=("Date", "Heure", "Email", "Objet", "Message", "Donnée", "Statut"),
                                show="headings", style='Custom.Treeview')
    history_tree.heading("Date", text="Date", anchor=tk.CENTER)
    history_tree.heading("Heure", text="Heure", anchor=tk.CENTER)
    history_tree.heading("Email", text="Email", anchor=tk.CENTER)
    history_tree.heading("Objet", text="Objet", anchor=tk.CENTER)
    history_tree.heading("Message", text="Message", anchor=tk.CENTER)
    history_tree.heading("Donnée", text="Donnée", anchor=tk.CENTER)
    history_tree.heading("Statut", text="Statut", anchor=tk.CENTER)

    # Add a vertical scrollbar to the right of the table
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=history_tree.yview)
    history_tree.configure(yscrollcommand=scrollbar.set)

    history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Use pack for the scrollbar

    # Set a custom background color for the window
    window.configure(bg='#f0f0f0')

    # Call the function to update the label and history table periodically
    update_label_periodically()

    get_unique_dates()

    # Start the tkinter main loop
    window.mainloop()
