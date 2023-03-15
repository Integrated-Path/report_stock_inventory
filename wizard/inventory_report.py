# # -*- coding: utf-8 -*-
#
# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class InventoryReport(models.TransientModel):
    _inherit = 'stock.quantity.history'

    location = fields.Many2many('stock.location', string='Location', domain="[('usage', '=', 'internal')]",
                                help="Location Filter", required=True)
    category = fields.Many2many('product.category', string='Category', help="Category Filter")
    include_lines = fields.Boolean(string="Include Lines", default=True)

    def xlsx_report(self):
        inventory_date = self.inventory_datetime.strftime('%Y-%m-%d')
        loc_name = ''
        for loc in self.location:
            loc_name = loc_name + loc.display_name + ','
        loc_name = loc_name[:-1]
        categ_name = ''
        for categ in self.category:
            categ_name = categ_name + categ.name + ','
        categ_name = categ_name[:-1]
        data = {
            'location': self.location.ids,
            'category': self.category.ids,
            'compute_at_date': self.open_at_date,
            'date': self.inventory_datetime,
            'loc_name': loc_name,
            'categ_name': categ_name,
            'inventory_date': inventory_date
        }
        return self.env.ref('report_stock_inventory.stock_inventory_def_reports_xlsx_id').report_action([], data)

        # return {
        #     'type': 'ir_actions_xlsx_download',
        #     'data': {'model': 'stock.quantity.history',
        #              'options': json.dumps(data, default=date_utils.json_default),
        #              'output_format': 'xlsx',
        #              'report_name': 'Inventory Stock Report',
        #              }
        # }

    def print_pdf(self):
        inventory_date = self.inventory_datetime.strftime('%Y-%m-%d')
        loc_name = ''
        for loc in self.location:
            loc_name = loc_name + loc.display_name + ','
        loc_name = loc_name[:-1]
        categ_name = ''
        for categ in self.category:
            categ_name = categ_name + categ.name + ','
        categ_name = categ_name[:-1]
        data = {
            'location': self.location.ids,
            'category': self.category.ids,
            'compute_at_date': self.open_at_date,
            'date': self.inventory_datetime,
            'loc_name': loc_name,
            'categ_name': categ_name,
            'inventory_date': inventory_date,
            'include_lines': self.include_lines,
        }

        return self.env.ref('report_stock_inventory.action_stock_pdf').report_action(self, data)


class PartnerXlsxStockReport(models.AbstractModel):
    _name = "report.report_stock_inventory.st_reports_xlsx_id"
    _inherit = "report.report_xlsx.abstract"
    _description = "Sale XLSX Report"

    def generate_xlsx_report(self, workbook, data, docs):
        sheet = workbook.add_worksheet('Stock xlsx Report')
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 12, 'bold': True, 'border': 1, 'bg_color': '#928E8E'})
        format4 = workbook.add_format({'font_size': 10, 'bold': True, 'border': 1, 'bg_color': '#D2D1D1'})
        format5 = workbook.add_format({'font_size': 10, 'border': 1})
        format6 = workbook.add_format({'font_size': 10, 'bold': True})
        format7 = workbook.add_format({'font_size': 10, 'bold': True})
        format9 = workbook.add_format({'font_size': 10, 'border': 1})
        format2.set_align('center', )
        format4.set_align('center')
        format6.set_align('right')
        format9.set_align('left')
        if data['category']:
            product = self.env['product.product'].search(
                [('categ_id', 'in', data['category']), ('type', '=', 'product'), ('qty_available', '>', 0)])
        else:
            product = self.env['product.product'].search([('type', '=', 'product'), ('qty_available', '>', 0)])

        if data['date']:
            sheet.write('A2', 'Date:', format6)
            sheet.write('B2', data['inventory_date'], format7)

        if data['loc_name'] and not data['categ_name']:
            sheet.write('G2', 'Location(s):', format6)
            sheet.write('H2', data['loc_name'], format7)
        if data['categ_name'] and not data['loc_name']:
            sheet.write('G2', 'Categories:', format6)
            sheet.write('H2', data['categ_name'], format7)
        if data['loc_name'] and data['categ_name']:
            sheet.write('G2', 'Categories:', format6)
            sheet.write('H2', data['categ_name'], format7)
            sheet.write('G3', 'Locations:', format6)
            sheet.write('H3', data['loc_name'], format7)
        sheet.merge_range('B7:D7', 'Inventory Stock Report', format2)
        sheet.write('A9', 'S NO', format4)
        sheet.write('B9', "Internal Reference", format4)
        sheet.write('C9', "Product", format4)
        sheet.write('D9', "Quantity", format4)
        sheet.write('E9', "Unit", format4)
        row_num = 9
        col_num = 0
        j = 10
        s_no = 1
        for prod in product:
            rec = prod.with_context({'location': data['location'], 'to_date': data['date']})
            if rec.qty_available > 0:
                sheet.write(row_num, col_num, s_no, format9)
                sheet.write(row_num, col_num + 1, rec.default_code, format5)
                sheet.write(row_num, col_num + 2, rec.name, format5)
                sheet.write(row_num, col_num + 3, rec.qty_available, format5)
                sheet.write(row_num, col_num + 4, rec.uom_id.name, format5)

                row_num += 1
                s_no += 1
                j += 1

        # workbook.close()
        # output.seek(0)
        # response.stream.write(output.read())
        # output.close()
