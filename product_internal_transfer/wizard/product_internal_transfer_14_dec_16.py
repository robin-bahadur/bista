from osv import fields, osv
from tools.translate import _
#import xlrd
#import StringIO
import base64
from datetime import datetime
import re
import time
import csv
import StringIO as baseStringIO
from cStringIO import StringIO as csIO

class product_internal_transfer(osv.osv_memory):
    
    _name = 'product.internal.transfer'
    _columns = {
                'import_file':fields.binary('Choose Excel File (.csv)'),
                'filename':fields.char('File name'),
}

    csv.register_dialect(
        'mydialect',
        delimiter = ',',
        quotechar = '"',
        doublequote = True,
        skipinitialspace = True,
        lineterminator = '\r\n',
        quoting = csv.QUOTE_MINIMAL)
    
    
    def imp_file(self, cr, uid, ids,context):
        """ function to import bank statement csv file  """
        picking_obj = self.pool.get('stock.picking')
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        stock_move_obj = self.pool.get('stock.move')
        stock_move_lines = {}
        date =  datetime.now()
        date_expected = datetime.now()
        src_location_id = ''
        if isinstance(ids,list):
            ids= ids[0]
        #  file_data = self.browse(cr,uid,ids).import_file
        # filename= self.browse(cr,uid,ids).filename
        col = 0
        csvfile = self.browse(cr,uid,ids).import_file
        if csvfile:
            csvfile = base64.b64decode(csvfile)                 
            for row in csv.reader(csIO(csvfile),dialect='mydialect'): # reading data from csv 
                qty = 0.0
                if len(row):
                    row_count = len(row)
                    while row_count >= 0:
                        row_count = row_count -1
                        if row_count == -1:
                            row_count=0
                            break
                        
                        value = row[row_count]
                        if row_count==0 and value and col >= 1:
                            source_location = value
                            src_location_id = location_obj.search(cr,uid,[('name', 'ilike',source_location)])
                            if not src_location_id:
                                raise osv.except_osv(_('Warning!'), _(' "%s" Soucre location doesnot exist in openerp \n' \
                                            'Please check in csv line no "%s" ') % (source_location, col+1))
                        else:                    
                            if row_count==0 and value != True and col >= 1:
                                raise osv.except_osv(_('Warning!'), _('Please Enter a Source Location in csv \n' \
                                            'Please check in csv line no "%s" ') % (col+1))

                        if row_count==1 and value and col >= 1:
                            destination_location = value
                            dest_location_id = location_obj.search(cr,uid,[('name', 'ilike',destination_location)])
                            if not dest_location_id:
                                raise osv.except_osv(_('Warning!'), _(' "%s" Destination location doesnot exist in openerp \n' \
                                            'Please check in csv line no "%s" ') % (destination_location, col+1))
                        else:                    
                            if row_count==1 and value != True and col >= 1:
                                raise osv.except_osv(_('Warning!'), _('Please Enter a Destination Location in csv \n' \
                                            'Please check in csv line no "%s" ') % (col+1))                    
                        
                            
                        if row_count==2 and value and col >= 1:
                            qty = value
                        if row_count==3 and value and col >= 1:
                            product_name = value
                            product_ids = product_obj.search(cr,uid,['|',('default_code', '=', product_name),('name', '=', product_name)])
                            product_id = product_obj.browse(cr, uid, product_ids)
                            if not product_id:
                                raise osv.except_osv(_('Warning!'), _(' "%s" Product doesnot exist in openerp \n' \
                                            'Please check in csv line no "%s" ') % (product_name, col+1))
                        else:
                            if row_count==3 and value != True and col >= 1:
                                raise osv.except_osv(_('Warning!'), _('Please Enter a internal refrence in csv \n' \
                                            'Please check in csv line no "%s" ') % (col+1))
                                    
                    if col >= 1:
                        exist_intl_pick =  picking_obj.search(cr, uid, [('name', 'ilike', 'INT'), ('type', '=', 'internal'),('location_id', '=', src_location_id and src_location_id[0]), ('state', '=', 'draft') ])
                        if exist_intl_pick:
                            exist_mv_line = stock_move_obj.search(cr, uid,[('product_id','=', product_id[0].id), ('location_dest_id','=',dest_location_id[0]), ('picking_id', '=', exist_intl_pick[0])])
                            if exist_mv_line:
                                for each_line in exist_mv_line:
                                    move_ids = stock_move_obj.browse(cr, uid, each_line)
                                    move_ids.write({'product_qty':float(qty) + move_ids.product_qty})
                            else:
                                stock_move_obj.create(cr, uid, {'product_id':product_id[0].id, 'product_qty':qty or 0.0,
                                                                'location_id':src_location_id[0],
                                                                'name': product_id[0].name,
                                                                'location_dest_id':dest_location_id[0],
                                                                'product_uom':product_id[0].uom_id.id,
                                                                'date':date, 
                                                                'date_expected':date_expected,
                                                                'picking_id':exist_intl_pick[0],
                                                                'company_id':product_id[0].company_id.id})
                                
                        if not exist_intl_pick:
                            int_picking_id = picking_obj.create(cr,uid,{
                                           'location_id':src_location_id[0],
                                           'type':'internal',
                                        })
                            if int_picking_id:
                                stock_move_lines.update({'product_id':product_id[0].id,
                                                         'product_uom':product_id[0].uom_id.id,
                                                         'name':'ABC',
                                                         'product_qty':qty or 0.0, 
                                                         'location_id':src_location_id[0], 
                                                         'location_dest_id':dest_location_id[0],
                                                         'date':date, 
                                                         'date_expected':date_expected,
                                                         'picking_id':int_picking_id,
                                                         'company_id':product_id[0].company_id.id
                                })
                                stock_move_obj.create(cr, uid, stock_move_lines)
                    row_count=0
                    col+=1
        else:
            raise osv.except_osv(_('Warning!'), _('Please select csv file!!'))