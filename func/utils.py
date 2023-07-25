import calendar
import datetime
import sqlite3
import os


def get_key(key, default_value=None):
    database_path = os.path.join(os.path.dirname(__file__), 'DB_TEST.sqlite3')
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        # Fetch the value of the key from the 'Configuration' table
        cursor.execute(f"SELECT * FROM Configuration WHERE key_value={key}")
        result = cursor.fetchone()

        if result:
            print(result[0])
            return result[0]
        else:
            # If the value is not found, return the default value or None
            return default_value


def update_config_from_env():
    global smtp_username, smtp_password, smtp_serveur, smtp_port, object_mail, message_mail
    global recipient, database_name, set_hour, set_minute, set_second, set_microsecond, set_day

    object_mail = str(get_key('objet'))
    message_mail = str(get_key('message'))
    smtp_username = str(get_key('smtp_username'))
    smtp_password = str(get_key('smtp_password'))
    smtp_serveur = str(get_key('smtp_serveur'))
    smtp_port = int(get_key('smtp_port'))
    recipient = str(get_key('recipient'))
    database_name = str(get_key('database_name'))
    set_hour = int(get_key('set_hour'))
    set_minute = int(get_key('set_minute'))
    set_second = int(get_key('set_second'))
    set_microsecond = int(get_key('set_microsecond'))
    set_day = int(get_key('set_day'))


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
