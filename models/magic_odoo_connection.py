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
#crm_lead helping 
import psycopg2
import logging
import threading
from psycopg2 import sql
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict, defaultdict
_logger = logging.getLogger(__name__)


class MagicResPartner(models.Model):
    _name = "magic.res.partner"
    _description = "Magic Customers"
    #_inherit = ['mail.thread', 'mail.activity.mixin']


    magic_ref = fields.Char('Ref')
    title = fields.Many2one('res.partner.title', 'Title')
    #customer_source_id = fields.Many2one('customer.source', 'Customer Source')
    name = fields.Char('Name')
    magic_phone = fields.Char('Phone')
    magic_mobile = fields.Char('Mobile')
    magic_fax = fields.Char('Fax')
    magic_street = fields.Char('Street')
    magic_street2 = fields.Char('Street 2')
    magic_city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    magic_zip = fields.Char('Zip')
    country_id = fields.Many2one('res.country', 'Country')
    magic_email = fields.Char('Email')
    magic_website = fields.Char('Website')
    magic_vat = fields.Char('Vat')
    magic_company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],)

    magic_comment = fields.Text('Internal Notes')
    magic_uniq_id = fields.Integer('Magic Uniq ID')
    magic_customer_number = fields.Integer('Magic Customer Code')
    category_ids = fields.Many2many('res.partner.category', 'Tags')

    customer_source_id = fields.Many2one('customer.source', 'Customer Source ID')
    state = fields.Selection([('draft', 'Draft'),('trasfer', 'Trasfer'),('cancel', 'Cancelled')], default="draft")
    magic_connection_id = fields.Many2one('magic.connection', 'Magic Connection ID')
    magic_customer_code = fields.Char('Magic Customer Code')
    customer_rank = fields.Integer('Customer Rank')
    supplier_rank = fields.Integer('Supplier Rank')



    def action_create_customer(self):
        self.ensure_one()
        record_list = []
        record_vals = {
                        'magic_uniq_id': self.magic_uniq_id,
                        'magic_customer_number': self.magic_customer_number,
                        'ref': self.magic_ref,
                        'title': self.title.id,
                        'magic_customer_code': self.magic_customer_code,
                        'name': self.name,
                        'phone': self.magic_phone,
                        'mobile': self.magic_mobile,
                        'fax': self.magic_fax,
                        'street': self.magic_street,
                        'street2': self.magic_street2,
                        'city': self.magic_city,
                        'zip': self.magic_zip,
                        #'state_id': state,
                        'country_id': self.country_id.id,
                        'company_type': 'person', #company for company
                        'email': self.magic_email,
                        'website': self.magic_website,
                        'vat': self.magic_vat,
                        'comment': self.magic_comment,
                        #'category_id': category, many2many relationship waiting for
                        'customer_rank': 1,
                        'supplier_rank': 0,

                        }
            
        record_list.append(record_vals)
        self.env['res.partner'].create(record_list)
        self.state = 'trasfer'

    
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'





    

class CustomerSource(models.Model):
    _name = "customer.source"
    _description = "Customer Source"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Name')
    
    
    
class MagicConnection(models.Model):
    _name = "magic.connection"
    _description = "Magic Customers"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    state = fields.Selection([('draft', 'Draft'),('connected', 'Connected'), ('failed', 'Failed'),('cancel', 'Cancelled')], default="draft")
    name = fields.Char('Host/IP')
    username = fields.Char('User Name')
    password = fields.Char('Password')
    database = fields.Char('Database')
    port = fields.Char('Port', default='5432')
    
    total_trasfer_odoo = fields.Integer(compute='_total_trasfer_to_odoo_count', string='Total Trasfer To Odoo')
    total_synch_record = fields.Integer(compute='_total_fatch_from_magic', string='Total Fatch From Magic')
    
    magic_res_partner_ids = fields.One2many('magic.res.partner', 'magic_connection_id', string='Magic Customer')
    res_partner_ids = fields.One2many('res.partner', 'magic_connection_id', string='Odoo Customer')


    
    def _total_trasfer_to_odoo_count(self):
        data = self.env['magic.res.partner'].search([('state', 'in', ['trasfer'])]).ids
        self.total_trasfer_odoo = len(data)

    def _total_fatch_from_magic(self):
        data = self.env['magic.res.partner'].search([]).ids
        self.total_synch_record = len(data)
  
    def open_magic_customer(self):
        #self.ensure_one()
        # action = self.env.ref('magic_odoo_connection.magic_res_partner_tree_view').read()[0]
        # action.update({
        #     'domain': [('booking_id', '=', self.id)]
        # })
        # return action
        return {
                'name': _('Magic Customer'),
               
                'view_mode': 'tree',
                'view_id': self.env.ref('magic_odoo_connector.magic_res_partner_tree_view').id,
                'res_model': 'magic.res.partner',
                #'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'target': 'current',
                }

    def open_trasfer_customer(self):
        #self.ensure_one()
        # action = self.env.ref('magic_odoo_connection.magic_res_partner_tree_view').read()[0]
        # action.update({
        #     'domain': [('booking_id', '=', self.id)]
        # })
        # return action
        return {
                'name': _('Customer'),
               
                'view_mode': 'tree',
                'view_id': self.env.ref('base.view_partner_tree').id,
                'res_model': 'res.partner',
                #'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'target': 'current',
                }


    def action_try_connection(self):
        try:
            #hostname = '161.35.115.87'
            #port = 5432
            #username = 'postgres'
            #password = '8a5f671a8b96BA'
            #database = 'postgres'
            hostname = self.name
            port = self.port
            username = self.username
            password = self.password
            database = self.database
            
            
            
            conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database )

            if conn:
                self.state = 'connected'
                
        except Exception as e:
            self.state = 'failed'
            _logger.warning("PostgreSQL Connection failed. Error: %s" % e)

        finally:
            if conn:
                conn.close()

    def action_cancel(self):
        if self:
            for rec in self:
                rec.state = 'cancel'
    
    
    
    
    
    
    def action_connect_database(self):
        try:
            #hostname = '161.35.115.87'
            #port = 5432
            #username = 'postgres'
            #password = '8a5f671a8b96BA'
            #database = 'postgres'

            hostname = self.name
            port = self.port
            username = self.username
            password = self.password
            database = self.database
            conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database )
            magic_max_number = 0
            magic_res_partner_max_number = 0

            cur = conn.cursor()
            #cur.execute("SELECT max(k_uniqueident) FROM tblCustomers")
            cur.execute("SELECT  COUNT(*) FROM tblCustomers a LEFT JOIN tblcustomernotes b ON a.intcustomerno = b.intcustomerno")
            magic_max_number = cur.fetchone()[0] or 0
            magic_res_partner_max_number = self.env['magic.res.partner'].search([], order='magic_uniq_id desc', limit=1).magic_uniq_id 
            if magic_res_partner_max_number == 0:
                magic_res_partner_max_number = 1
            

            print("==============================================")
            print(magic_max_number)
            print("==============================================")


            start = magic_res_partner_max_number
            end = magic_max_number
            
            title  = country  = False
            
            while start < end:
               
                cur.execute('''
                            SELECT a.k_uniqueident,a.intcustomerno,
                            coalesce(a.chatitle, ''), a.chaorigadcode,
                            CONCAT(a.vchnamefirst,' ',a.vchnamelast),
                            a.chaphone1,a.chaphone2,a.chafax,
                            a.vchstreetaddrprimaryline,
                            a.vchstreetaddrsecondaryline,
                            a.vchcity,a.vchzip,a.vchstate,
                            a.chacountrycode,
                            a.chacustomertype,
                            a.chaemailchecked,
                            a.vchwebsiteurl,
                            a.chataxexempt,
                            b.txtcustomernotes
                          
                            FROM tblCustomers a
                            LEFT JOIN tblcustomernotes b ON a.intcustomerno = b.intcustomerno
                            WHERE a.k_uniqueident >= %s
                            order by a.k_uniqueident
                            limit 10000
                            ''', [start])
                res = cur.fetchall()
                record_list = []
                print("==============================================")
                print(start)
                print("==============================================")
                for rec in res:
                    title = self._find_or_create_title(rec[2])
                    #state = self._find_or_create_state(rec[12])
                    country = self._find_or_create_country(rec[13])
                    #category = self._find_or_create_category(rec[19])

                    



                    record_vals = {
                        'magic_uniq_id': rec[0],
                        'magic_customer_number': rec[1],
                        'magic_ref': rec[1],
                        'title': title,
                        'magic_customer_code': rec[3],
                        'name': rec[4],
                        'magic_phone': rec[5],
                        'magic_mobile': rec[6],
                        'magic_fax': rec[7],
                        'magic_street': rec[8],
                        'magic_street2': rec[9],
                        'magic_city': rec[10],
                        'magic_zip': rec[11],
                        #'state_id': state,
                        'country_id': country,
                        'magic_company_type': 'person', #company for company
                        'magic_email': rec[15],
                        'magic_website': rec[16],
                        'magic_vat': rec[17],
                        'magic_comment': rec[18],
                        #'category_id': category, many2many relationship waiting for
                        'customer_rank': 1,
                        'supplier_rank': 0,

                        }
                    
                    record_list.append(record_vals)
                
                
                
                self.env['magic.res.partner'].create(record_list)
                print("============Completed")
                # self.flush()
                # self.invalidate_cache()
                self.env.cr.commit()
                start += 10000
            print("============Completed End")
                
        except Exception as e:
            _logger.warning("PostgreSQL Connection failed. Error: %s" % e)

        finally:
            if conn:
                conn.close()
    

    def _find_or_create_title(self, title=False):
        title = False if title == ' ' or title == '' else title  
        if title:
            titleObject = self.env['res.partner.title'].search(
                                    [('name', '=', title)])
            if not titleObject:
                titleObject = self.env['res.partner.title'].create({
                'name': title,
                })
            
            return titleObject.id
        else:
            return False
    
    # def _find_or_create_state(self, state=False):
    #     state = False if state == ' ' or state == '' else state  
    #     if state:
    #         stateObject = self.env['res.country.state'].search(
    #                                 [('name', '=', state)])
    #         if not stateObject:
    #             stateObject = self.env['res.country.state'].create({
    #             'name': state,
    #             })
            
    #         return stateObject.id
    #     else:
    #         return False

    def _find_or_create_country(self, country=False):
        country = False if country == ' ' or country == '' else country  
        if country:
            countryObject = self.env['res.country'].search(
                                    [('name', '=', country)])
            if not countryObject:
                countryObject = self.env['res.country'].create({
                'name': country,
                })
            
            return countryObject.id
        else:
            return False


    # def _find_or_create_category(self, category=False):
    #     category = False if category == ' ' or category == '' else category  
    #     if category:
    #         categoryObject = self.env['res.partner.category'].search(
    #                                 [('name', '=', category)])
    #         if not categoryObject:
    #             categoryObject = self.env['res.partner.category'].create({
    #             'name': category,
    #             })
            
    #         return categoryObject.id
    #     else:
    #         return False


class Respartner(models.Model):
    _inherit = "res.partner"

    magic_connection_id = fields.Many2one('customer.source', 'Magic Connection ID')

    magic_customer_number = fields.Integer('Magic Customer Number')
    magic_uniq_id = fields.Integer('Magic Uniq ID')
    magic_customer_code = fields.Char('Magic Customer Code')
    fax = fields.Char('Fax')
    

    


