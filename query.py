import sqlite3
import os

database_path = os.path.join(os.path.dirname(__file__), 'DB_TEST.sqlite3')


def create_configuration_table():
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        # Create the 'Configuration' table with 'key' and 'value' columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Configuration (
                key_value TEXT PRIMARY KEY,
                valeur TEXT
            )
        """)

        # Insert the provided configuration values into the 'Configuration' table
        config_values = [
            ('smtp_username', 'muriel.raharison@inviso-group.com'),
            ('smtp_password', 'DzczeHgosm'),
            ('smtp_serveur', 'mail.inviso-group.com'),
            ('smtp_port', '587'),
            ('database_name', 'DB_TEST.sqlite3'),
            ('set_hour', '10'),
            ('set_minute', '30'),
            ('set_second', '45'),
            ('set_microsecond', '0'),
            ('set_day', '25'),
            ('objet', 'Mon Mail Objet'),
            ('message', 'Mon Message')
        ]

        cursor.executemany("INSERT OR REPLACE INTO Configuration (key_value, valeur) VALUES (?, ?)", config_values)

        conn.commit()


if __name__ == "__main__":
    create_configuration_table()
