# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Vinaya S B(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

{
    'name': 'Inventory Report In PDF and Excel',
    'version': '13.0.1.1.1',
    'summary': 'This module helps to Create and Print inventory reports in Excel (XLSX) and PDF format.',
    'description': """This module helps to Create and Print inventory reports in Excel (XLSX) and PDF format,Excel Report,Xlsx.PDF Report,Report,Inventory.""",
    'category': 'Warehouse',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'author': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'stock'],
    'data': [
        'views/inventory_report.xml',
        # 'views/action_manager.xml',
        'reports/report_templates.xml',
        'reports/inventory_stock_pdf.xml'
    ],
    'qweb': [
    ],
    'assets': {
        # 'web.assets_qweb': [
        #     'naseem_warth/static/src/xml/pos_receipt.xml',
        # ],
        'web.assets_backend': [
            'report_stock_inventory/static/src/js/action_manager.js',
        ],
    },

    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 20,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
