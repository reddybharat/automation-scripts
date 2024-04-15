from openpyxl import load_workbook
from openpyxl.styles import Font

#loading workbook
wb = load_workbook('C:\Coding\scripts\Generated\\beverage_sales_pivot_table.xlsx')
#selecting the sheet
sheet = wb['Report']

sheet['O1'] = 'TOTAL'
sheet['O1'].font = Font('Arial', bold=True, size=12)

wb.save('C:\Coding\scripts\Generated\Report_formatted.xlsx')