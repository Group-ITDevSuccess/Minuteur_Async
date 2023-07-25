import calendar
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
import configparser

# Chemin du fichier config.ini
config_file = 'config.ini'

# Charger les variables d'environnement à partir du fichier config.ini
config = configparser.ConfigParser()
config.read(config_file)


def get_env_variable(key, default=None):
    return os.getenv(key, default)


def update_config_from_env():
    global smtp_username, smtp_password, smtp_serveur, smtp_port
    global recipient, database_name, set_hour, set_minute, set_second, set_microsecond, set_day

    smtp_username = config.get('DEFAULT', 'SMTP_USERNAME')
    smtp_password = config.get('DEFAULT', 'SMTP_PASSWORD')
    smtp_serveur = config.get('DEFAULT', 'SMTP_SERVEUR')
    smtp_port = config.getint('DEFAULT', 'SMTP_PORT')
    database_name = config.get('LOCAL', 'DATABASE_NAME')
    set_hour = config.getint('SETTINGS', 'SET_HOUR')
    set_minute = config.getint('SETTINGS', 'SET_MINUTE')
    set_second = config.getint('SETTINGS', 'SET_SECOND')
    set_microsecond = config.getint('SETTINGS', 'SET_MICROSECOND')
    set_day = config.getint('SETTINGS', 'SET_DAY')


def now():
    return datetime.datetime.now()


def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def validate_integer(value):
    try:
        return int(value)
    except ValueError:
        return None


def validate_string(value):
    if isinstance(value, str):
        return value.strip()
    return None


def calculate_time_remaining():
    date_heur_actuel = now()
    year_actuel = date_heur_actuel.year
    mois_actuel = date_heur_actuel.month
    jour_dans_mois_actuel = get_days_in_month(year_actuel, mois_actuel)
    date_heur_prochaine = date_heur_actuel.replace(day=set_day, hour=set_hour, minute=set_minute,
                                                   second=set_second, microsecond=set_microsecond)

    if date_heur_actuel > date_heur_prochaine:
        mois_suivant = mois_actuel + 1

        if mois_suivant > 12:
            mois_suivant = 1
            year_actuel += 1

        jours_dans_mois_suivant = get_days_in_month(year_actuel, mois_suivant)

        if set_day <= jours_dans_mois_suivant:
            date_heur_prochaine = date_heur_prochaine.replace(month=mois_suivant, year=year_actuel)
        else:
            date_heur_prochaine = date_heur_prochaine.replace(day=1, month=mois_suivant, year=year_actuel)

    time_remaining = date_heur_prochaine - date_heur_actuel
    return time_remaining


def calculate_next_month_day():
    date_heur_actuel = now()
    year_actuel = date_heur_actuel.year
    mois_actuel = date_heur_actuel.month
    jour_dans_mois_actuel = get_days_in_month(year_actuel, mois_actuel)

    # On calcule le jour suivant du 25 du mois actuel.
    date_heur_prochaine = date_heur_actuel.replace(day=set_day, hour=set_hour, minute=set_minute,
                                                   second=set_second, microsecond=set_microsecond)
    date_heur_prochaine += datetime.timedelta(days=1)

    # On avance au mois suivant en vérifiant si le jour 25 est valide dans ce mois.
    while date_heur_prochaine.day != set_day:
        mois_suivant = date_heur_prochaine.month + 1
        if mois_suivant > 12:
            mois_suivant = 1
            year_actuel += 1

        jours_dans_mois_suivant = get_days_in_month(year_actuel, mois_suivant)
        if set_day <= jours_dans_mois_suivant:
            date_heur_prochaine = date_heur_prochaine.replace(day=set_day, month=mois_suivant, year=year_actuel)
        else:
            date_heur_prochaine = date_heur_prochaine.replace(day=1, month=mois_suivant, year=year_actuel)

    return date_heur_prochaine


class EnvFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == config_file:
            # Re-load the environment variables from the config.ini file
            config.read(config_file)
            update_config_from_env()


def watch_env_file():
    event_handler = EnvFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()


# Update the configuration from the environment variables at the start
update_config_from_env()

# Call the function to start watching the .env file for changes
watch_env_file()
