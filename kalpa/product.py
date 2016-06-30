import decimal_precision as dp
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

class product_product(osv.osv):

    _inherit = 'product.product'

    def _sale_person_record_rule(self,cr,uid,ids,vals,context=None):
        group_obj = self.pool.get('res.groups')
        if not vals.has_key('message_follower_ids'):
            for id in ids:
                cr.execute('select create_uid from product_product where id=%s', (tuple(map(int, [id])),))
                create_uid = cr.fetchall()
                cr.execute('select gid from res_groups_users_rel where uid in %s', (tuple(map(int, [uid])),))
                assigned_gid = cr.fetchall()
                if assigned_gid:
                    for gid in assigned_gid:
                        group_name = group_obj.browse(cr,uid,gid[0],context).name
                        if group_name == 'Sale Person Record Rule' and create_uid[0][0] != uid:
                            raise osv.except_osv(('Error !'), ('You are not authorized Person to Update the Record'))



    def write(self,cr,uid,ids,vals,context=None):
        self._sale_person_record_rule(cr,uid,ids,vals,context=None)
        return super(product_product, self).write(cr, uid, ids, vals, context=context)


    def tax_type_sale(self, cr, uid, context=None):
        tax_ids_sale = self.pool.get('account.tax').search(cr, uid, [('type_tax_use', 'in', ('sale','all')),('is_default', '=', True)])
        return tax_ids_sale

    def tax_type_purchase(self, cr, uid, context=None):
        tax_ids_purchase = self.pool.get('account.tax').search(cr, uid, [('type_tax_use', 'in', ('purchase','all')),('is_default', '=', True)])
        return tax_ids_purchase

    def onchange_public_price(self, cr, uid, ids, public_price,categ_id):
       
        product_categ  = self.pool.get('product.category')
        vals = {
            'kalpa_consignment_price' : 0.55 * public_price,     #####issues solved
            'kalpa_public_price_ex' : 0.826446281 * public_price,
        }
        if categ_id:
            discount_percent = product_categ.browse(cr,uid,categ_id).discount
        else:
            discount_percent = 0.0
        

        if not discount_percent:
            vals['list_price'] = public_price
        else:
            list_price = public_price - ((discount_percent/100)*public_price)
            vals['list_price'] = list_price


        return { 'value' : vals }    ##### new_new_server_update


    _columns = {
        'kalpa_consignment_price': fields.float('Consignment Price', digits_compute=dp.get_precision('Sale Price')),
        'kalpa_public_price': fields.float('Public Price Inc', digits_compute=dp.get_precision('Sale Price')),
        'kalpa_public_price_ex' : fields.float('Public Price ex', digits_compute=dp.get_precision('Sale Price')),
    }



    _defaults = {
        'taxes_id': tax_type_sale,
        'supplier_taxes_id': tax_type_purchase
    }

product_product()

class product_category(osv.osv):

    _inherit = 'product.category'

    _columns = {
        'discount' : fields.float('Discount(%)',digits=(12,2)),

    }


product_category()
