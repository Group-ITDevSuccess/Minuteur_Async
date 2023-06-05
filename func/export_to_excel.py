from openpyxl import Workbook

def export_to_excel(df):
    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "CT_NUM"
    sheet["B1"] = "CT_INTITULE"
    sheet["C1"] = "SUMS"

    for index, row in df.iterrows():
        sheet["A" + str(index + 2)] = row["CT_NUM"]
        sheet["B" + str(index + 2)] = row["CT_INTITULE"]
        sheet["C" + str(index + 2)] = row["SUMS"]

    filename = "donnees.xlsx"
    workbook.save(filename)
    return filename

