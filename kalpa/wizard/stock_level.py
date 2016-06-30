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
import psycopg2
import sys
import pprint
from StringIO import StringIO
import cStringIO
import base64
import csv
class stock_level(osv.osv_memory):
    """ Import Stock Moves """

    _name = "stock.level"

    _description = "Import Stock Level"

    _columns = {
          'name':fields.char('Name',size=64),
          'csv_file': fields.binary('CSV file'),
          'stock_csv_export': fields.binary('Stock CSV file'),
          'location_id':fields.many2one('stock.location','Location')
    }
#    def main():
##	conn_string = "host='localhost' dbname='kalpa9sep' user='openerp' password='openerp' port='5432'"
##	# print the connection string we will use to connect
##	#print "Connecting to database\n	->%s" % (conn_string)
##
##	# get a connection, if a connect cannot be made an exception will be raised here
##	conn = psycopg2.connect(conn_string)
##
##	# conn.cursor will return a cursor object, you can use this cursor to perform queries
#	cursor = cr
##
##	# execute our Query
#	cr.execute("SELECT id,name FROM stock_location where id=78")
#
#	# retrieve the records from the database
#	records = cursor.fetchall()
#	STOCK_IN = 0
#	STOCK_OUT = 0
#	STOCK_IN11 = 0
#	STOCK_OUT11 = 0
#	data_list = []
#	data_dict = {}
#	count = 0
#	for loc in records:
#		data_val = (str(loc[1]),"STOCK_IN","STOCK_OUT","RESULT","REMAINING QTY")
#		data_list.append(data_val)
#		qry1 = "select product_id,sum(product_qty) from stock_move group by product_id, "\
#		"location_dest_id having location_dest_id=%s order by product_id" %(loc[0],)
#		cursor.execute(qry1)
#		temp1 = cursor.fetchall()
#		STOCK_IN = 0
#		STOCK_OUT = 0
#		rem = 0
#		for val1 in temp1:
#			count += 1
#			STOCK_IN = 0
#			STOCK_OUT = 0
#			rem = 0
#			if val1 and len(val1) > 0 and val1[1] != None:
#				if data_dict.has_key(str(val1[0])):
#					data_dict[str(val1[0])]['STOCK_IN'] = data_dict[str(val1[0])]['STOCK_IN'] + val1[1]
#				else:
#					data_dict[str(val1[0])] = {'STOCK_IN':val1[1]}
#			else:
#				if data_dict.has_key(str(val1[0])):
#					data_dict[str(val1[0])]['STOCK_IN'] = data_dict[str(val1[0])]['STOCK_IN'] + 0
#				else:
#					data_dict[str(val1[0])] = {'STOCK_IN':0}
#
#
#			qry2 = "select sum(product_qty) from stock_move group by location_id, product_id "\
#			"having location_id=%s and product_id=%s" %(loc[0],val1[0])
#			cursor.execute(qry2)
#			temp2 = cursor.fetchall()
#			if temp2 and len(temp2)>0:
#				for val2 in temp2:
#					if val2 and len(val2) > 0 and val2[0] != None:
#						if data_dict.has_key(str(val1[0])):
#							if data_dict[str(val1[0])].has_key('STOCK_OUT'):
#								data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + val2[0]
#							else:
#								data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':val2[0]}
#					else:
#						if data_dict.has_key(str(val1[0])):
#							if data_dict[str(val1[0])].has_key('STOCK_OUT'):
#								data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + 0
#							else:
#								data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':0}
#			else:
#				if data_dict.has_key(str(val1[0])):
#					if data_dict[str(val1[0])].has_key('STOCK_OUT'):
#						data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + 0
#					else:
#						data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':0}
#
#
#			qry3 = "select pd.default_code, pd.default_code || ' ' || tm.name from stock_move as sm left join product_product as pd on (sm.product_id=pd.id) "\
#			"left join product_template as tm on (pd.product_tmpl_id=tm.id) where sm.location_dest_id=%s and "\
#			"sm.product_id=%s" %(loc[0],val1[0])
#			cursor.execute(qry3)
#			temp3 = cursor.fetchall()
#			for val3 in temp3:
#				if data_dict.has_key(str(val1[0])):
#					if data_dict[str(val1[0])].has_key('CODE'):
#						data_dict[str(val1[0])]['CODE'] = val3[0]
#					else:
#						data_dict[str(val1[0])] = {'CODE':val3[0],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT']}
#
#				if data_dict.has_key(str(val1[0])):
#					if data_dict[str(val1[0])].has_key('NAME'):
#						data_dict[str(val1[0])]['NAME'] = val3[1]
#					else:
#						data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':val3[1],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT']}
#
#
#			qry4 = "select sum(rem_product_qty) from stock_move group by product_id, location_dest_id having "\
#			"location_dest_id=%s and product_id=%s" %(loc[0],val1[0])
#			cursor.execute(qry4)
#			temp4 = cursor.fetchall()
#
#			for val4 in temp4:
#				if val4 and len(val4) > 0 and val4[0] != None:
#					if data_dict.has_key(str(val1[0])):
#						if data_dict[str(val1[0])].has_key('REM'):
#							data_dict[str(val1[0])]['REM'] = data_dict[str(val1[0])]['REM'] + val4[0]
#						else:
#							data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':data_dict[str(val1[0])]['NAME'],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT'],'REM':val4[0]}
#				else:
#					if data_dict.has_key(str(val1[0])):
#						if data_dict[str(val1[0])].has_key('REM'):
#							data_dict[str(val1[0])]['REM'] = data_dict[str(val1[0])]['REM'] + 0
#						else:
#							data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':data_dict[str(val1[0])]['NAME'],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT'],'REM':0}
#
#
#		for val1 in temp1:
#			data_val = (data_dict[str(val1[0])]['CODE'],data_dict[str(val1[0])]['NAME'],data_dict[str(val1[0])]['STOCK_IN'],data_dict[str(val1[0])]['STOCK_OUT'],data_dict[str(val1[0])]['STOCK_IN']-data_dict[str(val1[0])]['STOCK_OUT'],data_dict[str(val1[0])]['REM'])
#			data_list.append(data_val)
#
#		qry11 = "select CASE WHEN location_dest_id=%s THEN sum(Product_qty) ELSE 0 END AS STOCK_IN, "\
#		"CASE WHEN location_id=%s THEN sum(product_qty) ELSE 0 END AS STOCK_OUT from stock_move group "\
#		"by location_dest_id, location_id having location_id=%s or location_dest_id=%s" % (loc[0],loc[0],loc[0],loc[0])
#		cursor.execute(qry11)
#		temp11 = cursor.fetchall()
#
#		for val11 in temp11:
#			STOCK_IN11 += val11[0]
#			STOCK_OUT11 += val11[1]
#
#		qry21 = "select sum(rem_product_qty) from stock_move where location_dest_id=%s" %(loc[0],)
#		cursor.execute(qry21)
#		temp21 = cursor.fetchall()
#
#		for val21 in temp21:
#			rem11 = val21[0]
#
#
#		if STOCK_IN11 or STOCK_OUT11:
#			data_val = (str(loc[1]),STOCK_IN11,STOCK_OUT11,STOCK_IN11 - STOCK_OUT11,rem11)
#			data_list.append(data_val)
#			data_val = ('','','','','','')
#			data_list.append(data_val)
#			data_val = ('','','','','','')
#			data_list.append(data_val)
#			STOCK_IN11 = 0
#			STOCK_OUT11 = 0
#			rem11 = 0
#
#
#	import csv
#	fp = open('/tmp/final.csv', 'wb')
#	a = csv.writer(fp, delimiter=',')
#	a.writerows(data_list)
#
#	# print out the records using pretty print
#	# note that the NAMES of the columns are not shown, instead just indexes.
#	# for most people this isn't very useful so we'll show you how to return
#	# columns as a dictionary (hash) in the next example.
#
#	print "EVERY THING WORKING"

    def stock_csv(self, cr, uid, ids, context):
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
	cursor = cr
        data=self.browse(cr,uid,ids)
        
	# execute our Query
        buf=cStringIO.StringIO()
        writer=csv.writer(buf, 'UNIX')
	cursor.execute("SELECT id,name FROM stock_location where id=%s",(tuple([data[0].location_id.id]),))

	# retrieve the records from the database
	records = cursor.fetchall()
	STOCK_IN = 0
	STOCK_OUT = 0
	STOCK_IN11 = 0
	STOCK_OUT11 = 0
	data_list = []
	data_dict = {}
	count = 0
	for loc in records:
            data_val = (str(loc[1]),"STOCK_IN","STOCK_OUT","RESULT","REMAINING QTY")
            data_list.append(data_val)
            qry1 = "select product_id,sum(product_qty) from stock_move group by product_id, "\
            "location_dest_id having location_dest_id=%s order by product_id" %(loc[0],)
            cursor.execute(qry1)
            temp1 = cursor.fetchall()
            STOCK_IN = 0
            STOCK_OUT = 0
            rem = 0
            for val1 in temp1:
                    count += 1
                    STOCK_IN = 0
                    STOCK_OUT = 0
                    rem = 0
                    if val1 and len(val1) > 0 and val1[1] != None:
                            if data_dict.has_key(str(val1[0])):
                                    data_dict[str(val1[0])]['STOCK_IN'] = data_dict[str(val1[0])]['STOCK_IN'] + val1[1]
                            else:
                                    data_dict[str(val1[0])] = {'STOCK_IN':val1[1]}
                    else:
                            if data_dict.has_key(str(val1[0])):
                                    data_dict[str(val1[0])]['STOCK_IN'] = data_dict[str(val1[0])]['STOCK_IN'] + 0
                            else:
                                    data_dict[str(val1[0])] = {'STOCK_IN':0}


                    qry2 = "select sum(product_qty) from stock_move group by location_id, product_id "\
                    "having location_id=%s and product_id=%s" %(loc[0],val1[0])
                    cursor.execute(qry2)
                    temp2 = cursor.fetchall()
                    if temp2 and len(temp2)>0:
                            for val2 in temp2:
                                    if val2 and len(val2) > 0 and val2[0] != None:
                                            if data_dict.has_key(str(val1[0])):
                                                    if data_dict[str(val1[0])].has_key('STOCK_OUT'):
                                                            data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + val2[0]
                                                    else:
                                                            data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':val2[0]}
                                    else:
                                            if data_dict.has_key(str(val1[0])):
                                                    if data_dict[str(val1[0])].has_key('STOCK_OUT'):
                                                            data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + 0
                                                    else:
                                                            data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':0}
                    else:
                            if data_dict.has_key(str(val1[0])):
                                    if data_dict[str(val1[0])].has_key('STOCK_OUT'):
                                            data_dict[str(val1[0])]['STOCK_OUT'] = data_dict[str(val1[0])]['STOCK_OUT'] + 0
                                    else:
                                            data_dict[str(val1[0])] = {'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':0}


                    qry3 = "select pd.default_code, pd.default_code || ' ' || tm.name from stock_move as sm left join product_product as pd on (sm.product_id=pd.id) "\
                    "left join product_template as tm on (pd.product_tmpl_id=tm.id) where sm.location_dest_id=%s and "\
                    "sm.product_id=%s" %(loc[0],val1[0])
                    cursor.execute(qry3)
                    temp3 = cursor.fetchall()
                    for val3 in temp3:
                            if data_dict.has_key(str(val1[0])):
                                    if data_dict[str(val1[0])].has_key('CODE'):
                                            data_dict[str(val1[0])]['CODE'] = val3[0]
                                    else:
                                            data_dict[str(val1[0])] = {'CODE':val3[0],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT']}

                            if data_dict.has_key(str(val1[0])):
                                    if data_dict[str(val1[0])].has_key('NAME'):
                                            data_dict[str(val1[0])]['NAME'] = val3[1]
                                    else:
                                            data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':val3[1],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT']}


                    qry4 = "select sum(rem_product_qty) from stock_move group by product_id, location_dest_id having "\
                    "location_dest_id=%s and product_id=%s" %(loc[0],val1[0])
                    cursor.execute(qry4)
                    temp4 = cursor.fetchall()

                    for val4 in temp4:
                            if val4 and len(val4) > 0 and val4[0] != None:
                                    if data_dict.has_key(str(val1[0])):
                                            if data_dict[str(val1[0])].has_key('REM'):
                                                    data_dict[str(val1[0])]['REM'] = data_dict[str(val1[0])]['REM'] + val4[0]
                                            else:
                                                    data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':data_dict[str(val1[0])]['NAME'],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT'],'REM':val4[0]}
                            else:
                                    if data_dict.has_key(str(val1[0])):
                                            if data_dict[str(val1[0])].has_key('REM'):
                                                    data_dict[str(val1[0])]['REM'] = data_dict[str(val1[0])]['REM'] + 0
                                            else:
                                                    data_dict[str(val1[0])] = {'CODE':data_dict[str(val1[0])]['CODE'],'NAME':data_dict[str(val1[0])]['NAME'],'STOCK_IN':data_dict[str(val1[0])]['STOCK_IN'],'STOCK_OUT':data_dict[str(val1[0])]['STOCK_OUT'],'REM':0}


            for val1 in temp1:
                    data_val = (data_dict[str(val1[0])]['CODE'],data_dict[str(val1[0])]['NAME'],data_dict[str(val1[0])]['STOCK_IN'],data_dict[str(val1[0])]['STOCK_OUT'],data_dict[str(val1[0])]['STOCK_IN']-data_dict[str(val1[0])]['STOCK_OUT'],data_dict[str(val1[0])]['REM'])
                    data_list.append(data_val)

            qry11 = "select CASE WHEN location_dest_id=%s THEN sum(Product_qty) ELSE 0 END AS STOCK_IN, "\
            "CASE WHEN location_id=%s THEN sum(product_qty) ELSE 0 END AS STOCK_OUT from stock_move group "\
            "by location_dest_id, location_id having location_id=%s or location_dest_id=%s" % (loc[0],loc[0],loc[0],loc[0])
            cursor.execute(qry11)
            temp11 = cursor.fetchall()

            for val11 in temp11:
                    STOCK_IN11 += val11[0]
                    STOCK_OUT11 += val11[1]

            qry21 = "select sum(rem_product_qty) from stock_move where location_dest_id=%s" %(loc[0],)
            cursor.execute(qry21)
            temp21 = cursor.fetchall()

            for val21 in temp21:
                    rem11 = val21[0]


            if STOCK_IN11 or STOCK_OUT11:
                    data_val = (str(loc[1]),STOCK_IN11,STOCK_OUT11,STOCK_IN11 - STOCK_OUT11,rem11)
                    data_list.append(data_val)
                    data_val = ('','','','','','')
                    data_list.append(data_val)
                    data_val = ('','','','','','')
                    data_list.append(data_val)
                    STOCK_IN11 = 0
                    STOCK_OUT11 = 0
                    rem11 = 0


	
	fp = open('/home/final.csv', 'wb')
	a = csv.writer(fp, delimiter=',')
	a.writerows(data_list)
        
        
#        for data in data_list:
#            row = []
        for d in data_list:
            writer.writerow(d)
#            if isinstance(d, basestring):
#                d = d.replace('\n',' ').replace('\t',' ')
#                try:
#                    d = d.encode('utf-8')
#                except:
#                    pass
#            if d is False: d = None
#            row.append(d)
#        writer.writerow(row)
        
        out=base64.encodestring(buf.getvalue())
        buf.close()

#        return True
#        out=base64.encodestring(buf.getvalue())
	# print out the records using pretty print
	# note that the NAMES of the columns are not shown, instead just indexes.
	# for most people this isn't very useful so we'll show you how to return
	# columns as a dictionary (hash) in the next example.

#	print "EVERY THING WORKING"
        string = ''
        string = "Location Details.csv"
#
        self.write(cr, uid, ids, {'stock_csv_export':out,'name':string})
        return {
          	'name':_("Export CSV"),
          	'view_mode': 'form',
          	'view_id': False,
          	'view_type': 'form',
          	'res_model': 'stock.level',
          	'res_id':ids[0],
          	'type': 'ir.actions.act_window',
          	'target': 'current',
          	'context': context,
          	'no_destroy':True,
          	}

    def stock_level_change(self, cr, uid, ids, context):

        '''
        Code to import csv and generate prepare stock move for stock/inventory
        '''
        stock_move_picking_id=''
        stock_move_obj=self.pool.get('stock.move')
        product_obj=self.pool.get('product.product')
        location_obj=self.pool.get('stock.location')
        res_obj=self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking.out')
        data = self.browse(cr, uid, ids[0])
        if not data.csv_file:
            raise osv.except_osv(_('CSV Error !'), _('Please select a .csv file'))
        module_data = data.csv_file
        val = base64.decodestring(module_data)
        i=0
        product_inv_data = val.split("\n")
        loc_id = active_id = ''
        count=1
        for row in product_inv_data:
#            try:
        
            prod_data_fields = row.split(",")

#            logger.error('row %s', row)
#            continue
            if i==0:
                i = i + 1
                location_name=prod_data_fields[0].replace('"','')
                continue
            i = i + 1
            if i > 1:
                prod_data=prod_data_fields
                product_default_code=prod_data[0].replace('"','')        
                product_id=product_obj.search(cr,uid,[('default_code','=',product_default_code)])
                if product_id:
                    product_data=product_obj.browse(cr,uid,product_id[0])
                    if prod_data_fields[4].replace('"','')==prod_data_fields[5].replace('"',''):
                        i = i + 1
                        continue

                    qty=float(prod_data_fields[4].replace('"','')) - float(prod_data_fields[5].replace('"',''))
                   
                    location_dest_id=location_obj.search(cr,uid,[('name','=','Inventory loss')])
                    location_id=location_obj.search(cr,uid,[('name','=','ngein')])
                    location_sourse_id=location_obj.search(cr,uid,[('name','=',location_name)])
                    res_id=res_obj.search(cr,uid,[('name','=','location_name')])
                    stock_picking_id = stock_move_obj.search(cr, uid, [('product_id','=',product_data.id),('location_id','=',location_sourse_id[0])])
                    # for stock_move in stock_move_obj.browse(cr,uid,stock_picking_id):
                    if stock_picking_id:
                        stock_move = stock_move_obj.browse(cr,uid,stock_picking_id[0])
                        if stock_move.picking_id:
                            stock_move_picking_id=stock_move.picking_id.id
                        # continue
                    else:  
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                'location_id' : location_sourse_id[0],
                                'type' : 'internal',
                        })
                        stock_move_picking_id = picking_id
                                # continue
                    # if stock_move_picking_id:
                    # print"==picking_id==",stock_move_picking_id
                    
                    if qty>0:
                        val={
                            'product_id' : product_data.id,
                            'product_uom' : product_data.product_tmpl_id.uom_id.id,
                            'name' : product_data.name,
                            'product_qty' : qty,
                            'location_id' : location_sourse_id[0],##Source Location--consignment location
                            'location_dest_id':location_dest_id[0],##'Destination Location' -- inventory loss
                            'user_id':1,
                            'partner_id':1,
                            'state':'done',
                            'picking_id':stock_move_picking_id
                        }
                        stock_move_id = stock_move_obj.create(cr ,uid,val)
                    elif qty < 0:
                        qty=qty*(-1)
                        for stock_move in stock_move_obj.browse(cr,uid,stock_picking_id):
                            if stock_move.product_qty == qty :
                                stock_move_obj.write(cr,uid,stock_move.id,{'location_id':location_id[0]})
                                break
                            elif stock_move.product_qty < qty :
                                qty -=  stock_move.product_qty
                                stock_move_obj.write(cr,uid,stock_move.id,{'location_id':location_id[0]})
                            if qty < 1:
                                break;
        return True

#####new_new_new_server_update
stock_level()











