import datetime

set_hour = 11
set_minute = 37
set_second = 00
set_microsecond = 0
set_day = 3


def now():
    return datetime.datetime.now()


def calculate_time_remaining():
    date_heur_actuel = now()
    jours = (set_day - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel.replace(hour=set_hour, minute=set_minute, second=set_second,
                                                   microsecond=set_microsecond)

    if date_heur_actuel >= date_heur_prochaine:
        jours += 7

    date_heur_prochaine += datetime.timedelta(days=jours)

    heur_rappel = date_heur_prochaine - date_heur_actuel
    return heur_rappel


def calculate_next_thursday():
    date_heur_actuel = now()
    jours = (set_day - date_heur_actuel.weekday() + 7) % 7
    date_heur_prochaine = date_heur_actuel + datetime.timedelta(days=jours)
    date_heur_prochaine = date_heur_prochaine.replace(hour=set_hour, minute=set_minute, second=set_second,
                                                      microsecond=set_microsecond)
    return date_heur_prochaine
