import datetime


def calculate_next_thursday():
    date_heur_actuel = datetime.datetime.now()
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel + datetime.timedelta(days=jours)
    date_heur_prochaine = date_heur_prochaine.replace(hour=9, minute=0, second=0, microsecond=0)
    return date_heur_prochaine

