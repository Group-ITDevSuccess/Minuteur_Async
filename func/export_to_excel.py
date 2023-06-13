from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill, Font
from datetime import date
from openpyxl.styles import Alignment


def get_age(date_string):
    """Calculates the age in days between a given date and today's date"""
    today = date.today()
    delta = today - date_string.date()  # Convertir en objet date
    return delta.days


def get_type(type_value):
    if type_value == 0:
        return "Client"
    elif type_value == 1:
        return "Fournisseur"
    elif type_value == 3:
        return "Autre"
    else:
        return ""


def export_to_excel(df):
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

    # Ajout des en-têtes avec le style de remplissage et de police
    sheet["A1"] = "TYPE"
    sheet["A1"].fill = header_fill
    sheet["A1"].font = header_font
    sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["B1"] = "CODE"
    sheet["B1"].fill = header_fill
    sheet["B1"].font = header_font
    sheet["B1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["C1"] = "INTITULE"
    sheet["C1"].fill = header_fill
    sheet["C1"].font = header_font
    sheet["C1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["D1"] = "NON ECHU"
    sheet["D1"].fill = header_fill
    sheet["D1"].font = header_font
    sheet["D1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["E1"] = "30"
    sheet["E1"].fill = header_fill
    sheet["E1"].font = header_font
    sheet["E1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["F1"] = "60"
    sheet["F1"].fill = header_fill
    sheet["F1"].font = header_font
    sheet["F1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["G1"] = "90"
    sheet["G1"].fill = header_fill
    sheet["G1"].font = header_font
    sheet["G1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["H1"] = "90+"
    sheet["H1"].fill = header_fill
    sheet["H1"].font = header_font
    sheet["H1"].alignment = Alignment(horizontal="center", vertical="center")

    sheet["I1"] = "SOLDES"
    sheet["I1"].fill = header_fill
    sheet["I1"].font = header_font
    sheet["I1"].alignment = Alignment(horizontal="center", vertical="center")

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

        # sheet["A" + str(row_index)] = get_type(row["TYPE"])

    for key, values in sums.items():
        sheet["A" + str(row_index)] = key[0]
        sheet["B" + str(row_index)] = key[1]
        sheet["C" + str(row_index)] = key[2]
        sheet["D" + str(row_index)] = values["NON_ECHU"]
        sheet["E" + str(row_index)] = values["30"]
        sheet["F" + str(row_index)] = values["60"]
        sheet["G" + str(row_index)] = values["90"]
        sheet["H" + str(row_index)] = values["90+"]
        sheet["I" + str(row_index)] = values["SOLDES"]

        # Appliquer le style de bordure aux cellules de la ligne
        for column in range(1, sheet.max_column + 1):
            sheet.cell(row=row_index, column=column).border = border_style

        row_index += 1

    # Ajuster la largeur des colonnes pour s'adapter au contenu
    for column_cells in sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Sauvegarder le fichier Excel
    filename = "donnees.xlsx"
    workbook.save(filename)
    return filename
