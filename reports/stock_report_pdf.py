# -*- coding: utf-8 -*-
import datetime

from odoo import models, api


class InventoryReportPDF(models.AbstractModel):
    _name = "report.report_stock_inventory.report_stock_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        quantities_at_date = 0

        if data['category']:
            products = self.env['product.product'].search(
                [('categ_id', 'in', data['category']), ('type', '=', 'product')])
        else:
            products = self.env['product.product'].search([('type', '=', 'product')])
        product_dict = []

        # get the stock moves backward until the given string date from the wizard and store it at stock_moves_to_date.
        stock_moves = self.env['stock.move'].search([])
        stock_moves_to_date = []
        for stock_move in stock_moves:
            if stock_move.date.date() > datetime.datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S').date():
                stock_moves_to_date.append(stock_move)

        total_quantity = 0
        for product in products:
            for location in data['location']:
                # calculate the quantity at location and date backward from stock quant and stock move tables.
                quantity_at_location_date = self.env['stock.quant'].search(
                    [('product_id', '=', product.id), ('location_id', '=', location)]).quantity
                for stock_move_to_date in stock_moves_to_date:
                    if (
                            stock_move_to_date.product_id.id == product.id and stock_move_to_date.location_id.id == location and stock_move_to_date.state == 'done'):
                        quantity_at_location_date = quantity_at_location_date + stock_move_to_date.product_qty
                    elif (
                            stock_move_to_date.product_id.id == product.id and stock_move_to_date.location_dest_id.id == location and stock_move_to_date.state == 'done'):
                        quantity_at_location_date = quantity_at_location_date - stock_move_to_date.product_qty
                if (quantity_at_location_date > 0):
                    total_quantity = total_quantity + quantity_at_location_date
                    product_dict.append(
                        {
                            'product': product,
                            'qty_available': int(quantity_at_location_date),
                            'uom_id': product.uom_id.name,
                            'location': self.env['stock.location'].search([('id', '=', location)]).name,
                        })

        return {
            'docs': product_dict,
            'doc_quantities': quantities_at_date,
            'loc_name': data['loc_name'],
            'categ_name': data['categ_name'],
            'report_date': datetime.date.today().strftime('%d-%m-%Y'),
            'inventory_date': data['inventory_date'],
            'total': int(total_quantity),
        }
