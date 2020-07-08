# # -*- coding: utf-8 -*-
#
# -*- coding: utf-8 -*-

from odoo import fields,api, models, _
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
                                help="Location Filter")
    category = fields.Many2many('product.category', string='Category', help="Category Filter")

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
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'stock.quantity.history',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Inventory Stock Report',
                     }
        }

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
            'inventory_date': inventory_date
        }
        return self.env.ref('report_stock_inventory.action_stock_pdf').report_action(self, data)

    def open_at_date(self):
        self.ensure_one()

        if self.open_at_date:
            tree_view_id = self.env.ref('stock.view_stock_product_tree').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Products'),
                'res_model': 'product.product',
                'context': dict(self.env.context, to_date=self.inventory_datetime),
            }
            return action
        else:
            self.env['stock.quant']._merge_quants()
            self.env['stock.quant']._unlink_zero_quants()
            action = self.env.ref('stock.quantsact').read()[0]
            if self.location:
                action['domain'] = [('location_id', 'in', self.location.ids)]
            return action

    def get_xlsx_report(self, data, response):
        print("hjvhghgvf")
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
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
        if data['date']:
            sheet.write('A2', 'Date:', format6)
            sheet.write('B2', data['inventory_date'], format7)
        if data['loc_name']:
            sheet.write('G2', 'Location(s):', format6)
            sheet.write('H2', data['loc_name'], format7)
        if data['categ_name']:
            sheet.write('G2', 'Categories:', format6)
            sheet.write('H2', data['categ_name'], format7)
        if data['loc_name'] and data['categ_name']:
            sheet.write('G2', 'Categories:', format6)
            sheet.write('H2', data['categ_name'], format7)
            sheet.write('G3', 'Locations:', format6)
            sheet.write('H3', data['loc_name'], format7)
        if data['compute_at_date'] == 0:
            query = '''SELECT t.name,quantity,reserved_quantity,l.name as loc_name,p.default_code,pt.name as unit
                        FROM stock_quant s
                        INNER JOIN product_product as p ON p.id=s.product_id
                        INNER JOIN product_template as t ON p.product_tmpl_id=t.id
                        INNER JOIN stock_location as l ON l.id=s.location_id
                        INNER JOIN uom_uom as pt ON t.uom_id=pt.id
                        WHERE '''
            if data['location'] and not data['category']:
                loc_filter = data['location'].ids
                if len(loc_filter) == 1:
                    loc_filter = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_filter = str(tuple(data['location'].ids))
                query += ''' s.location_id IN %s AND  l.usage='internal' AND t.type='product'
                             GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                             ORDER BY t.name''' % loc_filter
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            elif data['category'] and not data['location']:
                categ_filter = data['category'].ids
                if len(categ_filter) == 1:
                    categ_filter = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_filter = str(tuple(data['category'].ids))
                query += '''t.categ_id IN %s AND l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name''' % categ_filter
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            elif data['category'] and data['location']:
                categ_filter = data['category'].ids
                loc_filter = data['location'].ids
                if len(categ_filter) == 1:
                    categ_filter = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_filter = tuple(data['category'].ids)
                if len(loc_filter) == 1:
                    loc_filter = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_filter = tuple(data['location'].ids)

                query += '''t.categ_id IN %s AND s.location_id IN %s AND l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name''' % (categ_filter, loc_filter)
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            else:
                query = ''' SELECT t.name,quantity,reserved_quantity,l.name as loc_name,p.default_code,pt.name as unit
                            FROM stock_quant s
                            INNER JOIN product_product as p ON p.id=s.product_id
                            INNER JOIN product_template as t ON p.product_tmpl_id=t.id
                            INNER JOIN stock_location as l ON l.id=s.location_id
                            INNER JOIN uom_uom as pt ON t.uom_id=pt.id
                            WHERE l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name'''
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            sheet.merge_range('B7:D7', 'Inventory Stock Report', format2)
            sheet.write('A9', 'S NO', format4)
            sheet.write('B9', "Internal Reference", format4)
            sheet.write('C9', "Product", format4)
            sheet.write('D9', "Location", format4)
            sheet.write('E9', "Quantity", format4)
            sheet.write('F9', "Unit", format4)
            row_num = 9
            col_num = 0
            j = 10
            s_no = 1
            for prod in quantities:
                sheet.write(row_num, col_num, s_no, format9)
                sheet.write(row_num, col_num + 1, prod['default_code'], format5)
                sheet.write(row_num, col_num + 2, prod['name'], format5)
                sheet.write(row_num, col_num + 3, prod['loc_name'], format5)
                sheet.write(row_num, col_num + 4, prod['quantity'], format5)
                sheet.write(row_num, col_num + 5, prod['unit'], format5)

                row_num += 1
                s_no += 1
                j += 1

        else:
            location_filter = ''
            category_filter = ''

            if data['location'] and data['category']:
                categ_filter = data['category'].ids
                loc_filter = data['location'].ids
                if len(categ_filter) == 1:
                    categ_ids = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_ids = str(tuple(data['category'].ids))
                if len(loc_filter) == 1:
                    loc_ids = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_ids = str(tuple(data['location'].ids))
                category_filter = 'AND pt.categ_id IN %s' % categ_ids
                location_filter = 'AND sm.location_dest_id IN %s' % loc_ids

            elif data['location'] and not data['category']:
                loc_filter = data['location'].ids
                if len(loc_filter) == 1:
                    loc_ids = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_ids = str(tuple(data['location'].ids))
                location_filter = 'AND sm.location_dest_id IN %s' % loc_ids

            elif data['category'] and not data['location']:
                categ_filter = data['category'].ids
                if len(categ_filter) == 1:
                    categ_ids = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_ids = str(tuple(data['category'].ids))
                category_filter = 'AND pt.categ_id IN %s' % categ_ids

            query_at_date = '''
                            SELECT product_id,name,sum(quantity) as total,default_code,unit FROM(SELECT sl.name as loc_name,um.name as unit,
                                    sm.product_id, sum(sml.qty_done) * -1 as quantity, pt.name,pp.default_code, sml.date
                                    FROM stock_move  sm
                                    INNER JOIN stock_move_line sml ON sml.move_id=sm.id
                                    INNER JOIN stock_location sl ON sl.id= sm.location_id
                                    INNER JOIN product_product pp ON pp.id=sm.product_id
                                    INNER JOIN product_template pt ON pt.id=pp.product_tmpl_id 
                                    INNER JOIN uom_uom as um ON pt.uom_id=um.id
                                    WHERE sm.state = 'done' AND 
                                    sl.usage='internal' 
                                    AND sm.date <= '%s'
                                    AND pt.type='product'
                                    %s 
                                    %s
                                    GROUP BY loc_name,pt.name, sml.date, sm.product_id,pp.default_code,unit

                                UNION ALL

                                SELECT sl.name as loc_name,um.name as unit,sm.product_id,sum(sml.qty_done) as quantity,
                                    pt.name,pp.default_code, sml.date
                                    FROM stock_move sm
                                    INNER JOIN stock_move_line sml ON sml.move_id=sm.id
                                    INNER JOIN stock_location sl ON sl.id= sm.location_dest_id
                                    INNER JOIN product_product pp ON pp.id=sm.product_id
                                    INNER JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                    INNER JOIN uom_uom as um ON pt.uom_id=um.id
                                     WHERE sml.state = 'done'
                                    AND sl.usage='internal' 
                                    AND sm.date <= '%s'
                                    AND pt.type='product'
                                    %s
                                    %s 
                                    GROUP BY loc_name,pt.name, sml.date,sm.product_id,pp.default_code,unit) as sub 
                                    GROUP BY product_id,name,default_code,unit
                                    ORDER BY product_id;
                        ''' % (
            data['date'], location_filter, category_filter, data['date'], location_filter, category_filter)
            self._cr.execute(query_at_date)
            quantities_at_date = self._cr.dictfetchall()

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
            for prod in quantities_at_date:
                sheet.write(row_num, col_num, s_no, format9)
                sheet.write(row_num, col_num + 1, prod['default_code'], format5)
                sheet.write(row_num, col_num + 2, prod['name'], format5)
                sheet.write(row_num, col_num + 3, prod['total'], format5)
                sheet.write(row_num, col_num + 4, prod['unit'], format5)

                row_num += 1
                s_no += 1
                j += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

