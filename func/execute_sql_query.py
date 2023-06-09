import pandas as pd
import pyodbc
import configparser

# Chemin du fichier .env
env_file = '.env'

# Créer un objet ConfigParser
config = configparser.ConfigParser()

# Lire les variables d'environnement à partir du fichier .env
config.read(env_file)


def execute_sql_query():
    # Informations de connexion
    server = config.get('SERVER', 'SERVER_CONNEXION')
    database = config.get('SERVER', 'DATABASE_CONNEXION')
    username = config.get('SERVER', 'USER_CONNEXION')
    password = config.get('SERVER', 'PASS_CONNEXION')

    # Chaîne de connexion
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Connexion à la base de données
    connection = pyodbc.connect(conn_str)

    if connection:
        print('Connecté à la base de données')

    query = """
        SELECT F_ECRITUREC.CT_NUM, CT_INTITULE, 
        SUM(CASE WHEN EC_SENS=0 THEN EC_MONTANT ELSE -EC_MONTANT END) 
        AS SUMS FROM F_ECRITUREC INNER JOIN F_COMPTET ON F_ECRITUREC.CT_NUM=F_COMPTET.CT_NUM 
        GROUP BY F_ECRITUREC.CT_NUM, CT_INTITULE
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        print("Rows: ", rows)  # Afficher les valeurs récupérées depuis la base de données

        if rows:
            # Convertir les objets pyodbc.Row en tuples
            rows = [tuple(row) for row in rows]

            # Vérifier la structure des données
            data_types = [type(row) for row in rows]
            print("Data Type: ", data_types)

            if all(isinstance(row, tuple) for row in rows):
                df = pd.DataFrame(rows, columns=["CT_NUM", "CT_INTITULE", "SUMS"])
                print("DF: ", df)  # Afficher le DataFrame pour vérification
            else:
                print("Les valeurs récupérées ne sont pas au format attendu.")

    connection.close()

    return df
