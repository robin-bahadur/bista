
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
import pickle
import sys

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


class sale_order_lines(osv.osv_memory):
    _name = "sale.order.lines"
    _description = "Import Sale Lines"


    def generate_lines(self, cr, uid, ids, context):

        '''
         Code to import csv and generate sale order lines for the sale order

        '''

        sale_id = context.get('active_id','False')
        
        #######
        sale_browse = self.pool.get('sale.order').browse(cr ,uid ,sale_id)
        pricelist_id = sale_browse.pricelist_id
        
        #######
        
        data = self.browse(cr, uid, ids[0])

        if not data.csv_file_sale_lines:
            raise osv.except_osv(_('CSV Error !'), _('Please select a .csv file'))
        module_data = data.csv_file_sale_lines
        val = base64.decodestring(module_data)


        product_inv_data = val.split("\r")

        if len(product_inv_data)==1 and product_inv_data[0].find('\n')!=-1:
            product_inv_data = product_inv_data[0].split('\n')

    
        for i in range(0,len(product_inv_data)):
            if i==0:
                continue
            product_inv_data_lines = product_inv_data[i]


            product_single_line = product_inv_data_lines.split(',')

            if product_single_line[0] == '' or product_single_line[0] == '\n':
                continue
            elif int(product_single_line[0])< 1:
                raise osv.except_osv(_('Product Quantity !'), _('Please enter proper quantity value in the csv(No Negative values)'))
            
            reference = product_single_line[1].strip()
            reference = reference.replace("\"","")
            
            product_id = self.pool.get('product.product').search(cr, uid, [('default_code','ilike',reference)])
            
            if product_id == []:
                raise osv.except_osv(_('Product Reference error !'), _('Please select a proper product reference'))

            obj_sale_order_line = self.pool.get('sale.order.line')
            obj_product = self.pool.get('product.product').browse(cr, uid, product_id[0])

            #######################################################################
            # This is to get pricelist of product according to pricelist selected in sales order.
            price = False
            if not pricelist_id:
                raise osv.except_osv(_('Pricelist not defined !'), _('Please select a pricelist in Order Form'))
                
            else:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id.id],
                        product_id[0], int(product_single_line[0]) or 1.0, sale_browse.partner_id.id, {
                            'uom': obj_product.uom_id and obj_product.uom_id.id or False,
                            'date': sale_browse.date_order or False,
                            })[pricelist_id.id]
                #print "price ........",price
                if price is False:
                    raise osv.except_osv(_('Pricelist not defined !'), _('Cannot find a pricelist matching this product and quantity'))

            ##########################################################################
            description = ""
            description += "[" + obj_product.default_code + "]" + obj_product.name
            sale_line_id = obj_sale_order_line.create(cr, uid, {
                'product_id' : product_id[0],
                'name' : description,
                'order_id' : sale_id,
                'product_uom' : obj_product.uom_id and obj_product.uom_id.id or False,
                ##########
                'product_uom_qty' : int(product_single_line[0]),
                'price_unit' : price or 0.0 ,#obj_product.list_price,
                ##########
                'discount' : product_single_line[2],
                
            })

            #tax_id = obj_product.taxes_id[0].id
            #cr.execute('insert into sale_order_tax(order_line_id,tax_id) values(%s,%s)',(sale_line_id,tax_id))


        return True

    _columns = {
          'csv_file_sale_lines': fields.binary('CSV file', required=True),

    }


sale_order_lines()


class sale_export_xml(osv.osv):

    _name = 'sale.export.xml'

    def export_xml(self, cr, uid, ids, context=None):
        '''
        code to export all the quotation orders belonging to quantore into a xml file

        '''
        obj_sale_order = self.pool.get('sale.order')
        obj_sale_order_line = self.pool.get('sale.order.line')
        obj_partner = self.pool.get('res.partner')

        datas = []
        datas.append(['<?xml version="1.0" encoding="UTF-8" ?> '])
        datas.append(['<ORDERS>'])
        datas.append(['  <Envelop>'])
        datas.append(['    <RecordType>ENV</RecordType>'])
        datas.append(['    <SenderCodeEAN>19991</SenderCodeEAN>'])
        datas.append(['        <SenderCode>19991</SenderCode>'])
        datas.append(['    <SenderName>TLV2 Test account</SenderName>'])
        datas.append(['    <RecipientCodeEAN>QUANTORE</RecipientCodeEAN>'])
        datas.append(['    <TestIndicator>0</TestIndicator>'])
        datas.append(['    <CreationDate>20101112</CreationDate>'])
        datas.append(['    <CreationTime>114024</CreationTime>'])
        datas.append(['    <MessageTypeCode>SALORD</MessageTypeCode>'])
        datas.append(['    <MessageVersion>2.0</MessageVersion>'])

        partner_ids = obj_partner.search(cr, uid, [('qt_number','<>','')])
        for partner_id in partner_ids:
            sale_ids = obj_sale_order.search(cr, uid, [('state','=','draft'),('partner_id','=',partner_id)],order='date_order')
            for sale_order_id in sale_ids:
                obj_sale_quantore = obj_sale_order.browse(cr, uid, sale_order_id)
                datas.append(['     <OrderHeader>'])
                datas.append(['        <RecordType>ORH</RecordType>'])
                datas.append(['        <SupplierCode>QUANTORE</SupplierCode>'])
                datas.append(['        <CustomerCode>'+ str(obj_sale_quantore.partner_id.ref)  +'</CustomerCode>'])
                datas.append(['        <OrderCode>' + str(obj_sale_quantore.name)+ '</OrderCode>'])
                datas.append(['        <DelAddressCode>123</DelAddressCode>'])
                datas.append(['        <OrderDate>' + str(obj_sale_quantore.date_order) + '</OrderDate> '])
                datas.append(['        <DelDate>' + str(obj_sale_quantore.date_order) + '</DelDate>'])
                datas.append(['        <Contact>' + str(obj_sale_quantore.partner_invoice_id.name) + '</Contact>'])
                datas.append(['        <Reference1>REF 1</Reference1>'])
                datas.append(['        <Reference2>REF 2</Reference2>'])
                datas.append(['        <DelAddressName1>' + str(obj_sale_quantore.partner_invoice_id.name) + '</DelAddressName1>'])
                datas.append(['        <DelAddressName2>' + str(obj_sale_quantore.partner_invoice_id.name) + '</DelAddressName2>'])
                datas.append(['        <DelAddressStreet1>' + str(obj_sale_quantore.partner_invoice_id.street) + '</DelAddressStreet1>'])
                datas.append(['        <DelAddressStreet2>' + str(obj_sale_quantore.partner_invoice_id.street2) + '</DelAddressStreet2>'])
                datas.append(['        <DelAddressZipcode>' + str(obj_sale_quantore.partner_invoice_id.zip) + '</DelAddressZipcode>'])
                datas.append(['        <DelAddressCity>' + str(obj_sale_quantore.partner_invoice_id.city) + '</DelAddressCity> '])
                datas.append(['        <DelAddressCountryCode></DelAddressCountryCode>'])
                datas.append(['        <CustomerName1></CustomerName1>'])
                datas.append(['        <DelAddressBC>C</DelAddressBC>'])
                datas.append(['        <OrderProcessCode>KLO</OrderProcessCode>  '])
                i = 1
                for obj_sale_order_lines in obj_sale_quantore.order_line:

                    datas.append(['          <OrderLine>'])
                    datas.append(['            <RecordType>ORL</RecordType>'])
                    datas.append(['            <SupplierCode>QUANTORE</SupplierCode>'])
                    datas.append(['            <OrderCode>' + str(obj_sale_quantore.name)+ '</OrderCode>'])
                    datas.append(['            <OrderLineNumber>' + str(i)+ '</OrderLineNumber>'])
                    datas.append(['            <ProductCodeSupplier>XYZ</ProductCodeSupplier>'])
                    datas.append(['            <ProductDescription1>' + str(obj_sale_order_lines.name)+ '</ProductDescription1>'])
                    datas.append(['            <Quantity>' + str(obj_sale_order_lines.product_uom_qty) +'</Quantity>'])
                    datas.append(['            <DelDate>' + str(obj_sale_quantore.date_order) + '</DelDate>'])
                    datas.append(['            <Memo>ABC</Memo>'])
                    datas.append(['          </OrderLine>'])
                    i += 1


                datas.append(['     </OrderHeader>'])


        datas.append(['  </Envelop>'])
        datas.append(['</ORDERS>'])




        test_data = ''
        for data in datas:
            test_data += data[0] + "\n"

        out = base64.encodestring(test_data)
        string = ""
        string = 'Quantore_Orders.xml'#+'-'+ time.strftime('%Y-%m-%d %H:%M:%S')+'.xml'


        return self.write(cr, uid, ids, {'state':'get', 'xml_sale_order':out,'name': string})




    _columns = {
        'name' : fields.char('Name',size=32),
        'xml_sale_order' : fields.binary('XML file'),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),

    }

sale_export_xml()
