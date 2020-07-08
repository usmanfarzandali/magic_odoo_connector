# -*- coding: utf-8 -*-
###################################################################################
#
#    Sharplogicians Pvt. Ltd.
#    Copyright (C) 2020-TODAY Sharplogicians (<https://sharplogicians.com/>).
#    Author: Usman Farzand (<https://sharplogicians.com/>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "Magic Odoo Connector",
    'version': '13.0.1.0.6',
    'summary': """Magic Odoo Connector""",
    'description': """Magic Connection with Odoo ERP""",
    'category': 'Contacts',
    'author': 'Usman Farzand',
    'company': 'Sharplogicians',
    'maintainer': 'Usman Farzand',
    'website': "https://sharplogicians.com",
    'depends': ['base', 'contacts'],
    

    'data': [
            
            'security/ir.model.access.csv',
             'views/customer_source_view.xml',
             'views/magic_connection_view.xml',
             'views/magic_res_partner_view.xml',
            
             
             'views/menu_view.xml',
    ],
    'qweb': ["static/src/xml/pos_dashboard.xml"],
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}