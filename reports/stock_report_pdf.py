# -*- coding: utf-8 -*-
import datetime

from odoo import models, api


class InventoryReportPDF(models.AbstractModel):
    _name = "report.report_stock_inventory.report_stock_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        quantities_at_date = 0
        quantities = 0

        if data['compute_at_date'] == False:
            query = '''SELECT t.name,quantity,reserved_quantity,l.name as loc_name,p.default_code,pt.name as unit
                        FROM stock_quant s
                        INNER JOIN product_product as p ON p.id=s.product_id
                        INNER JOIN product_template as t ON p.product_tmpl_id=t.id
                        INNER JOIN stock_location as l ON l.id=s.location_id
                        INNER JOIN uom_uom as pt ON t.uom_id=pt.id
                        WHERE '''
            if data['location'] and not data['category']:
                loc_filter = data['location']
                if len(loc_filter) == 1:
                    loc_filter = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_filter = str(tuple(data['location']))
                query += ''' s.location_id IN %s AND  l.usage='internal' AND t.type='product'
                             GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                             ORDER BY t.name''' % loc_filter
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            elif data['category'] and not data['location']:
                categ_filter = data['category']
                if len(categ_filter) == 1:
                    categ_filter = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_filter = str(tuple(data['category']))
                query += '''t.categ_id IN %s AND l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name''' % categ_filter
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            elif data['category'] and data['location']:
                categ_filter = data['category']
                loc_filter = data['location']
                if len(categ_filter) == 1:
                    categ_filter = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_filter = tuple(data['category'])
                if len(loc_filter) == 1:
                    loc_filter = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_filter = str(tuple(data['location']))

                query += '''t.categ_id IN %s AND s.location_id IN %s AND l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name''' % (categ_filter, loc_filter)
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()

            else:
                query = ''' SELECT t.name,quantity,reserved_quantity,l.name as loc_name,p.default_code,pt.name as unit
                            FROM stock_quant s
                            INNER JOIN product_product AS p ON p.id=s.product_id
                            INNER JOIN product_template AS t ON p.product_tmpl_id=t.id
                            INNER JOIN stock_location AS l ON l.id=s.location_id
                            INNER JOIN uom_uom AS pt ON t.uom_id=pt.id
                            WHERE l.usage='internal' AND t.type='product'
                            GROUP BY t.name,quantity,loc_name,reserved_quantity,p.default_code,pt.name
                            ORDER BY t.name'''
                self._cr.execute(query)
                quantities = self._cr.dictfetchall()
        else:
            location_filter = ''
            category_filter = ''

            if data['location'] and data['category']:
                categ_filter = data['category']
                loc_filter = data['location']
                if len(categ_filter) == 1:
                    categ_ids = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_ids = str(tuple(data['category']))
                if len(loc_filter) == 1:
                    loc_ids = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_ids = str(tuple(data['location']))
                category_filter = 'AND pt.categ_id IN %s' % categ_ids
                location_filter = 'AND sm.location_dest_id IN %s' % loc_ids

            elif data['location'] and not data['category']:

                loc_filter = data['location']
                if len(loc_filter) == 1:
                    loc_ids = str(tuple(loc_filter)).replace(",", "")
                else:
                    loc_ids = str(tuple(data['location']))
                location_filter = 'AND sm.location_dest_id IN %s' % loc_ids

            elif data['category'] and not data['location']:
                categ_filter = data['category']
                if len(categ_filter) == 1:
                    categ_ids = str(tuple(categ_filter)).replace(",", "")
                else:
                    categ_ids = str(tuple(data['category']))
                category_filter = 'AND pt.categ_id IN %s' % categ_ids

            query_at_date = '''
                            SELECT product_id,name,sum(quantity) AS total,default_code,unit FROM(select sl.name AS loc_name,um.id as unit,
                                    sm.product_id, sum(sml.qty_done) * -1 AS quantity, pt.name,pp.default_code, sml.date
                                    FROM stock_move sm
                                    INNER JOIN stock_move_line sml ON sml.move_id=sm.id
                                    INNER JOIN stock_location sl ON sl.id= sm.location_id
                                    INNER JOIN product_product pp ON pp.id=sm.product_id
                                    INNER JOIN product_template pt ON pt.id=pp.product_tmpl_id 
                                    INNER JOIN uom_uom AS um ON pt.uom_id=um.id
                                    WHERE sm.state = 'done' AND 
                                    sl.usage='internal' 
                                    AND sm.date <= '%s'
                                    AND pt.type='product'
                                    %s 
                                    %s
                                    GROUP BY loc_name,pt.name, sml.date, sm.product_id,pp.default_code,unit

                                UNION ALL

                                SELECT sl.name as loc_name,um.id as unit,sm.product_id,sum(sml.qty_done) AS quantity,
                                    pt.name,pp.default_code, sml.date
                                    FROM stock_move sm
                                    INNER JOIN stock_move_line sml ON sml.move_id=sm.id
                                    INNER JOIN stock_location sl ON sl.id= sm.location_dest_id
                                    INNER JOIN product_product pp ON pp.id=sm.product_id
                                    INNER JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                    INNER JOIN uom_uom AS um ON pt.uom_id=um.id
                                     WHERE sml.state = 'done'
                                    AND sl.usage='internal' 
                                    AND sm.date <= '%s'
                                    AND pt.type='product'
                                    %s
                                    %s 
                                    GROUP BY loc_name,pt.name, sml.date,sm.product_id,pp.default_code,unit) AS sub 
                                    GROUP BY product_id,name,default_code,unit
                                    ORDER BY product_id;
                                    ''' % (
            data['date'], location_filter, category_filter, data['date'], location_filter, category_filter)
            self._cr.execute(query_at_date)
            quantities_at_date = self._cr.dictfetchall()
        #     quantities_at_date[0]['line'] = 'fuck you'

        doct_list = list()

        units = self.env['uom.uom'].search([('active','=', True)])
        for line in quantities_at_date:            
            new_dict = line

            # getting the quantity in inventory
            loc_total = self.env['stock.quant'].search([['location_id', '=', data['location']]
                ,['product_id.id', '=', line['product_id']]], limit=1).quantity
            if loc_total:
                new_dict.update({'loc_total': loc_total})
            else:
                new_dict.update({'loc_total': "0.0"})

            #getting the unit arabic name
            new_dict.update({'unit_name': "-"})

            for unit in units:
                if (line['unit'] == unit.id):
                    new_dict.update({'unit_name': unit.name})


            doct_list.append(new_dict)

        return {
            'docs': quantities,
            'doc_quantities': doct_list,
            'doc_type': type(quantities_at_date) ,
            'loc_name': data['loc_name'],
            'categ_name': data['categ_name'],
            'report_date': datetime.date.today().strftime('%d-%m-%Y'),
            'inventory_date': data['inventory_date'],
        }

    def tran_unit(self, unitId):
        units = self.env['uom.uom']
        for line in units:
            if (line.id == unitId):
                return line.name
            else:
                return "nothing"