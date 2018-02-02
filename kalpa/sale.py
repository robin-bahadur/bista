from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order(osv.osv):
    _inherit = "sale.order"
    _order = "create_date desc"    

    _columns = {
	  'date_order': fields.date('Ordered Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)],
					'sent':[('readonly', False)]}), 
	  'creation_date': fields.date('Creation Date',required=True),
	  'discount_on_total':fields.float('Discount on Total (%)',readonly=True, states ={'draft': [('readonly', False)]}),
          #'chk_discount':fields.boolean('Apply Discount'),
          'discount_policy': fields.selection([
                       ('line', 'On Line Basis'),
                       ('total', 'On Total'),
                    ], 'Discount Type'),
	  'zip': fields.related('partner_id','zip',type='char',string="Zip",store=False),
	  'contact_name': fields.char('Contact Person',size=128),
	#'partner_invoice_id': fields.char('Invoice Address',size=124),
	#'partner_shipping_id': fields.char('Delivery Address',size=124),
 	}
    _defaults = {
	'creation_date': fields.date.context_today,
	'discount_policy':'line',
	'date_order': fields.date.context_today,
	}


   
    def onchange_discount_all(self, cr, uid, ids, percent,order_line):

        new_order_line = []

        sale_line_obj = self.pool.get('sale.order.line')

        prod_obj = self.pool.get('product.product')

        res = {}

        if order_line:

            if order_line[0][2]== False:

              

                for line in range(len(order_line)):

                    sale_line_obj.write(cr, uid, [order_line[line][1]], {'discount':percent})

                self.button_dummy(cr, uid, ids,context={})

                return {'value':{'order_line':order_line}}

            else:

                for line in order_line:

                    new_line = line[2]

                    new_line.update({'discount':percent})

                    new_order_line.append([0, False,new_line])

                    

                    self.button_dummy(cr, uid, ids,context={})

                return {'value':{'order_line':new_order_line}}

        return {'value':res}

    def create(self, cr, uid, vals, context=None):
        res = super(sale_order, self).create(cr, uid, vals, context=context)
        sale_line_obj = self.pool.get('sale.order.line')
        if res:
            discount_policy = self.browse(cr, uid, res).discount_policy
            if discount_policy == 'total':
                discount_on_total = self.browse(cr, uid, res).discount_on_total
                line_ids = sale_line_obj.search(cr, uid, [('order_id', '=', res)])
                for line in sale_line_obj.browse(cr, uid,line_ids):
                    sale_line_obj.write(cr, uid, [line.id], {'discount':discount_on_total})
        return res

    def write(self,cr,uid,ids,vals,context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        sale_line_obj = self.pool.get('sale.order.line')
        if ids[0]:
            discount_policy = self.browse(cr, uid, ids[0]).discount_policy
            if discount_policy == 'total':
                discount_on_total = self.browse(cr, uid, ids[0]).discount_on_total
                line_ids = sale_line_obj.search(cr, uid, [('order_id', '=', ids[0])])
                for line in sale_line_obj.browse(cr, uid,line_ids):
                    sale_line_obj.write(cr, uid, [line.id], {'discount':discount_on_total})
            else:
#                discount_on_total = self.browse(cr, uid, ids[0]).discount_on_total
                line_ids = sale_line_obj.search(cr, uid, [('order_id', '=', ids[0])])
                for line in sale_line_obj.browse(cr, uid,line_ids):
                    
                    discount = sale_line_obj.browse(cr, uid, line.id).discount
                    sale_line_obj.write(cr, uid, [line.id], {'discount':discount})
        return res	

    def onchange_shop_id(self, cr, uid, ids, shop_id):
        v = {}
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
            v['project_id'] = shop.project_id.id
            v['order_policy'] = 'picking'
            # Que faire si le client a une pricelist a lui ?
            if shop.pricelist_id.id:
                v['pricelist_id'] = shop.pricelist_id.id
        return {'value': v} 

    def onchange_partner_id(self, cr, uid, ids, part,context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'partner_order_id': False, 'payment_term': False, 'fiscal_position': False}}
	res_partner_browse = self.pool.get('res.partner').browse(cr,uid,part)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        client_ref = part.ref
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
	contact_name = part.contact_name
        val = {
            'partner_invoice_id': addr['invoice'],
	    #'partner_invoice_id': str(res_partner_browse.street)+','+str(res_partner_browse.zip)+','+str(res_partner_browse.city),
            'partner_order_id': addr['contact'],
            'partner_shipping_id': addr['delivery'],
	    #'partner_shipping_id': str(res_partner_browse.street)+','+str(res_partner_browse.zip)+','+str(res_partner_browse.city),
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'client_order_ref' : client_ref,
 	    'contact_name': contact_name,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}




#    def action_ship_create(self, cr, uid, ids, *args):
#        '''
#        this function is overriden because we need to check whether the shipping is
#        created i.e delivery order from the stock locations i.e customized link in consignment locations
#        or by the default erp process see line no.42 order.origin
#        '''
#
#        print "Shipping is Executed in kalpa"
#        wf_service = netsvc.LocalService("workflow")
#        picking_id = False
#        move_obj = self.pool.get('stock.move')
#        proc_obj = self.pool.get('procurement.order')
#        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
#        for order in self.browse(cr, uid, ids, context={}):
#            print "INORDER"
#            proc_ids = []
#            output_id = order.shop_id.warehouse_id.lot_output_id.id
#            picking_id = False
#            for line in order.order_line:
#                print"LINESALE",line.stock_move_id
#                proc_id = False
#                date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
#                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')
#
#                if line.state == 'done':
#                    continue
#                move_id = False
#                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
#                    if order.origin:
#                        location_ids = self.pool.get('stock.location').search(cr ,uid, [('name','=',order.origin)])
#                        location_id = location_ids[0]
#                    else:
#                        location_id = order.shop_id.warehouse_id.lot_stock_id.id
#                    if not picking_id:
#                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
#                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
#                            'name': pick_name,
#                            'origin': order.name,
#                            'type': 'out',
#                            'state': 'auto',
#                            'move_type': order.picking_policy,
#                            'sale_id': order.id,
#                            'address_id': order.partner_shipping_id.id,
#                            'note': order.note,
#                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
#                            'company_id': order.company_id.id,
#                        })
#                    move_id = self.pool.get('stock.move').create(cr, uid, {
#                        'name': line.name[:64],
#                        'picking_id': picking_id,
#                        'product_id': line.product_id.id,
#                        'date': date_planned,
#                        'date_expected': date_planned,
#                        'product_qty': line.product_uom_qty,
#                        'consignment_price' : line.product_id.kalpa_consignment_price,
#                        'product_public_price' : line.product_id.kalpa_public_price,
#                        'product_total' : line.product_uom_qty * line.product_id.kalpa_consignment_price,
#                        'product_uom': line.product_uom.id,
#                        'product_uos_qty': line.product_uos_qty,
#                        'product_uos': (line.product_uos and line.product_uos.id)\
#                                or line.product_uom.id,
#                        'product_packaging': line.product_packaging.id,
#                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
#                        'location_id': location_id,
#                        'location_dest_id': output_id,
#                        'sale_line_id': line.id,
#                        'tracking_id': False,
#                        'state': 'draft',
#                        #'state': 'waiting',
#                        'note': line.notes,
#                        'company_id': order.company_id.id,
#                        'stock_move_id' : line.stock_move_id,
#                    })
#
#                if line.product_id:
#                    proc_id = self.pool.get('procurement.order').create(cr, uid, {
#                        'name': line.name,
#                        'origin': order.name,
#                        'date_planned': date_planned,
#                        'product_id': line.product_id.id,
#                        'product_qty': line.product_uom_qty,
#                        'product_uom': line.product_uom.id,
#                        'product_uos_qty': (line.product_uos and line.product_uos_qty)\
#                                or line.product_uom_qty,
#                        'product_uos': (line.product_uos and line.product_uos.id)\
#                                or line.product_uom.id,
#                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
#                        'procure_method': line.type,
#                        'move_id': move_id,
#                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],
#                        'company_id': order.company_id.id,
#                    })
#                    proc_ids.append(proc_id)
#                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
#                    if order.state == 'shipping_except':
#                        for pick in order.picking_ids:
#                            for move in pick.move_lines:
#                                if move.state == 'cancel':
#                                    mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'),('sale_line_id', '=', line.id),('picking_id', '=', pick.id)])
#                                    if mov_ids:
#                                        for mov in move_obj.browse(cr, uid, mov_ids):
#                                            move_obj.write(cr, uid, [move_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
#                                            proc_obj.write(cr, uid, [proc_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
#
#            val = {}
#
#            if picking_id:
#                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
#
#            for proc_id in proc_ids:
#                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
#
#            if order.state == 'shipping_except':
#                val['state'] = 'progress'
#                val['shipped'] = False
#
#                if (order.order_policy == 'manual'):
#                    for line in order.order_line:
#                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
#                            val['state'] = 'manual'
#                            break
#            self.write(cr, uid, [order.id], val)
#        return True
#
#
#
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        stock_location_obj=self.pool.get('stock.location')
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        if (order.note):                                  ##### new_server_update
                search_id = stock_location_obj.search(cr,uid,[('name','ilike',order.note)])
                if search_id:
                    location_id=search_id[0]
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
	    'stock_move_id': line.stock_move_id,
        }
        
    def process_order(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        obj_picking=self.pool.get('stock.picking')
        obj_stock_move=self.pool.get('stock.move')
        search_id=obj_picking.search(cr, uid, [('sale_id','=',ids[0])])
#         journal_id=self.pool.get('stock.invoice.onshipping')._get_journal(cr,uid,context)
        stock_partial_pick_obj=self.pool.get('stock.partial.picking')
        for pick in obj_picking.browse(cr, uid, search_id):
            if not pick.move_lines:
                raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
            todo_moves = [x.id for x in pick.move_lines if x.state in ['confirmed','waiting']]
            obj_stock_move.action_confirm(cr, uid, todo_moves)
            wf_service.trg_validate(uid, 'stock.picking', pick.id,'button_confirm', cr)
#             for picking in self.browse(cr, uid, ids):
#             obj_picking.draft_force_assign(cr,uid,[pick.id],context)
            obj_picking.force_assign(cr,uid,[pick.id],context)
            obj_picking.test_assigned(cr,uid,[pick.id])
            pick.action_assign_wkf()
            context = obj_picking.action_process(cr, uid, [pick.id], context=context).get('context')
#             context = process.
            context['active_id'],context['active_ids'] = pick.id,search_id 
            res_id=stock_partial_pick_obj.create(cr,uid,{'date':time.strftime('%Y-%m-%d %H:%M:%S')},context)
            if res_id:
                stock_partial_pick_obj.do_partial(cr, uid, [int(res_id)], context)
            pick.action_done()
            inv_id=obj_picking.action_invoice_create(cr, uid, [pick.id], False, False, 'out_invoice', context)
        if inv_id:
            inv_id=inv_id.values()
            inv_id=int(inv_id[0])
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_id':inv_id,
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                }
sale_order()


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'
	
    _columns = {
	'name': fields.text('Description', required=False, select=True, readonly=True, states={'draft': [('readonly', False)]}),
}
    def invoice_line_create(self, cr, uid, ids, context=None):
        '''
        this function is overriden to create invoice lines based
        on the consignment price and not the sale price
        see line no 198 , line.line_consignment_price
        '''

   
        if context is None:
            context = {}

        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(cr, uid,
                        line.procurement_id.id, context=context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(cr, uid,
                        line.procurement_id.id, context=context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    a = prop and prop.id or False
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    if line.line_consignment_price:
                       
                        pu = round(line.line_consignment_price * line.product_uom_qty / uosqty,
                                self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                       
                    else:
                        
                        pu = round(line.price_unit * line.product_uom_qty / uosqty,
                                self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                if not a:
                    raise osv.except_osv(_('Error !'),
                                _('There is no income category account defined in default Properties for Product Category or Fiscal Position is not defined !'))
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'price_unit': pu,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
#                    'note': line.notes,
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})
                sales[line.order_id.id] = True
                create_ids.append(inv_id)
        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined !'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
       
        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        #if update_tax: #The quantity only have changed
        #    result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}


    _columns = {
        'stock_move_id' : fields.integer('Stock move ID'),
        'line_consignment_price' : fields.float('Consignment Price'),
        'ref_product': fields.related('product_id','default_code',type='char',string='product reference', store=True, size=64),
    }

    def tax_default(self,cr,uid,ids,context=None):
	#search_tax=self.pool.tax('account.tax').search(cr,uid,[('id','>',0)])
	cr.execute('select id from account_tax where is_default is True')
	search_tax=cr.fetchall()[0]
	return search_tax

    _defaults = {
	'tax_id': tax_default,
	
	}
sale_order_line()



#
#class account_invoice_line(osv.osv):
#
#    _inherit = 'account.invoice.line'
#
#    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
#        '''
#        to compute the subtotal based on consignment price and not the sale price
#        see line no.256,257
#        '''
#        print "Computing Subtotal customized"
#        res = {}
#        tax_obj = self.pool.get('account.tax')
#        cur_obj = self.pool.get('res.currency')
#        for line in self.browse(cr, uid, ids):
#            price = 0
#            print "consignment price",line.line_consignment_price
#            if line.line_consignment_price:
#                price = line.line_consignment_price * (1-(line.discount or 0.0)/100.0)
#                print "price in the subtotal",price
#            else:
#                price = line.price_unit * (1-(line.discount or 0.0)/100.0)
#                print "normal price"
#
#            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
#            res[line.id] = taxes['total']
#            if line.invoice_id:
#                cur = line.invoice_id.currency_id
#                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
#        return res
#    _columns = {
#
#
#        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', type="float",
#            digits_compute= dp.get_precision('Account'), store=True),
#
#    }
#
#account_invoice_line()

