import datetime


def calculate_time_remaining():
    date_heur_actuel = datetime.datetime.now()
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel.replace(hour=23, minute=59, second=59, microsecond=0)

    if date_heur_actuel >= date_heur_prochaine:
        jours += 7

    date_heur_prochaine += datetime.timedelta(days=jours)

    heur_rappel = date_heur_prochaine - date_heur_actuel
    return heur_rappel
