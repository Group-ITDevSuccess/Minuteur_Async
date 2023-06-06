import pandas as pd
import pyodbc

def execute_sql_query():
     # Informations de connexion
    server = '192.168.1.161'
    database = 'NMP'
    username = 'reader'
    password = 'm1234'

    # Chaîne de connexion
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Connexion à la base de données
    connection = pyodbc.connect(conn_str)

    if connection:
        print('Connecter au BD')

    query = """
        SELECT F_ECRITUREC.CT_NUM,CT_INTITULE, 
        SUM(CASE WHEN EC_SENS=0 THEN EC_MONTANT ELSE  -EC_MONTANT END) 
        AS SUMS  FROM F_ECRITUREC INNER JOIN F_COMPTET ON F_ECRITUREC.CT_NUM=F_COMPTET.CT_NUM 
        GROUP BY F_ECRITUREC.CT_NUM,CT_INTITULE
        """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    connection.close()

    df = pd.DataFrame(rows, columns=["CT_NUM", "CT_INTITULE", "SUMS"])
    return df
