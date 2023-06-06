from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill, Font

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
    sheet["A1"] = "CT_NUM"
    sheet["A1"].fill = header_fill
    sheet["A1"].font = header_font
    sheet["B1"] = "CT_INTITULE"
    sheet["B1"].fill = header_fill
    sheet["B1"].font = header_font
    sheet["C1"] = "SUMS"
    sheet["C1"].fill = header_fill
    sheet["C1"].font = header_font

    for index, row in df.iterrows():
        sheet["A" + str(index + 2)] = row["CT_NUM"]
        sheet["B" + str(index + 2)] = row["CT_INTITULE"]
        sheet["C" + str(index + 2)] = row["SUMS"]

    # Appliquer le style de bordure à toutes les cellules remplies
    for row in sheet.iter_rows(min_row=1, min_col=1, max_row=sheet.max_row, max_col=sheet.max_column):
        for cell in row:
            cell.border = border_style

    filename = "donnees.xlsx"
    workbook.save(filename)
    return filename
