import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class stock_partial_picking(osv.osv_memory):
    _inherit='stock.partial.picking'

    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'stock.picking.' + picking_type
                move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)
        stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)

        obj_stock_location=self.pool.get('stock.location')
        active_id=context.get('active_id','')
        print"active_id==============",active_id
        stock_picking_out_obj=self.pool.get('stock.picking.out')
        stock_brows_obj=stock_picking_out_obj.browse(cr,uid,active_id)
	
	if stock_brows_obj.sale_id:

        	location_id = stock_brows_obj.sale_id.shop_id.warehouse_id.lot_stock_id.id
        	if location_id:
                	location_id = [location_id]
        	name=stock_brows_obj.note
        	if name:
            		search_location_id = obj_stock_location.search(cr,uid,[('name','ilike',name)])
            		if search_location_id:
                		location_id = search_location_id
        	obj_stock_location.consignment_gross_total(cr,uid,location_id)###server_update
        	return {'type': 'ir.actions.act_window_close'}
	else:
         	return {'type': 'ir.actions.act_window_close'}

stock_partial_picking()

#### new_server_update
