import pandas as pd
import psycopg2

def execute_sql_query():

    connection = psycopg2.connect(
        host="localhost",
        database="nom_base_de_donnees",
        user="utilisateur",
        password="mot_de_passe"
    )

    query = """
        SELECT F_ECRITUREC.CT_NUM, CT_INTITULE, SUM(CASE WHEN EC_SENS=0 THEN EC_MONTANT ELSE -EC_MONTANT END) AS SUMS
        FROM F_ECRITUREC
        INNER JOIN F_COMPTET ON F_ECRITUREC.CT_NUM = F_COMPTET.CT_NUM
        GROUP BY F_ECRITUREC.CT_NUM, CT_INTITULE
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    connection.close()

    df = pd.DataFrame(rows, columns=["CT_NUM", "CT_INTITULE", "SUMS"])
    return df
