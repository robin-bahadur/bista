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


class stock_change_price(osv.osv_memory):
    _name = "stock.change.price"
    _description = "Change Price"


    def change_price(self, cr, uid, ids, context=None):

        """ to change the consignment price of a specific
        move in the consignment locations """

        print "ids",ids
        stock_move_id = context.get('active_id')
        obj_stock_move = self.pool.get('stock.move').browse(cr, uid, stock_move_id)
        quantity = obj_stock_move.rem_product_qty

        obj_change_price = self.browse(cr, uid, ids[0])
        change_consignment_price = obj_change_price.change_consignment_price
        change_public_price = obj_change_price.change_public_price
        
        if (change_consignment_price>0 and change_public_price>0):
            return_value1 = obj_stock_move.write({
                'consignment_price': change_consignment_price,
                'product_public_price' : change_public_price,
                'product_total' : change_consignment_price * quantity,
            })
            location_dest_id = obj_stock_move.location_dest_id.id
            obj_location = self.pool.get('stock.location').browse(cr, uid, location_dest_id)
            return_value2 = obj_location.consignment_gross_total()
            print "Return Value",return_value2
            return {'type': 'ir.actions.act_window_close'}
        else:
            return {'type': 'ir.actions.act_window_close'}


    def _get_price(self, cr, uid, context=None):

        
        stock_move_id = context.get('active_id')
        obj_stock_move = self.pool.get('stock.move').browse(cr, uid, stock_move_id)
        print "Remaining quantity",obj_stock_move.consignment_price

        return obj_stock_move.consignment_price

    def _get_public_price(self, cr, uid, context=None):

        stock_move_id = context.get('active_id')
        obj_stock_move = self.pool.get('stock.move').browse(cr, uid, stock_move_id)
        
        return obj_stock_move.product_public_price
         

    _columns = {
        'change_consignment_price' : fields.float('Consignment Price'),
        'change_public_price' : fields.float('Public Price'),

    }

#    _sql_constraints = [
#        ('check_consign_price',"CHECK ( change_consignment_price  > 0 )", "Consignment price should be greater than zero"),
#        ('check_no_of_days', "CHECK ( change_public_price  > 0 )", "Public price should be greater than zero"),
#
#    ]

    _defaults = {
        'change_consignment_price' : _get_price,
        'change_public_price' : _get_public_price,
    }
stock_change_price()