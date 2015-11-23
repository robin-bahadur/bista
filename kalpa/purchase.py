from openerp.osv import fields, osv

class purchase_order_line(osv.osv):
    _inherit='purchase.order.line'
    _columns={
                'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok','=',True)], change_default=True, required=True),

    }
purchase_order_line()