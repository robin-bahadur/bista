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

from osv import fields, osv
from tools.translate import _

import decimal_precision as dp
import time
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule



class stock_old_consignment(osv.osv_memory):
    _name = "stock.old.consignment"
    _description = "Old Consignment"


    def return_products(self, cr, uid, ids, context):

        ''' Function to return the products by Transferring it from Consignment Location to the
        Stock Location '''

        obj_return_products = self.browse(cr, uid, ids[0])
        if not obj_return_products.destination_location:
            raise osv.except_osv(_('Destination Location Error !'), _('Please select a proper destination Location'))

        obj_stock_move = self.pool.get('stock.move')
        obj_picking = self.pool.get('stock.picking')
        location_id = context.get('active_id')
        picking_id = obj_picking.create(cr, uid, {'type' : 'internal'})
        print "Picking ID",picking_id
        print "location id",location_id

        obj_internal_ids = obj_stock_move.search(cr, uid, [('location_dest_id','=',location_id),('state_add','=','yes')])
        print "obj_internal_ids" , obj_internal_ids

        for eachid in obj_internal_ids:
            obj_each_internal_move = obj_stock_move.browse(cr, uid, eachid)
            stock_id = obj_stock_move.create(cr, uid, {
                'product_id' : obj_each_internal_move.product_id.id,
                'name' : obj_each_internal_move.product_id.name,
                'location_id' : location_id,
                'picking_id' : picking_id,
                'product_uom' : obj_each_internal_move.product_uom.id,
                'product_reference' : obj_each_internal_move.product_reference,
                'product_category1' : obj_each_internal_move.product_category1.id,
                'product_public_price' : obj_each_internal_move.product_public_price,
                'product_total' : obj_each_internal_move.product_total,
                'consignment_price' : obj_each_internal_move.consignment_price,
                'product_qty' : obj_each_internal_move.rem_product_qty,
                'location_dest_id' : obj_return_products.destination_location.id,
                'rem_product_qty' : obj_each_internal_move.rem_product_qty,
                'date_products_return' : time.strftime("%Y-%m-%d"),
            })
            return_value = obj_each_internal_move.write({'rem_product_qty': 0,'state_add': 'no' })

        picking_name =  obj_picking.browse(cr, uid, picking_id).name
        message = _("Products have been returned to Picking %s") % (picking_name,)
        obj_picking.log(cr, uid, picking_id, message)

        status_delivery = obj_picking.action_done(cr, uid, [picking_id])
        print "status delivery",status_delivery

        return True




    _columns = {
        'source_location' : fields.char('Source Location', size=32, readonly=True),
        'destination_location' : fields.many2one('stock.location','Destination Location'),
        'csv_file_stock_old_lines': fields.binary('CSV file', required=True),

    }



stock_old_consignment()