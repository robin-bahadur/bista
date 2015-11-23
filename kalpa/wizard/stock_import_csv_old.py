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


class stock_export_csv(osv.osv_memory):
    """ Export Module """

    _name = "stock.export.csv"

    _description = "Export CSV"


    def export_csv(self, cr, uid, ids, context=None):
        '''
        to export all the move lines to the csv

        '''

        location_id = context.get('active_id')
        location_obj = self.pool.get('stock.location').browse(cr, uid, location_id)
        if not location_obj.partner_id.id:
            raise osv.except_osv(_('Partner info Missing !'), _('Please select a Proper Partner for the Location'))

        datas = []
        datas.append("Quantity")
        datas.append("Product_Reference_Code")
        datas.append("Category")
        datas.append("Product")
        datas.append("Consignment_Price")
        datas.append("Total")
        datas.append("Public_Price")
        datas.append("Database_ID")
        datas.append("Reference")
        datas.append("Date")

        
        #buf=cStringIO.StringIO()
#        writer = csv.writer(f, delimiter=',', dialect='excel')
        buf=cStringIO.StringIO()
        writer=csv.writer(buf, 'UNIX')
        
        pls_write = writer.writerow(datas)
        datas = []

        pls_write = writer.writerow(datas)


        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append("Concept Consignatielijst")
        pls_write = writer.writerow(datas)
        datas = []
        pls_write = writer.writerow(datas)
        pls_write = writer.writerow(datas)
        pls_write = writer.writerow(datas)

        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)

        pls_write = writer.writerow(datas)
        datas = []

        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(location_obj.partner_id.name)
        pls_write = writer.writerow(datas)
        datas = []

        
        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(location_obj.partner_id.name)
        pls_write = writer.writerow(datas)
        datas = []

        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)
        x = location_obj.partner_id.street2
        street2 = str(x)
        street = location_obj.partner_id.street
        datas.append(str(street) + " " +  str(street2))
        pls_write = writer.writerow(datas)
        datas = []

        datas.append(None)
        datas.append(None)
        datas.append(None)
        datas.append(None)
        str_data = str(location_obj.partner_id.zip) + " " + str(location_obj.partner_id.city)
        datas.append(str_data)
        pls_write = writer.writerow(datas)
        datas = []

        pls_write = writer.writerow(datas)
        pls_write = writer.writerow(datas)
        pls_write = writer.writerow(datas)


        for location_data in self.pool.get('stock.location').browse(cr,uid,[location_id]):

            move_objs = location_data.move_id

        all_move_ids = []

        picking_ids = self.pool.get('stock.picking').search(cr, uid ,[('type','=','internal')])
        for pid in picking_ids:
            object_move_id = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',pid),('location_dest_id','=',location_id),('state','=','done'),('rem_product_qty','>',0)], order="product_reference")
            if len(object_move_id):
                for i in object_move_id:
                    all_move_ids.append(i)

        all_move_ids = self.pool.get('stock.move').search(cr, uid, [('id','in',all_move_ids)], order="product_reference")

        objects_stock_move = self.pool.get('stock.move').browse(cr, uid, all_move_ids)
        for move_obj in objects_stock_move:

            datas.append(move_obj.rem_product_qty)
            datas.append(move_obj.product_id.default_code)
            datas.append(move_obj.product_category1.name)
            datas.append(move_obj.product_id.name)
            datas.append(move_obj.consignment_price)
            datas.append(move_obj.product_total)
            datas.append(move_obj.product_public_price)
            datas.append(move_obj.id)
            datas.append(move_obj.picking_id.name)
            date_picking = move_obj.picking_date
            datas.append(move_obj.picking_date)


            pls_write = writer.writerow(datas)
            datas = []



        out=base64.encodestring(buf.getvalue())
        
        buf.close()
        string = "con"
        location_name = self.pool.get('stock.location').browse(cr, uid, location_id).name
        date = time.strftime('%Y%m%d')
        string += location_name + date +".csv"
        self.write(cr, uid, ids[0], {'state':'get', 'csv_file':out,'name': string},context=None)

        res1 = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'kalpa', 'view_stock_export_csv_wizard_new')
        res_id = res1 and res1[1] or False,
        return {
          'name':_("Save CSV"),
          'view_mode': 'form',
          'view_id': res_id,
          'view_type': 'form',
          'res_model': self._name,
          'res_id':ids[0],
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
          'no_destroy':True,
          }

    

    _columns = {
        'name' : fields.char('Name',size=32),
        'csv_file' : fields.binary('CSV file'),
        'state': fields.selection( [ ('choose','choose'),('get','get')],'state')

    }


stock_export_csv()


class stock_import_csv(osv.osv_memory):
    """ Import Module """

    _name = "stock.import.csv"

    _description = "Import Order"

    _columns = {
          'csv_file': fields.binary('CSV file', required=True),
          'state': fields.selection([('init','init'),('done','done')], 'state', readonly=True),
          
    }

    _defaults = {
        'state': 'init',
    }

    def import_csv(self, cr, uid, ids, context):

        '''
        Code to import csv and generate a sale order,confirm the order,prepare a delivery order
        and also a draft invoice
        '''

        data = self.pool.get('stock.import.csv').browse(cr, uid, ids[0])
        if not data.csv_file:
            raise osv.except_osv(_('CSV Error !'), _('Please select a .csv file'))
        module_data = data.csv_file
        val = base64.decodestring(module_data)

        product_inv_data = val.split("\r")
        
        if len(product_inv_data)==1 and product_inv_data[0].find('\n')!=-1:
            product_inv_data = product_inv_data[0].split('\n')
        
        for i in range(0,len(product_inv_data)):
            product_inv_data_lines = product_inv_data[i]

            if i==0:
                active_id = context.get('active_id')
                obj_stock_location = self.pool.get('stock.location').browse(cr, uid, active_id)

                #pid = obj_stock_location.address_id.id
		pid = obj_stock_location.partner_id.id

                if not pid:
                    raise osv.except_osv(_('Partner info Missing !'), _('Please select a Proper Partner for the Location'))

                #partner_id = obj_stock_location.address_id.partner_id.id
		partner_id = obj_stock_location.partner_id.id
                obj_sale_order = self.pool.get('sale.order')

                supplier_data = self.pool.get('res.partner').browse(cr, uid, partner_id , context=context)
                pricelist_id = supplier_data.property_product_pricelist and supplier_data.property_product_pricelist.id or False


                if obj_stock_location.partner_id.property_payment_term.id:
                    payment_term = obj_stock_location.partner_id.property_payment_term.id

                else:
                    raise osv.except_osv(_('Payment Term Missing !'), _('Please select a Payment Term for the customer'))


                gen_sale_id = obj_sale_order.create(cr, uid, {
                    'partner_id' : partner_id,
                    'partner_order_id' : pid,
                    'partner_invoice_id' : pid,
                    'order_policy': 'picking',
                    'partner_shipping_id' : pid,
                    'pricelist_id' : pricelist_id,
                    'origin' : obj_stock_location.name,
                    'note' : obj_stock_location.name,
                    'payment_term' : payment_term,
                })


            else:
                product_single_line = product_inv_data_lines.split(',')

                if product_single_line[0] == '\n':

                    continue

                obj_saleorder_line = self.pool.get('sale.order.line')
                if product_single_line[0] and product_single_line[0]!='':

                    move_id = int(product_single_line[7])
                    obj_each_internal_move = self.pool.get('stock.move').browse(cr, uid, move_id)

                    if int(product_single_line[0]) > obj_each_internal_move.rem_product_qty:
                        raise osv.except_osv(_('Exceeding Quantity !'), _('Meer verkocht dan de voorraad'))

                    obj_saleorder_line = self.pool.get('sale.order.line')
                    #tax_id = obj_each_internal_move.product_id.taxes_id[0].id
                   
                    
                    sale_order_id = obj_saleorder_line.create(cr ,uid, {
                        'product_id' : obj_each_internal_move.product_id.id,
                        'product_uom' : obj_each_internal_move.product_uom.id,
                        'name' : obj_each_internal_move.product_id.name,
                        'line_consignment_price' : obj_each_internal_move.consignment_price,
                        'price_unit' : obj_each_internal_move.product_id.list_price,
                        'order_id' : gen_sale_id,
                        'product_uom_qty' : product_single_line[0],
                        'stock_move_id' : move_id,
                        

                    })
                    
                    #cr.execute('insert into sale_order_tax(order_line_id,tax_id) values(%s,%s)',(sale_order_id,tax_id))


        obj_confirm_sale =  self.pool.get('sale.order').browse(cr, uid, gen_sale_id)
        wf_service = netsvc.LocalService("workflow") #to generate a workflow object
        status = wf_service.trg_validate(uid, 'sale.order', gen_sale_id, 'order_confirm', cr) # to invoke a workflow to confirm the sale order
#        status_confirm_order = wf_service.trg_validate(uid, 'sale.order', gen_sale_id, 'order_confirm', cr)
        picking_id = self.pool.get('stock.picking').search(cr, uid, [('sale_id','=',gen_sale_id)])
        status_delivery = self.pool.get('stock.picking').action_done(cr, uid, picking_id)

        if status_delivery:
            obj_confirm_sale.write({'shipped':True})
        status_invoice = wf_service.trg_validate(uid, 'sale.order', gen_sale_id, 'manual_invoice', cr)# to invoke a workflow to generate a draft invoice

        return True


stock_import_csv()


class stock_import_consignment(osv.osv_memory):

    _name = 'stock.import.consignment'


    _description = "Import Consignment"

    _columns = {
          'csv_file_consignment': fields.binary('CSV file', required=True),
          'state': fields.selection([('init','init'),('done','done')], 'state', readonly=True),
          'source_location_id' : fields.many2one('stock.location','Source Location'),
          'destination_location' : fields.char('Destination Location', size=64, readonly=True),

    }

    def _get_dest_location(self, cr, uid, context=None):

        location_id = context.get('active_id')
        obj_location = self.pool.get('stock.location').browse(cr, uid, location_id)
        return obj_location.name

    
    _defaults = {
        'state': 'init',
        'destination_location' : _get_dest_location,
    }



    def import_consignment(self, cr, uid, ids, context):

        '''
         Code to import csv and generate a consignment list (stock picking---> stock move)
         csv will be the one exported from the products 
        '''


        data = self.pool.get('stock.import.consignment').browse(cr, uid, ids[0])
        if not data.source_location_id:
            raise osv.except_osv(_('Source Location Error !'), _('Please select a proper Source Location'))
        

        if not data.csv_file_consignment:
            raise osv.except_osv(_('CSV Error !'), _('Please select a .csv file'))
        module_data = data.csv_file_consignment
        val = base64.decodestring(module_data)


        product_inv_data = val.split("\r")

        if len(product_inv_data)==1 and product_inv_data[0].find('\n')!=-1:
            product_inv_data = product_inv_data[0].split('\n')

        picking_process_id = 0
        for i in range(0,len(product_inv_data)):
            product_inv_data_lines = product_inv_data[i]

            if i==0:
                active_id = context.get('active_id')
 
                obj_stock_location = self.pool.get('stock.location').browse(cr, uid, active_id)

                picking_id = self.pool.get('stock.picking').create(cr, uid, {
                    'location_id' : obj_stock_location.id,
                    'type' : 'internal',
                })
                picking_process_id = picking_id

            else:

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

                obj_stock_move = self.pool.get('stock.move')
                obj_product = self.pool.get('product.product').browse(cr, uid, product_id[0])

                stock_id = obj_stock_move.create(cr, uid, {
                    'product_id' : product_id[0],
                    'name' : obj_product.name,
                    'location_id' : data.source_location_id.id,
                    'picking_id' : picking_id,
                    'product_uom' : obj_product.uom_id.id,
                    'product_reference' : reference,
                    'product_category1' : obj_product.categ_id.id,
                    'product_public_price' : obj_product.kalpa_public_price,
                    'product_total' : obj_product.kalpa_consignment_price * int(product_single_line[0]),
                    'consignment_price' : obj_product.kalpa_consignment_price,
                    'product_qty' : int(product_single_line[0]),
                    'location_dest_id' : obj_stock_location.id,
                    'rem_product_qty' : int(product_single_line[0]),
                })
           


        obj_picking = self.pool.get('stock.picking').browse(cr, uid, picking_process_id)
        picking_id = int(obj_picking.id)
        picking_name = str(obj_picking.name)

        message = _("The CSV has been converted to Stock Picking %s") % (picking_name,)
        obj_picking = self.pool.get('stock.picking')
        obj_picking.log(cr, uid, picking_id, message)
        status_delivery = self.pool.get('stock.picking').action_done(cr, uid, [picking_process_id])
        return True


    


stock_import_consignment()

class product_list_export(osv.osv_memory):

    _name = 'product.list.export'


    def export_product_csv(self, cr, uid, ids, context=None):

        '''
        function to export only those products whose qty available >0 and
        this csv can only be used in either importing consignment or importing sale lines
        '''
        obj_product = self.pool.get('product.product')

        datas = []
  
        datas.append("Quantity")
        datas.append("default_code")
        datas.append('Discount')
        datas.append("categ_id")
        datas.append("name")
        datas.append("list_price")
        datas.append("kalpa_public_price")
        datas.append("kalpa_consignment_price")
        
        
        
        buf=cStringIO.StringIO()
        writer = csv.writer(buf, 'UNIX')
#        writer=csv.writer(buf, 'UNIX', delimiter=' ')

        pls_write = writer.writerow(datas)
        datas = []

        product_ids = obj_product.search(cr, uid, [])
        
        obj_products =  obj_product.browse(cr, uid, product_ids)

        for x in obj_products:
            
            if x.qty_available<=0:
                continue

            datas.append(x.qty_available)
            datas.append(x.default_code)
            datas.append(None)
            datas.append(x.categ_id.name)
            datas.append(x.name)
            datas.append(x.list_price)
            datas.append(x.kalpa_public_price)
            datas.append(x.kalpa_consignment_price)

            pls_write = writer.writerow(datas)
            datas = []

        
        out=base64.encodestring(buf.getvalue())

        buf.close()
        date = time.strftime('%Y%m%d')
        string = ''
        string += 'Products_List_' + date +".csv"
        
        return self.write(cr, uid, ids, {'state':'get', 'product_csv_file':out,'name': string})


    _columns = {
        'name' : fields.char('Name',size=32),
        'product_csv_file' : fields.binary('CSV file',required=True),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),

    }

product_list_export()





class product_list_export_all(osv.osv_memory):

    _name = 'product.list.export.all'


    def export_product_csv_all(self, cr, uid, ids, context=None):

        '''
        function to export all products irrespective of their stock availibility
        this csv can only be used in either importing consignment or importing sale lines
        '''
        obj_product = self.pool.get('product.product')

        datas = []

        datas.append("Quantity")
        datas.append("default_code")
        datas.append('Discount')
        datas.append("categ_id")
        datas.append("name")
        datas.append("list_price")
        datas.append("kalpa_public_price")
        datas.append("kalpa_consignment_price")



        buf=cStringIO.StringIO()
        writer = csv.writer(buf, 'UNIX')
#        writer=csv.writer(buf, 'UNIX', delimiter=' ')

        pls_write = writer.writerow(datas)
        datas = []

        product_ids = obj_product.search(cr, uid, [])

        obj_products =  obj_product.browse(cr, uid, product_ids)

        for x in obj_products:

            datas.append(x.qty_available)
            datas.append(x.default_code)
            datas.append(None)
            datas.append(x.categ_id.name)
            datas.append(x.name)
            datas.append(x.list_price)
            datas.append(x.kalpa_public_price)
            datas.append(x.kalpa_consignment_price)

            pls_write = writer.writerow(datas)
            datas = []


        out=base64.encodestring(buf.getvalue())

        buf.close()
        date = time.strftime('%Y%m%d')
        string = ''
        string += 'Products_List_all_' + date +".csv"

        return self.write(cr, uid, ids, {'state':'get', 'product_csv_file_all':out,'name': string})


    _columns = {
        'name' : fields.char('Name',size=32),
        'product_csv_file_all' : fields.binary('CSV file',required=True),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),

    }

product_list_export_all()




class consignment_quantity(osv.osv_memory):

    _name = 'consignment.quantity'


    def export_consignment_quantity(self, cr, uid, ids, context=None):

        '''
        function to export the total quantity of the products which are present in the consignment
        '''
        
        obj_product = self.pool.get('product.product')
        obj_stock_move = self.pool.get('stock.move')
        obj_picking = self.pool.get('stock.picking')
        obj_location = self.pool.get('stock.location')

        datas = []

        datas.append("Total_Quantity")
        datas.append("Name")
        datas.append("default_code")
        datas.append("Cost_Price")


        buf=cStringIO.StringIO()
        writer = csv.writer(buf, 'UNIX')

        pls_write = writer.writerow(datas)
        datas = []


        product_ids = context.get('active_ids')
        location_id = obj_location.search(cr, uid, [('is_consignment','=',True)])
        
        if not location_id or len(location_id)>1:
            raise osv.except_osv(_('Location Error !'), _('Either you have not set a Parent consignment location or there are 2 locations set as Parent'))
        location_child_ids = obj_location.search(cr, uid, [('location_id','=',location_id[0])])
        if not location_child_ids:
            raise osv.except_osv(_('Location Error !'), _('There are no child locations pertaining to the parent location you have set in the Locations'))
        picking_ids = obj_picking.search(cr, uid ,[('type','=','internal')])

        cr.execute('select sum(rem_product_qty),product_id from stock_move where picking_id in(select id from stock_picking where type=%s) and state=%s and product_id in %s and location_dest_id in(select id from stock_location where location_id in(select id from stock_location where is_consignment=True)) group by product_id',('internal','done',tuple(product_ids)))
        res = cr.dictfetchall() #to fetch all the records from the recordset and store it in the dictionary
        for x in res:
            obj_present_product = obj_product.browse(cr, uid, x['product_id'])
            datas.append(x['sum'])
            datas.append(obj_present_product.name)
            datas.append(obj_present_product.default_code)
            if uid==1:
                datas.append(obj_present_product.standard_price)
            else:
                datas.append(None)
            pls_write = writer.writerow(datas)
            datas = []




        out=base64.encodestring(buf.getvalue())

        buf.close()
        date = time.strftime('%Y%m%d')
        string = ''
        string += 'Consignment_Quantity_' + date +".csv"

        return self.write(cr, uid, ids, {'state':'get', 'consignment_quantity_csv':out,'name': string})


    _columns = {
        'name' : fields.char('Name',size=32),
        'consignment_quantity_csv' : fields.binary('CSV file',required=True),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),

    }

consignment_quantity()


class consignment_quantity_sold(osv.osv_memory):

    _name = 'consignment.quantity.sold'

    def export_consignment_quantity_sold(self, cr, uid, ids, context=None):

        '''
        function to export the total products sold in the consignment between a specific interval
        '''

        obj_consignment_object = self.browse(cr, uid, ids[0])
        obj_sale = self.pool.get('sale.order')
        obj_product = self.pool.get('product.product')
        obj_sale_order_line = self.pool.get('sale.order.line')
        start_date = obj_consignment_object.start_date
        end_date = obj_consignment_object.end_date

        datas = []

        datas.append("Quantity_Sold")
        datas.append("Reference")

        buf=cStringIO.StringIO()
        writer = csv.writer(buf, 'UNIX')
        pls_write = writer.writerow(datas)
        datas = []

        if not start_date or not end_date:
            raise osv.except_osv(_('Date Error !'), _('Please select both the Start Date and End Date for proper calculation'))

        product_ids_all = obj_product.search(cr, uid, [])

        for each_product_id in product_ids_all:
            product_qty = 0
            reference = obj_product.browse(cr, uid, each_product_id).default_code
#            sale_line_ids = obj_sale_order_line.search(cr, uid, [('create_date','>=',start_date),('create_date','<=',end_date),('stock_move_id','>',0),('product_id','=',each_product_id)])
            cr.execute("select id from sale_order_line where create_date BETWEEN %s and %s and stock_move_id>0 and product_id=%s",(start_date,end_date,each_product_id))
            sale_line_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            for line_id in sale_line_ids:
                obj_sale_line = obj_sale_order_line.browse(cr, uid, line_id)
                if not obj_sale_line.order_id.shipped:
                    continue
                product_qty += obj_sale_line.product_uom_qty
            datas.append(product_qty)
            datas.append(reference)
            pls_write = writer.writerow(datas)
            datas = []

        
        out=base64.encodestring(buf.getvalue())
        buf.close()
        date = time.strftime('%Y%m%d')
        string = ''
        string += 'Consignment_Quantity_Sold_' + date +".csv"

        return self.write(cr, uid, ids, {'state':'get', 'consignment_quantity_csv_sold':out,'name': string})

    _columns = {
        'name' : fields.char('Name',size=32),
        'start_date' : fields.date('Start date'),
        'end_date' : fields.date('End Date'),
        'consignment_quantity_csv_sold' : fields.binary('CSV file',required=True),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),

    }



consignment_quantity_sold()
