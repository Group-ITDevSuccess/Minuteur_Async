import datetime


def calculate_next_thursday():
    date_heur_actuel = datetime.datetime.now()
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel + datetime.timedelta(days=jours)
    date_heur_prochaine = date_heur_prochaine.replace(hour=23, minute=59, second=59, microsecond=0)
    return date_heur_prochaine

