# To change this template, choose Tools | Templates
# and open the template in the editor.

import time
import datetime
from datetime import date, timedelta
import thread
import threading
from cStringIO import StringIO
from dateutil import parser

from report import report_sxw

class return_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(return_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'returned_moves' : self._returned_moves,
            'split_date' : self._split_date,
            'get_returned_quantity' : self._get_return_qty,
            'get_present_date' : self._get_present_date,
            'direct_debit' : self._direct_debit,
        })

    def _direct_debit(self, o):
        if o.partner_id.per_kalpa:
            return "ja"
        else:
            return "nee"

    def _get_present_date(self):

        present_date = time.strftime('%d %b %Y')
        return present_date 

    def _get_return_qty(self,o):

        d = date.today()-timedelta(days=365)
        d = str(d)

        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        total_quantity = 0
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_id','=',o.id),('state','=','done'),('date_products_return','>=',d)], order="product_reference")
            for ob in object_move:
                x = self.pool.get('stock.move').browse(self.cr, self.uid, ob)
                total_quantity+= x.rem_product_qty
        return total_quantity


    def _split_date(self,line):
        date_time = line.date_products_return
        date_part = date_time.split(' ')
        new_date = date_part[0].strip()
        parse_date = parser.parse(new_date) # to convert from string to datetime
        formatted_date = parse_date.strftime("%d-%b-%Y") # to change the format of date
        return formatted_date

    def _returned_moves(self, o):


        d = date.today()-timedelta(days=365)
        d = str(d)

        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_id','=',o.id),('state','=','done'),('date_products_return','>=',d)], order="product_reference")

            if len(object_move):
                for ob in object_move:
                    move_ids.append(ob)

        if o.id:
            list_move_ids = move_ids

            list_move_ids = self.pool.get('stock.move').search(self.cr, self.uid, [('id','in',list_move_ids)], order="date_products_return desc,product_reference asc")
            objects_moves = self.pool.get('stock.move').browse(self.cr, self.uid, list_move_ids)

            return objects_moves
        else:
            return None
        



report_sxw.report_sxw('report.stock.return', 'stock.location', 'addons/kalpa/report/stock_return_report.rml', parser=return_move)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shift
