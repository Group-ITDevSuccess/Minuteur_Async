import sqlite3


def data_sent_email():
    conn = sqlite3.connect('./DB_TEST.sqlite3')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Societes.name, Societes.server, Societes.username, Societes.password, Emails.email
        FROM EmailSociete
        INNER JOIN Societes ON EmailSociete.id_societe = Societes.id
        INNER JOIN Emails ON EmailSociete.id_email = Emails.id
    """)
    rows = cursor.fetchall()
    print(rows)

    for row in rows:
        # Traitez chaque ligne de données ici
        name, server, username, password, email = row
        print()
        print("----------------------")
        print("Société Name:", name)
        print("Société Server:", server)
        print("Société Username:", username)
        print("Société Password:", password)
        print("Email:", email)
        print("----------------------")
        print()

    cursor.close()
    conn.close()

    return rows

data_sent_email()