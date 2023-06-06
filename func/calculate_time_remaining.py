import datetime

def calculate_time_remaining():
    date_heur_actuel = datetime.datetime.now()
    date_heur_prochaine = date_heur_actuel.replace(hour=9, minute=47, second=0, microsecond=0)
    jours = (1 - date_heur_actuel.weekday() + 7) % 7
  
    if date_heur_actuel >= date_heur_prochaine:
        jours += 7

    date_heur_prochaine += datetime.timedelta(days=jours)
    heur_rappel = date_heur_prochaine - date_heur_actuel
    return heur_rappel
