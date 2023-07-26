import calendar
import datetime
import configparser
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# Function to read the config.ini file and return the configparser object
def read_config():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    config.read(config_file)
    return config


# Function to write the config object back to the config.ini file
def write_config(config):
    config_file = 'config.ini'
    with open(config_file, 'w') as configfile:
        config.write(configfile)


# Function to get environment variable from the config.ini file
def get_env_variable(config, section, key):
    # Check if the section and key exist
    if section in config and key in config[section]:
        return config[section][key]
    return None


# Function to update the config from environment variables
def update_config_from_env():
    config = read_config()

    # Define the sections and keys to update from environment variables
    sections_and_keys = [
        ('DEFAULT', 'SMTP_USERNAME'),
        ('DEFAULT', 'SMTP_PASSWORD'),
        ('DEFAULT', 'SMTP_SERVEUR'),
        ('DEFAULT', 'SMTP_PORT'),
        ('LOCAL', 'RECIPIENT'),
        ('LOCAL', 'DATABASE_NAME'),
        ('SETTINGS', 'SET_HOUR'),
        ('SETTINGS', 'SET_MINUTE'),
        ('SETTINGS', 'SET_SECOND'),
        ('SETTINGS', 'SET_MICROSECOND'),
        ('SETTINGS', 'SET_DAY'),
    ]

    for section, key in sections_and_keys:
        env_value = os.getenv(key)
        if env_value is not None:
            config[section][key] = env_value

    write_config(config)


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
    config = read_config()
    set_hour = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_HOUR'))
    set_minute = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_MINUTE'))
    set_second = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_SECOND'))
    set_microsecond = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_MICROSECOND'))
    set_day = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_DAY'))

    if None in (set_hour, set_minute, set_second, set_microsecond, set_day):
        return None

    date_heur_actuel = now()

    date_heur_prochaine = date_heur_actuel.replace(
        day=set_day,
        hour=set_hour,
        minute=set_minute,
        second=set_second,
        microsecond=set_microsecond
    )

    if date_heur_actuel > date_heur_prochaine:
        mois_suivant = date_heur_actuel.month + 1

        if mois_suivant > 12:
            mois_suivant = 1
            year_actuel = date_heur_actuel.year + 1
        else:
            year_actuel = date_heur_actuel.year

        jours_dans_mois_suivant = get_days_in_month(year_actuel, mois_suivant)

        if set_day <= jours_dans_mois_suivant:
            date_heur_prochaine = date_heur_prochaine.replace(month=mois_suivant, year=year_actuel)
        else:
            date_heur_prochaine = date_heur_prochaine.replace(day=1, month=mois_suivant, year=year_actuel)

    time_remaining = date_heur_prochaine - date_heur_actuel
    return time_remaining


def calculate_next_month_day():
    config = read_config()
    set_day = validate_integer(get_env_variable(config, 'SETTINGS', 'SET_DAY'))
    if set_day is None:
        return None

    date_heur_actuel = now()
    date_heur_prochaine = date_heur_actuel.replace(day=set_day)
    date_heur_prochaine += datetime.timedelta(days=1)

    while date_heur_prochaine.day != set_day:
        mois_suivant = date_heur_prochaine.month + 1
        if mois_suivant > 12:
            mois_suivant = 1
            year_actuel = date_heur_prochaine.year + 1
        else:
            year_actuel = date_heur_prochaine.year

        jours_dans_mois_suivant = get_days_in_month(year_actuel, mois_suivant)
        if set_day <= jours_dans_mois_suivant:
            date_heur_prochaine = date_heur_prochaine.replace(day=set_day, month=mois_suivant, year=year_actuel)
        else:
            date_heur_prochaine = date_heur_prochaine.replace(day=1, month=mois_suivant, year=year_actuel)

    return date_heur_prochaine


class EnvFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == 'config.ini':
            # Re-load the environment variables from the config.ini file
            update_config_from_env()


def watch_env_file():
    event_handler = EnvFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    # Update the configuration from environment variables at startup
    update_config_from_env()

    # Call the function calculate_time_remaining here or at the appropriate place
    calculate_time_remaining()