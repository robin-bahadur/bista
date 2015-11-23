# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import tools
import csv
import time
import datetime
import zipfile
from StringIO import StringIO
import cStringIO
import base64
from tools.translate import _
from osv import osv, fields
import netsvc

import decimal_precision as dp


class purchase_order_lines(osv.osv_memory):
    _name = "purchase.order.lines"
    _description = "Import Purchase Lines"


    def generate_lines(self, cr, uid, ids, context):

        '''
         Code to import csv and generate purchase order lines for the purchase order

        '''

        sale_id = context.get('active_id')
        print "sale ID",sale_id

        data = self.browse(cr, uid, ids[0])
        if not data.csv_file_sale_lines:
            raise osv.except_osv(_('CSV Error !'), _('Please select a .csv file'))
        module_data = data.csv_file_sale_lines
        val = base64.decodestring(module_data)


        product_inv_data = val.split("\r")

        print "Product INV Data",product_inv_data,type(product_inv_data)
        if len(product_inv_data)==1 and product_inv_data[0].find('\n')!=-1:
            product_inv_data = product_inv_data[0].split('\n')

        print "len",len(product_inv_data)

        for i in range(0,len(product_inv_data)):
            if i==0:
                continue
            product_inv_data_lines = product_inv_data[i]
            print "product_inv_data_lines",product_inv_data_lines

            product_single_line = product_inv_data_lines.split(',')
            print "product_single_line",product_single_line
            if product_single_line[0] == '':
                continue


            reference = product_single_line[1].strip()
            reference = reference.replace("\"","")

            product_id = self.pool.get('product.product').search(cr, uid, [('default_code','ilike',reference)])

            if product_id == []:
                raise osv.except_osv(_('Product Reference error !'), _('Please select a proper product reference'))

            obj_sale_order_line = self.pool.get('sale.order.line')
            obj_product = self.pool.get('product.product').browse(cr, uid, product_id[0])

            sale_line_id = obj_sale_order_line.create(cr, uid, {
                'product_id' : product_id[0],
                'name' : obj_product.name,
                'order_id' : sale_id,
                'product_uom' : obj_product.uom_id.id,
                'product_uom_qty' : int(product_single_line[0]),
                'price_unit' : obj_product.list_price,
                'discount' : product_single_line[2],

            })
            tax_id = obj_product.taxes_id[0].id
            cr.execute('insert into sale_order_tax(order_line_id,tax_id) values(%s,%s)',(sale_line_id,tax_id))


        return True



    _columns = {
          'csv_file_purchase_lines': fields.binary('CSV file', required=True),

    }


purchase_order_lines()
