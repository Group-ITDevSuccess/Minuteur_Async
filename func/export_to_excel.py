from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill, Font
from datetime import date

def get_age(date_string):
    """Calculates the age in days between a given date and today's date"""
    today = date.today()
    delta = today - date_string
    return delta.days

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
    sheet["A1"] = "CODE"
    sheet["A1"].fill = header_fill
    sheet["A1"].font = header_font

    sheet["B1"] = "INTITULE"
    sheet["B1"].fill = header_fill
    sheet["B1"].font = header_font

    sheet["C1"] = "ECHEANCE"
    sheet["C1"].fill = header_fill
    sheet["C1"].font = header_font

    sheet["D1"] = "ECHU"
    sheet["D1"].fill = header_fill
    sheet["D1"].font = header_font

    sheet["E1"] = "30"
    sheet["E1"].fill = header_fill
    sheet["E1"].font = header_font

    sheet["F1"] = "60"
    sheet["F1"].fill = header_fill
    sheet["F1"].font = header_font

    sheet["G1"] = "90"
    sheet["G1"].fill = header_fill
    sheet["G1"].font = header_font

    sheet["H1"] = "90+"
    sheet["H1"].fill = header_fill
    sheet["H1"].font = header_font

    sheet["I1"] = "SOMME"
    sheet["I1"].fill = header_fill
    sheet["I1"].font = header_font
    row_index = 2

    sums = {}

    for index, row in df.iterrows():
        key = (row["CODE"], row["INTITULE"], row["ECHEANCE"])
        solde = row["SOLDE"]
        echeance_date = row["ECHEANCE"].date()

        if key not in sums:
            sums[key] = {
                "ECHU": 0,
                "30": 0,
                "60": 0,
                "90": 0,
                "90+": 0,
                "SOLDE": 0,
            }

        sums[key]["SOLDE"] += solde

        if echeance_date == date(1753, 1, 1) or echeance_date == date.today():
            sums[key]["ECHU"] += solde
        else:
            age = get_age(echeance_date)

            if age <= 30:
                sums[key]["30"] += solde
            elif 31 <= age <= 60:
                sums[key]["60"] += solde
            elif 61 <= age <= 90:
                sums[key]["90"] += solde
            else:
                sums[key]["90+"] += solde

    for key, values in sums.items():
        sheet["A" + str(row_index)] = key[0]
        sheet["B" + str(row_index)] = key[1]
        sheet["C" + str(row_index)] = key[2]
        sheet["D" + str(row_index)] = values["ECHU"]
        sheet["E" + str(row_index)] = values["30"]
        sheet["F" + str(row_index)] = values["60"]
        sheet["G" + str(row_index)] = values["90"]
        sheet["H" + str(row_index)] = values["90+"]
        sheet["I" + str(row_index)] = values["SOLDE"]

        row_index += 1

    # Appliquer le style de bordure à toutes les cellules remplies
    for row in sheet.iter_rows(min_row=1, min_col=1, max_row=sheet.max_row, max_col=sheet.max_column):
        for cell in row:
            cell.border = border_style
    print(sheet.rows)
    filename = "donnees.xlsx"
    workbook.save(filename)
    return filename
