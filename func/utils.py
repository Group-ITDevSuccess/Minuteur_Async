import datetime


def now():
    return datetime.datetime.now()


def calculate_time_remaining():
    date_heur_actuel = now()
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel.replace(hour=11, minute=24, second=0, microsecond=0)

    if date_heur_actuel >= date_heur_prochaine:
        jours += 7

    date_heur_prochaine += datetime.timedelta(days=jours)

    heur_rappel = date_heur_prochaine - date_heur_actuel
    return heur_rappel


def calculate_next_thursday():
    date_heur_actuel = now()
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel + datetime.timedelta(days=jours)
    date_heur_prochaine = date_heur_prochaine.replace(hour=11, minute=24, second=0, microsecond=0)
    return date_heur_prochaine
