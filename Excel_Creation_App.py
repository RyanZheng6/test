from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
import datetime

def create_excel_file(filename, sheet_name, headers, data):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    for col, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=header)

    for row, record in enumerate(data, start=2):
        for col, value in enumerate(record, start=1):
            ws.cell(row=row, column=col, value=value)

    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15

    wb.save(filename)

    print(f"Excel file '{filename}' has been created successfully.")

def create_Report():
    filename = f"Report_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
    create_file(filename)
    return filename

def create_file(filename):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'
    wb.save(filename)
    print(f"Excel file '{filename}' has been created successfully.")

def createSummarySheet(filename, sheet_name, headers, data):

    wb = load_workbook(filename)
    ws = wb[sheet_name]

    for col, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=header)
    for row, record in enumerate(data, start=2):
        for col, value in enumerate(record, start=1):
            cell = ws.cell(row=row, column=col, value=value)
            if(value=='link'):
                cell.hyperlink = f"#'{record[0]}'!A1"
                cell.font = Font(color="0000FF", underline="single")

    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15

    wb.save(filename)
    print(f"Summary for the clients file has been created successfully.")

def addClientDetails(filename, sheet_name, headers, data):
    wb = load_workbook(filename)
    ws = wb.create_sheet(sheet_name)

    for col, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=header)

    for row, record in enumerate(data, start=2):
        for col, value in enumerate(record, start=1):
            ws.cell(row=row, column=col, value=value)

    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15

    wb.save(filename)

    print(f"Excel file '{filename}' has added client detail {sheet_name} successfully.")