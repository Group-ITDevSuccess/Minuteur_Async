import datetime
import tkinter as tk

# from tkinter import messagebox

from func.calculate_next_thursday import calculate_next_thursday
from func.calculate_time_remaining import calculate_time_remaining
from func.execute_sql_query import execute_sql_query
from func.export_to_excel import export_to_excel
from func.send_email_with_attachment import send_email_with_attachment


def execute_script():
    df = execute_sql_query()
    filename = export_to_excel(df)
    recipient = "sage@inviso-group.com"
    send_email_with_attachment(filename, recipient)
    # messagebox.showinfo(
    #     "Succès", "Les données ont été envoyées par e-mail à " + recipient)
    update_time_remaining_label()

def update_label_periodically():
    update_time_remaining_label()
    window.after(1000, update_label_periodically)

def update_time_remaining_label():
    heur_rappel = calculate_time_remaining()
    if heur_rappel.days == 0 and heur_rappel.seconds == 0:
        next_thursday = calculate_next_thursday()
        execute_script()
        time_until_next_thursday = next_thursday - datetime.datetime.now()
        time_remaining_label["text"] = "Prochain compte à rebours avant le prochain envoi (Jeudi suivant) : " + \
                                       str(time_until_next_thursday.days) + " jours, " + \
                                       str(time_until_next_thursday.seconds // 3600) + " heures, " + \
                                       str((time_until_next_thursday.seconds // 60) % 60) + " minutes, " + \
                                       str(time_until_next_thursday.seconds %
                                           60) + " secondes"
    else:
        time_remaining_label["text"] = "Temps restant jusqu'au prochain envoi : " + str(heur_rappel.days) + " jours, " + \
                                       str(heur_rappel.seconds // 3600) + " heures, " + \
                                       str((heur_rappel.seconds // 60) % 60) + " minutes, " + \
                                       str(heur_rappel.seconds %
                                           60) + " secondes"



window = tk.Tk()
window.title("Programme d'envoi de données")

time_remaining_label = tk.Label(window, text="")
time_remaining_label.pack()



update_label_periodically()

execute_button = tk.Button(
    window, text="Exécuter le script", command=execute_script)
execute_button.pack()

window.mainloop()
