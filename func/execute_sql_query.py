import pandas as pd
import pyodbc


def execute_sql_query(base):
    # Chaîne de connexion
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={base['server']};DATABASE={base['database']}" \
               f";UID={base['username']};PWD={base['password']}"

    # Connexion à la base de données
    connection = pyodbc.connect(conn_str)

    if connection:
        print('Connected')

    query = """
        SELECT F_ECRITUREC.CT_NUM, CT_INTITULE, 
        SUM(CASE WHEN EC_SENS=0 THEN EC_MONTANT ELSE -EC_MONTANT END) 
        AS SUMS FROM F_ECRITUREC INNER JOIN F_COMPTET ON F_ECRITUREC.CT_NUM=F_COMPTET.CT_NUM 
        GROUP BY F_ECRITUREC.CT_NUM, CT_INTITULE
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            # Convertir les objets pyodbc.Row en tuples
            rows = [tuple(row) for row in rows]

            if all(isinstance(row, tuple) for row in rows):
                df = pd.DataFrame(rows, columns=["CT_NUM", "CT_INTITULE", "SUMS"])
                print('Exel save and use')
            else:
                print("Error format")

    connection.close()

    return df
