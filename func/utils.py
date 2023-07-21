import calendar
import datetime

set_hour = 11
set_minute = 30
set_second = 00
set_microsecond = 0
set_day = 25


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


timer_remaining = calculate_time_remaining()
print(timer_remaining)
next_month = calculate_next_month_day()
print(next_month)
