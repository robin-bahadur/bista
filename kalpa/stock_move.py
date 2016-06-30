from osv import fields
from osv import osv
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule

from service import web_services
from tools.translate import _
import pytz
import re
import time
import tools
import base64
import StringIO
import binascii
from base64 import b64decode
import cStringIO
import csv
import netsvc

class stock_move(osv.osv):

    _inherit = 'stock.move'

    def onchange_quantity_price(self, cr, uid, ids, current_id, consignment_price, quantity, flag=False):
        '''
        this function is used to compute the product_total based on the consignment price
        and the quantity
        '''

        if flag:
            return consignment_price * quantity
        else:
            if current_id:
                obj_current_stock_move = self.browse(cr, uid, current_id)
                parent_move_id = obj_current_stock_move.stock_move_id

                if parent_move_id:
                    parent_rem_product_qty = self.pool.get('stock.move').browse(cr, uid, parent_move_id).rem_product_qty

                    if quantity > parent_rem_product_qty:
                        raise osv.except_osv(_('Product Quantity Error !'), _('Your Product qty exceeeds your Consignment quantity(%f)') %(parent_rem_product_qty))
            vals = {
                'product_total' : consignment_price * quantity,
                'rem_product_qty' : quantity,
            }

            return {'value': vals}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_id: Destination location id
        @param address_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        lang = False
        if partner_id:
            addr_rec = self.pool.get('res.partner.address').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec.partner_id and addr_rec.partner_id.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]

        obj_product = self.browse(cr, uid, ids)

#        product_quantity = obj_product.product_qty

        uos_id  = product.uos_id and product.uos_id.id or False



        product_consignment_price = product.kalpa_consignment_price
        current_id = False


        product_total = self.onchange_quantity_price(cr, uid, ids, current_id,product_consignment_price, 1.00, flag=True)
        result = {
            'consignment_price' : product.kalpa_consignment_price,
            'product_reference' : product.default_code,
            'product_category1' : product.categ_id.id,
            'product_public_price' : product.kalpa_public_price,
            'product_total' : product_total,
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'rem_product_qty' : 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty']
        }
        if not ids:
            result['name'] = product.partner_ref
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}


    def change_state(self, cr, uid, ids, context=None):
        '''
        to change the state of the stock move in the consignment locations
        '''

        self.write(cr, uid, ids, {'state_add':'yes'})
        return True


    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                          product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_qty': 0.00
          }

        if (not product_id) or (product_uos_qty <=0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_qty'] = product_uos_qty / uos_coeff['uos_coeff']
        else:
            result['product_qty'] = product_uos_qty


        if ids:
            obj_stock_move = self.browse(cr, uid, ids[0])

            if obj_stock_move.product_qty >1.00:
                result.update({ 'product_qty': obj_stock_move.product_qty })
        return {'value': result}

#    def get_product_qty(cr, uid, context=None):
#        print"Context",context
#        return 50


    _columns = {
        'consignment_price' : fields.float('Consignment Price'),
        'sold_quantity' : fields.integer('Quantity Sold',readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman3',select=True),
        'product_reference' : fields.char('Reference', size=32),
        'product_category' : fields.many2one('product.product', 'Category'),
        'product_category1' : fields.many2one('product.category', 'Category'),
        'product_public_price' : fields.float('Public price'),
        'product_total' : fields.float('Total'),
        'state_add' : fields.selection([('yes','Yes'),('no','No')]),
        'rem_product_qty' : fields.integer('Remaining Quantity'),
        'stock_move_id' : fields.integer('Stock move ID'),
        'create_date1' : fields.date('Consignment Date'),
        'picking_date' : fields.related('picking_id','date',type='date',relation='stock.picking',string='Date'),
        'user_id' : fields.many2one('res.users','Salesman'),
        'date_products_return' : fields.datetime('Return Date'),
    }

    _defaults = {
        'state_add' : 'no',
        'user_id': lambda obj, cr, uid, context:uid,
    }





stock_move()

class stock_picking(osv.osv):

    _inherit = 'stock.picking'

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):

        """ Builds the dict containing the values for the invoice

            @param picking: picking object

            @param partner: object of the partner to invoice

            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)

            @param journal_id: ID of the accounting journal

            @return: dict that will be used to create the invoice object

        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            payemntterm = False
            sale_id = picking.sale_id
            if sale_id:
                payemntterm = sale_id.payment_term

            account_id = partner.property_account_receivable.id

            payment_term = payemntterm and payemntterm.id or partner.property_payment_term.id or False

        else:

            account_id = partner.property_account_payable.id

            payment_term = partner.property_supplier_payment_term.id or False

        comment = self._get_comment_invoice(cr, uid, picking)

        discount_policy = discount_on_total = ''
        user_id = ''
        if picking.sale_id:

            sale_obj = self.pool.get('sale.order').browse(cr,uid,picking.sale_id.id)

            discount_policy = sale_obj.discount_policy or False

            discount_on_total = sale_obj.discount_on_total or False

            user_id = sale_obj.user_id.id

        invoice_vals = {

            'name': picking.name,

            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),

            'type': inv_type,

            'account_id': account_id,

            'partner_id': partner.id,

            'comment': comment,

            'payment_term': payment_term,

            'fiscal_position': partner.property_account_position.id,

            'date_invoice': context.get('date_inv', False),

            'company_id': picking.company_id.id,

            'user_id': user_id or uid,

            'discount_policy':discount_policy or False,

            'discount_on_total':discount_on_total or False,

        }

        cur_id = self.get_currency_id(cr, uid, picking)

        if cur_id:

            invoice_vals['currency_id'] = cur_id

        if journal_id:

            invoice_vals['journal_id'] = journal_id

        return invoice_vals #####new_new_new_new_server_update




    def location_change(self, cr, uid, ids, loc_id):
        '''
        this function is used so that in the moves of this stock picking
        the location_dest_id will be set to this location
        '''


        partner_id = self.pool.get('stock.location').browse(cr ,uid, loc_id).partner_id.id


        vals = {
            'partner_id' : partner_id,

        }
        return {'value': {'partner_id': partner_id}}



    def action_done(self, cr, uid, ids, context=None):

        '''
        this function is overriden so that the remaining quantity of the stock moves
        can be deducted if moves are present in the consignment locations see from line
        220 to line 242

        '''
        
        self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
        stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',ids[0])])

        for move_id in stock_move_ids:
            x = self.pool.get('stock.move').write(cr, uid, [move_id], {'state': 'done'})


        sale_order_origin = self.browse(cr, uid, ids[0]).sale_id.origin
        if sale_order_origin:

            objs_order_line = self.browse(cr, uid, ids[0]).sale_id.order_line


            stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',ids[0])])

            for move_id in stock_move_ids:

                obj_each_stock_move = self.pool.get('stock.move').browse(cr, uid, move_id)
                parent_move_id = obj_each_stock_move.stock_move_id

                if not parent_move_id:
                    continue
                obj_parent_move = self.pool.get('stock.move').browse(cr, uid, parent_move_id)
                parent_rem_qty = obj_parent_move.rem_product_qty

                parent_rem_qty = parent_rem_qty - obj_each_stock_move.product_qty

                product_total = obj_parent_move.consignment_price * parent_rem_qty
                ret_val = obj_parent_move.write({'rem_product_qty': parent_rem_qty , 'product_total': product_total })
#                return_value = obj_parent_move.write({'rem_product_qty' : parent_rem_qty })



        return True

#    def action_move(self, cr, uid, ids, context=None):
#        """ Changes move state to assigned.
#        @return: True
#        """
#        print "Times"
#        for pick in self.browse(cr, uid, ids, context=context):
#            todo = []
#            for move in pick.move_lines:
#                if move.state == 'assigned':
#                    todo.append(move.id)
#            if len(todo):
#                self.pool.get('stock.move').action_done(cr, uid, todo,
#                        context=context)
#
#
#
#        print "Action picking ID",ids[0]
#
#
#        sale_order_origin = self.browse(cr, uid, ids[0]).sale_id.origin
#        if sale_order_origin:import netsvc
#
#            objs_order_line = self.browse(cr, uid, ids[0]).sale_id.order_line
#
#
#            stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',ids[0])])
#
#            for move_id in stock_move_ids:
#                print "IDGH",move_id
#                obj_each_stock_move = self.pool.get('stock.move').browse(cr, uid, move_id)
#                parent_move_id = obj_each_stock_move.stock_move_id
#                print "Parent",parent_move_id
#                obj_parent_move = self.pool.get('stock.move').browse(cr, uid, parent_move_id)
#                parent_rem_qty = obj_parent_move.rem_product_qty
#                print "Parent1",parent_rem_qty
#                parent_rem_qty = parent_rem_qty - obj_each_stock_move.product_qty
#                print "Parent2",parent_rem_qty
#                ret_val = self.pool.get('stock.move').write(cr, uid, obj_parent_move.id, {'rem_product_qty': parent_rem_qty })
##                return_value = obj_parent_move.write({'rem_product_qty' : parent_rem_qty })
#                print "Return value",ret_val
#
#                print "Return nvalue1",obj_parent_move.rem_product_qty
#
#        return True




    _columns = {
        'user_id': fields.many2one('res.users', 'Salesman', select=True),
        'location_id': fields.many2one('stock.location','Stock Location'),
        'total_products' : fields.integer('Total products'),
        'sales_tax' : fields.float('Sales Tax'),
        'total_value' : fields.float('Total'),


    }

    _defaults = {
        'invoice_state' : '2binvoiced',

    }

stock_picking()



class stock_location(osv.osv):

    _inherit = 'stock.location'
    def copy(self, cr, uid, id, default=None, context=None):

        if True:
            raise osv.except_osv(_('Warning!'), _('You can not duplicate a consignment,Instead create new one through create button'))  ###server_update
        return super(res_partner, self).copy(cr, uid, id, default, context)

#    def _compute_lines(self, cr, uid, ids, name, args, context=None):
#        result = {}
#        for invoice in self.browse(cr, uid, ids, context=context):
#            src = []
#            lines = []
#            if invoice.move_id:
#                for m in invoice.move_id.line_id:
#                    temp_lines = []
#                    if m.reconcile_id:
#                        temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
#                    elif m.reconcile_partial_id:
#                        temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
#                    lines += [x for x in temp_lines if x not in lines]
#                    src.append(m.id)
#
#            lines = filter(lambda x: x not in src, lines)
#            result[invoice.id] = lines
#        return result

    def _compute_moves(self, cr, uid, ids, name, args, context=None):
        '''
        Function for showing up all the consignments with the destination location
        set to current location
        '''
        
        result = {}

        picking_ids = self.pool.get('stock.picking').search(cr, uid ,[('type','=','internal')])
#        picking_ids = self.pool.get('stock.picking').search(cr, uid ,[])
        move_ids = []
        for pid in picking_ids:

            object_move = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',pid),('location_dest_id','in',ids),('state','=','done'),('rem_product_qty','>',0)])
#            object_move = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',pid),('location_dest_id','in',ids)])
            if len(object_move):
                for ob in object_move:
                    data=self.pool.get('stock.move').browse(cr,uid,ob)
                   
                    move_ids.append(ob)

        if len(ids):
            rid = ids[0]
            result[rid] = move_ids
           
            return result
        else:
            return False


    def consignment_gross_total(self, cr, uid, ids, context=None):
        '''
        this function is used to compute the gross total of the moves in the consignment
        adding the taxes too
        '''
      
        obj_stock_move_lines = self.browse(cr, uid, ids[0]).move_id

        consignment_total = 0
        for move_line in obj_stock_move_lines:
            consignment_total += move_line.product_total
        tax_percentage = self.browse(cr, uid, ids[0]).tax_id.amount
        if tax_percentage:
            consignment_total += tax_percentage * consignment_total
        
        return_value = self.write(cr, uid, ids[0],{'gross_total':consignment_total})
        return True

    def reset_state(self, cr, uid, ids, context=None):
        '''
        this function is used to reset the states of all the moves in the consignment
        '''
        obj_stock_move_lines = self.browse(cr, uid, ids[0]).move_id
        for move_line in obj_stock_move_lines:
            move_line.write({'state_add':'no'})
        return True



    def create_sale_order(self, cr, uid, ids, context=None):
        '''
        Writing function for generating sales order and populating the
        order lines from the internal moves according to the location
        '''
       
        obj_stock_location = self.browse(cr, uid, ids[0])
        if not obj_stock_location.partner_id.id:
            raise osv.except_osv(_('Partner info Missing !'), _('Please select a Proper Partner for the Location'))
        #pid = obj_stock_location.address_id.id
        #partner_id = obj_stock_location.address_id.partner_id.id
	pid = obj_stock_location.partner_id.id
        partner_id = obj_stock_location.partner_id.id
        obj_sale_order = self.pool.get('sale.order')

        supplier_data = self.pool.get('res.partner').browse(cr, uid, partner_id , context=context)
        pricelist_id = supplier_data.property_product_pricelist and supplier_data.property_product_pricelist.id or False
        user_id = supplier_data.user_id.id or False
       
        if obj_stock_location.partner_id.property_payment_term.id:
            payment_term = obj_stock_location.partner_id.property_payment_term.id
        else:
            #raise osv.except_osv(_('Payment Term Missing !'), _('Please select a Payment Term for the customer'))
	   
	    search_payment_term = self.pool.get('account.payment.term').search(cr,uid,[('name','=','60 Dagen')])
	    for m in self.pool.get('account.payment.term').browse(cr,uid,search_payment_term):
			payment_term=m.id
			
        gen_sale_id = obj_sale_order.create(cr, uid, {
            #'partner_id' : partner_id,
	    'partner_id' : pid,
            #'partner_order_id' : pid,
            'partner_invoice_id' : pid,
            'order_policy': 'picking',
            'partner_shipping_id' : pid,
            'pricelist_id' : 3,
            'origin' : obj_stock_location.name,
            'note' : obj_stock_location.name,
	    'date_order': time.strftime('%Y-%m-%d'),
            'payment_term' : payment_term,
	    'user_id':user_id or uid,
        })
        obj_internal_ids = self.pool.get('stock.move').search(cr, uid, [('location_dest_id','=',ids[0]),('state_add','=','yes')])
        for eachid in obj_internal_ids:
            obj_each_internal_move = self.pool.get('stock.move').browse(cr, uid, eachid)
            ret = obj_each_internal_move.write({'state_add':'no'})
            
            obj_saleorder_line = self.pool.get('sale.order.line')
            sale_order_id = obj_saleorder_line.create(cr ,uid, {
                'product_id' : obj_each_internal_move.product_id.id,
                'product_uom' : obj_each_internal_move.product_uom.id,
                'name' : obj_each_internal_move.product_id.name,
                'line_consignment_price' : obj_each_internal_move.consignment_price,
                'price_unit' : obj_each_internal_move.consignment_price,
                'order_id' : gen_sale_id,
                'product_uom_qty' : obj_each_internal_move.rem_product_qty,
                'stock_move_id' : eachid,
                'salesman_id':user_id or uid,

            })
            '''if obj_each_internal_move.product_id.id:
                product_id = obj_each_internal_move.product_id.id
                obj_product = self.pool.get('product.product').browse(cr, uid, product_id)
                tax_id = obj_product.taxes_id[0].id
                cr.execute('insert into sale_order_tax(order_line_id,tax_id) values(%s,%s)',(sale_order_id,tax_id))'''


        return {
            'domain': "[('id','=',"+str(gen_sale_id)+")]",
            'name': 'Sales Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'auto_refresh':0,
#            'context': "{'type': 'out_refund'}",
            'type': 'ir.actions.act_window',
#            'search_view_id': res and res[1] or False
        }




    def onchange_partner_consignment(self, cr, uid, ids, partner_id):
     
        res_partner_ids = self.pool.get('res.partner').search(cr, uid, [('id','=',partner_id)])
        

        vals = {
            'address_id' : res_partner_ids,
        }

        return {'value' : vals }

    #def export_data(self, cr, uid, ids, context=None):
        
     #   datas = []
     #   datas.append("Database_ID")
     #   datas.append("Reference")
     #   datas.append("Date")
     #   datas.append("Product")
     #   datas.append('Product_Reference_Code')
     #   datas.append("Category")
     #   datas.append("Quantity")
     #   datas.append("Consignment_Price")
     #   datas.append("Public_Price")
     #   datas.append("Total")
     #   buf=cStringIO.StringIO()
     #   writer=csv.writer(buf, 'UNIX', delimiter=' ')
     
     #   print "List",csv.list_dialects()
     #   pls_write = writer.writerow(datas)
     #   datas = []
        
     #   for location_data in self.pool.get('stock.location').browse(cr,uid,ids):
            
     #       move_objs = location_data.move_id
           
     #       for move_obj in move_objs:
     #           datas.append(move_obj.id)
     #           datas.append(move_obj.picking_id.name)
     #           date_picking = move_obj.picking_date
     #           date_parts = date_picking.split(' ')
                
     #           delimeter = ''
     #           picking_date_new= delimeter.join(date_parts)
     #           datas.append(move_obj.picking_date)
              
     #           datas.append(move_obj.product_id.name)
     #           datas.append(move_obj.product_id.default_code)
     #           datas.append(move_obj.product_category1.name)
     #           datas.append(move_obj.product_qty)
     #           datas.append(move_obj.consignment_price)
     #           datas.append(move_obj.product_public_price)
     #           datas.append(move_obj.product_total)
     #           pls_write = writer.writerow(datas)
     #           datas = []
     #   out=base64.encodestring(buf.getvalue())
     #   print "out",base64.decodestring(out)
     #   buf.close()
     #   return self.write(cr, uid, ids, {'state':'get', 'exportfile_csv':out})


#        return self.write(cr, uid, ids, {'state':'get', 'exportfile_csv':out , 'csv_name':})
    def _default_tax(self, cr, uid, context):

        tax_ids_sale = self.pool.get('account.tax').search(cr, uid, [('type_tax_use', 'in', ('sale','all')),('is_default', '=', True)])
        return tax_ids_sale[0]

    _columns = {
        'is_consignment' : fields.boolean('Consignment Location'),
        'user_id' : fields.many2one('res.users','Salesman'),
        'partner_id' : fields.many2one('res.partner','Partner'),
        'tax_id' : fields.many2one('account.tax','Tax(%)'),
        'gross_total' : fields.float('Gross Total',digits=(12,2)),
        'move_id' : fields.function(_compute_moves, method=True, relation='stock.move', type="one2many", string='Internal Moves'),
        'exportfile_csv': fields.binary('Export Template', readonly=True),
        'csv_name' : fields.char('name_csv',size=32),
        'state': fields.selection( ( ('choose','choose'),   # choose language
                                        ('get','get'),         # get the file
                                      ) ),
    }

    _defaults = {
#        'tax_id' : _default_tax,
        'user_id': lambda obj, cr, uid, context:uid,

    }

stock_location()

class res_company(osv.osv):

    _inherit = "res.company"

    _columns = {
        'consignment_date' : fields.char('Consignment Date',size=64),
        'invoice_logo' : fields.binary('Invoice Logo'),
        'quotation_logo' : fields.binary('Orderbevestiging Logo'),
        'consignment1_logo' : fields.binary('Consignment Order + Logo'),
        'consignment_logo' : fields.binary('Consignment Order Logo'),
        'return_consignment_logo' : fields.binary('Returned Products Logo'),
        'refund_invoice_logo' : fields.binary('Refund Invoice Logo'),
    }

    _defaults = {
        'consignment_date' : lambda *a: time.strftime('%d %b %Y'),

    }

res_company()

