from osv import fields, osv
from tools.translate import _

import decimal_precision as dp
import time
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule



class consignment_price(osv.osv_memory):
    _name = "consignment.price"
    _description = "Consignment Price Change"

    def return_price(self, cr, uid, ids, context):
        
        active_id=context['active_id']
        cons_price=[]
        move_ids=self.pool.get('stock.location').browse(cr,uid,active_id).move_id
        if move_ids:
            i= 0
            for each_move in move_ids:
                kalpa_cons_price = each_move.product_id.kalpa_consignment_price
                product_public_price = each_move.product_id.kalpa_public_price
                product_total = each_move.rem_product_qty * kalpa_cons_price
                cons_price.append(kalpa_cons_price)
                cr.execute("UPDATE stock_move SET consignment_price=%s,product_public_price=%s,product_total=%s WHERE id=%s"%(kalpa_cons_price,product_public_price,product_total,each_move.id))
                cr.commit()
                i+=1
        return {'type': 'ir.actions.act_window_close'}

consignment_price()
