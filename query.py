import sqlite3

# Les données du fichier .env
data = {
    "DEFAULT": {
        "smtp_username": "muriel.raharison@inviso-group.com",
        "smtp_password": "DzczeHgosm",
        "smtp_serveur": "mail.inviso-group.com",
        "smtp_port": "587"
    },
    "LOCAL": {
        "database_name": "DB_TEST.sqlite3"
    },
    "SETTINGS": {
        "set_hour": "10",
        "set_minute": "30",
        "set_second": "45",
        "set_microsecond": "0",
        "set_day": "25"
    },
    "MAIL": {
        "objet": "Mon Mail Objet",
        "message": "Mon Message"
    }
}


# Fonction pour créer la table si elle n'existe pas et insérer les données dans la table SQLite
def create_and_insert_data_into_table(data):
    with sqlite3.connect("env_data.db") as conn:
        cursor = conn.cursor()

        # Créer la table si elle n'existe pas
        cursor.execute('''CREATE TABLE IF NOT EXISTS env_data (
                            id INTEGER PRIMARY KEY,
                            type TEXT NOT NULL,
                            key TEXT NOT NULL,
                            value TEXT NOT NULL
                          )''')

        for env_type, env_data in data.items():
            for key, value in env_data.items():
                cursor.execute("INSERT INTO env_data (type, key, value) VALUES (?, ?, ?)",
                               (env_type, key, value))

        conn.commit()


# Appel de la fonction pour créer la table et insérer les données
create_and_insert_data_into_table(data)
