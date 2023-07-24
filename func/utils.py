import calendar
import datetime
import os
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Créer un objet ConfigParser
config = configparser.ConfigParser()

# Charger les valeurs du fichier .env dans le ConfigParser
config.read('.env')

# Récupérer les valeurs des variables d'environnement à partir de ConfigParser
smtp_username = config.get('DEFAULT', 'smtp_username')
smtp_password = config.get('DEFAULT', 'smtp_password')
smtp_serveur = config.get('DEFAULT', 'smtp_serveur')
smtp_port = config.get('DEFAULT', 'smtp_port')
recipient = config.get('USER', 'recipient')
database_name = config.get('LOCAL', 'database_name')
set_hour = int(config.get('SETTINGS', 'set_hour'))
set_minute = int(config.get('SETTINGS', 'set_minute'))
set_second = int(config.get('SETTINGS', 'set_second'))
set_microsecond = int(config.get('SETTINGS', 'set_microsecond'))
set_day = int(config.get('SETTINGS', 'set_day'))

def now():
    return datetime.datetime.now()


def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


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
        if event.src_path.endswith('.env'):
            # Re-charger les valeurs du fichier .env
            config.read('.env')

            # Mise à jour des valeurs des variables d'environnement
            global smtp_username, smtp_password, smtp_serveur, smtp_port
            global recipient, database_name, set_hour, set_minute, set_second, set_microsecond, set_day

            smtp_username = config.get('DEFAULT', 'smtp_username')
            smtp_password = config.get('DEFAULT', 'smtp_password')
            smtp_serveur = config.get('DEFAULT', 'smtp_serveur')
            smtp_port = config.get('DEFAULT', 'smtp_port')
            recipient = config.get('USER', 'recipient')
            database_name = config.get('LOCAL', 'database_name')
            set_hour = int(config.get('SETTINGS', 'set_hour'))
            set_minute = int(config.get('SETTINGS', 'set_minute'))
            set_second = int(config.get('SETTINGS', 'set_second'))
            set_microsecond = int(config.get('SETTINGS', 'set_microsecond'))
            set_day = int(config.get('SETTINGS', 'set_day'))


# Fonction pour démarrer la surveillance du fichier .env
def watch_env_file():
    event_handler = EnvFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()


# Appeler la fonction pour démarrer la surveillance du fichier .env
watch_env_file()
