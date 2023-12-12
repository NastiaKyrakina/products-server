import io
import json
import xlsxwriter

def write_to_file(data):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Загальна калорійність')
    worksheet.write('A2', data.get('general').get('energy'))
    worksheet.write('B1', 'Загальна вартість')
    worksheet.write('B2', data.get('general').get('price'))
    worksheet.write('C1', 'Вуглеводи')
    worksheet.write('C2', data.get('general').get('carbohydrates'))
    worksheet.write('D1', 'Жири')
    worksheet.write('D2', data.get('general').get('fats'))
    worksheet.write('E1', 'Білки')
    worksheet.write('E2', data.get('general').get('proteins'))
    worksheet.write('A4', 'Назва')
    worksheet.write('B4', 'Кількість')
    worksheet.write('C4', 'Калорійність')
    worksheet.write('D4', 'Білки')
    worksheet.write('E4', 'Жири')
    worksheet.write('F4', 'Вуглеводи')
    worksheet.write('G4', 'Вартість')
    row = 3
    col = 0
    for product in data.get('product_bucket'):
        print(product)
        worksheet.write(row, col, product.get('name'))
        worksheet.write(row, col + 1, product.get('amount'))
        worksheet.write(row, col + 2, product.get('states')[0].get("energy"))
        worksheet.write(row, col + 3, product.get('states')[0].get("proteins"))
        worksheet.write(row, col + 4, product.get('states')[0].get("fats"))
        worksheet.write(row, col + 5, product.get('states')[0].get("carbohydrates"))
        worksheet.write(row, col + 6, product.get('price'))
        row += 1
    workbook.close()
    output.seek(0)
    return output
