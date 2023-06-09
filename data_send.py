import sqlite3

def data_sent_email():

    conn = sqlite3.connect('./DB_TEST.sqlite3')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Societes.name, Emails.email
        FROM EmailSociete
        INNER JOIN Societes ON EmailSociete.id_societe = Societes.id
        INNER JOIN Emails ON EmailSociete.id_email = Emails.id
    """)
    rows = cursor.fetchall()

    for row in rows:
        # Traitez chaque ligne de données ici
        societe_name, email = row
        print("Société:", societe_name)
        print("Email:", email)
        print("----------------------")
        print()

    cursor.close()
    conn.close()

    return rows
