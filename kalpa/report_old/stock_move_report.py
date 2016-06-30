# To change this template, choose Tools | Templates
# and open the template in the editor.

import time
import datetime
from datetime import date, timedelta
import thread
import threading
from cStringIO import StringIO
from dateutil import parser
import decimal

from report import report_sxw

class move1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(move1, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'string' : '53233X',
            'get_dates' : self._get_dates,
            'consignment_lines' : self._get_consignment_lines,
            'net_total' : self._net_total,
            'split_date' : self._split_date,
            'latest_consignment' : self._latest_consignment,
            'get_newconsignment_quantity' : self._get_new_qty,
            'get_all_consignment_quantity' : self._get_qty,
            'split_date' : self._split_date,
            'get_present_date' : self._get_present_date,
            'net_total_tax' : self._net_total_tax,
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

    def _split_date(self, line):

        date_move = line.date
        date_parts = date.split('')
        return date_parts[0]

    def _get_qty(self,o):


        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        total_quantity = 0
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0)], order="product_reference")
            for ob in object_move:
                x = self.pool.get('stock.move').browse(self.cr, self.uid, ob)
                total_quantity+= x.rem_product_qty

        return total_quantity


    def _get_new_qty(self,o):

        d = date.today()-timedelta(days=7)
        d = str(d)

        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        total_quantity = 0
        
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0),('date','>=',d)], order="product_reference")
            
            for ob in object_move:
                x = self.pool.get('stock.move').browse(self.cr, self.uid, ob)
                total_quantity+= x.rem_product_qty

        return total_quantity

    def _latest_consignment(self,o):


        d = date.today()-timedelta(days=7)
        d = str(d)


        result = {}
        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0),('date','>=',d)], order="product_reference")
            for ob in object_move:
                x = self.pool.get('stock.move').browse(self.cr, self.uid, ob)

            if len(object_move):
                for ob in object_move:
                    move_ids.append(ob)

        if o.id:

            list_move_ids = move_ids

            list_move_ids = self.pool.get('stock.move').search(self.cr, self.uid, [('id','in',list_move_ids)], order="product_reference")
            objects_moves = self.pool.get('stock.move').browse(self.cr, self.uid, list_move_ids)
            return objects_moves
        else:
            return False

        




    def _split_date(self,line):

        date_time = line.picking_date
        date_part = date_time.split(' ')
        new_date = date_part[0].strip()
        parse_date = parser.parse(new_date) # to convert from string to datetime
        formatted_date = parse_date.strftime("%d-%b-%Y") # to change the format of date
        return formatted_date

    def _get_dates(self,o):
        return_date = time.strftime('%d %b %Y')

        return return_date


    def _net_total_tax(self,o):

        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        net_total = 0

        for pid in picking_ids:
            object_move_id = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0)])
            obj_stock_move = self.pool.get('stock.move').browse(self.cr, self.uid, object_move_id)

            if len(obj_stock_move)>0:
                for move in obj_stock_move:
                    net_total += move.product_total
        net_total = round(net_total,2)
        return net_total
    
    def _net_total(self,o):
        
        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        net_total = 0
        for pid in picking_ids:
            object_move_id = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0)])
            obj_stock_move = self.pool.get('stock.move').browse(self.cr, self.uid, object_move_id)
            
            if len(obj_stock_move)>0:
                for move in obj_stock_move:
                    net_total += move.product_total
#        net_total = round(net_total,2)
        net_total1 = str(net_total)
        d=decimal.Decimal(net_total1)
        q = decimal.Decimal('0.00')
        x = d.quantize(q)
        return x


    def _get_consignment_lines(self,o):

        '''
         to every time return an object of internal Move pertaining to that location
        '''

        result = {}
        picking_ids = self.pool.get('stock.picking').search(self.cr, self.uid ,[('type','=','internal')])
        move_ids = []
        for pid in picking_ids:
            object_move = self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',pid),('location_dest_id','=',o.id),('state','=','done'),('rem_product_qty','>',0)], order="product_reference")
            for ob in object_move:
                x = self.pool.get('stock.move').browse(self.cr, self.uid, ob)

            if len(object_move):
                for ob in object_move:
                    move_ids.append(ob)

        if o.id:

            list_move_ids = move_ids
            list_move_ids = self.pool.get('stock.move').search(self.cr, self.uid, [('id','in',list_move_ids)], order="product_reference")
            objects_moves = self.pool.get('stock.move').browse(self.cr, self.uid, list_move_ids)

            return objects_moves
        else:
            return False



report_sxw.report_sxw('report.stock.location', 'stock.location', 'addons/kalpa/report/stock_picking_move.rml', parser=move1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shift
