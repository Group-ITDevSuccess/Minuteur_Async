from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill, Font
from datetime import date
from openpyxl.styles import Alignment
from datetime import datetime


def get_age(date_string):
    """Calculates the age in days between a given date and today's date"""
    today = date.today()
    delta = today - date_string.date()  # Convertir en objet date
    return delta.days


def get_type(type_value):
    type_mapping = {
        0: "Client",
        1: "Fournisseur",
        3: "Autre"
    }
    return type_mapping.get(type_value, "")


def export_to_excel(df):
    # Obtention de la date actuelle
    current_date = datetime.now().strftime("%Y-%m-%d")

    workbook = Workbook()
    sheet = workbook.active

    # Création d'un style de bordure pour les cellules
    border_style = Border(left=Side(style='thin'),
                          right=Side(style='thin'),
                          top=Side(style='thin'),
                          bottom=Side(style='thin'))

    # Création d'un style de remplissage pour l'en-tête
    header_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Création d'un style de police gras pour l'en-tête
    header_font = Font(bold=True)

    # En-têtes des colonnes
    headers = ["TYPE", "CODE", "INTITULE", "NON ECHU", "30", "60", "90", "90+", "SOLDES"]

    for col_index, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_index, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Dictionnaire pour stocker les sommes des valeurs
    sums = {}

    row_index = 2

    for index, row in df.iterrows():
        key = (get_type(row["TYPE"]), row["CODE"], row["INTITULE"])
        echeance = row["ECHEANCE"]
        solde = row["SOLDE"]

        if key not in sums:
            sums[key] = {
                "NON_ECHU": 0,
                "30": 0,
                "60": 0,
                "90": 0,
                "90+": 0,
                "SOLDES": 0
            }

        age = get_age(echeance)

        if age <= 0 or echeance.date() == date(1753, 1, 1):
            sums[key]["NON_ECHU"] += solde
        elif 0 < age <= 30:
            sums[key]["30"] += solde
        elif 30 < age <= 60:
            sums[key]["60"] += solde
        elif 60 < age <= 90:
            sums[key]["90"] += solde
        else:
            sums[key]["90+"] += solde

        sums[key]["SOLDES"] += solde

    for key, values in sums.items():
        for col_index, value in enumerate(key, start=1):
            sheet.cell(row=row_index, column=col_index, value=value)

        for col_index, value in enumerate(values.values(), start=len(key) + 1):
            sheet.cell(row=row_index, column=col_index, value=value)

        # Appliquer le style de bordure aux cellules de la ligne
        for column in range(1, sheet.max_column + 1):
            sheet.cell(row=row_index, column=column).border = border_style

        row_index += 1

    # Ajuster la largeur des colonnes pour s'adapter au contenu
    for column_cells in sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Sauvegarder le fichier Excel
    filename = f"donnees_{current_date}.xlsx"
    workbook.save(filename)
    return filename
