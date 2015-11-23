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
from openerp import netsvc


class account_tax(osv.osv):

    _inherit = "account.tax"


    def onchange_bool(self, cr, uid,ids, boolean):
        '''
        this function is used to assign tax  to each and every product by
        manually pushing the product_id and tax_id in the many2many table
        product_taxes_rel
        '''

        print"ids",ids
        if ids:
            if boolean == True :
                product_search = self.pool.get('product.product').search(cr,uid,[])
                print"product_search",product_search
#                print"ere"+1
                tax_type = self.browse(cr,uid,ids[0]).type_tax_use
                print "tax type" , tax_type
                for each_prod in product_search:
    #                cr.execute ('insert into product_taxes_rel (where prod_id = %s, tax_id = %s; each_prod,ids[0])
                        template_id = self.pool.get('product.product').browse(cr, uid, each_prod).product_tmpl_id.id
                        if tax_type == 'sale' :
                            cr.execute('INSERT INTO product_taxes_rel \
                            (prod_id,tax_id) values (%s,%s)', (template_id,ids[0]))
                            print "sale"

                        elif tax_type == 'purchase' :
                            cr.execute('INSERT INTO product_supplier_taxes_rel \
                            (prod_id,tax_id) values (%s,%s)', (template_id,ids[0]))
                            print "purchase"


            else :

                product_search = self.pool.get('product.product').search(cr,uid,[])
#                print"product_search",product_search
#                print"ere"+1
                for each_prod in product_search:
    #                cr.execute ('insert into product_taxes_rel (where prod_id = %s, tax_id = %s; each_prod,ids[0])
                    cr.execute('delete from product_taxes_rel where \
                            tax_id=%s', (ids[0],))
                    cr.execute('delete from product_supplier_taxes_rel where \
                            tax_id=%s', (ids[0],))

        return True


    _columns = {
        'is_default': fields.boolean('Default'),
    }

account_tax()

class account_payment_term(osv.osv):

    _inherit = "account.payment.term"

    _columns = {
        'direct_debit': fields.boolean('Direct Debit'),
        'refund' : fields.boolean('Refund'),

    }

account_payment_term()

class account_invoice(osv.osv):

    _inherit = 'account.invoice'
#    _defaults = {
#        'payment_term' : 1,             #### server_update
#
#    }

account_invoice()


class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):

        if context is None:

            context = {}

        company_id = company_id if company_id != None else context.get('company_id',False)

        context = dict(context)

        context.update({'company_id': company_id, 'force_company': company_id})

        if not partner_id:

            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )

        if not product:

            if type in ('in_invoice', 'in_refund'):

                return {'value': {}, 'domain':{'product_uom':[]}}

            else:

                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}

        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)

        fpos_obj = self.pool.get('account.fiscal.position')

        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False



        if part.lang:

            context.update({'lang': part.lang})

        result = {}

        res = self.pool.get('product.product').browse(cr, uid, product, context=context)



        if type in ('out_invoice','out_refund'):

            a = res.property_account_income.id

            if not a:

                a = res.categ_id.property_account_income_categ.id

        else:

            a = res.property_account_expense.id

            if not a:

                a = res.categ_id.property_account_expense_categ.id

        a = fpos_obj.map_account(cr, uid, fpos, a)

        if a:

            result['account_id'] = a



        if type in ('out_invoice', 'out_refund'):

            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)

        else:

            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)

        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)



        if type in ('in_invoice', 'in_refund'):

            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )

        else:

            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})

        result['name'] = res.partner_ref



        if type in ('out_invoice','out_refund'):

            cr.execute('select id from account_tax where is_default is True')

            search_tax=cr.fetchall()[0]

            if search_tax:

                result['invoice_line_tax_id'] = search_tax





        result['uos_id'] = uom_id or res.uom_id.id

        if res.description:

            result['name'] += '\n'+res.description



        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}



        res_final = {'value':result, 'domain':domain}



        if not company_id or not currency_id:

            return res_final



        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)

        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)



        if company.currency_id.id != currency.id:

            if type in ('in_invoice', 'in_refund'):

                res_final['value']['price_unit'] = res.standard_price

            new_price = res_final['value']['price_unit'] * currency.rate

            res_final['value']['price_unit'] = new_price



        if result['uos_id'] and result['uos_id'] != res.uom_id.id:

            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)

            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])

            res_final['value']['price_unit'] = new_price

        return res_final

    _columns = {
        'ref_product': fields.related('product_id','default_code',type='char' ,string='P reference', store=True, size=64),

    }

account_invoice_line()

class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'



#Overwrite create_move_from_st_line method



    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, next_number, context=None):

        account_move_obj = self.pool.get('account.move')

        voucher_obj = self.pool.get('account.voucher')

        wf_service = netsvc.LocalService("workflow")

        move_line_obj = self.pool.get('account.move.line')

        bank_st_line_obj = self.pool.get('account.bank.statement.line')

        st_line = bank_st_line_obj.browse(cr, uid, st_line_id, context=context)

        if st_line.voucher_id:

            voucher_obj.write(cr, uid, [st_line.voucher_id.id], {'number': next_number}, context=context)

            if st_line.voucher_id.state == 'cancel':

                voucher_obj.action_cancel_draft(cr, uid, [st_line.voucher_id.id], context=context)

            wf_service.trg_validate(uid, 'account.voucher', st_line.voucher_id.id, 'proforma_voucher', cr)



            v = voucher_obj.browse(cr, uid, st_line.voucher_id.id, context=context)

            bank_st_line_obj.write(cr, uid, [st_line_id], {

                'move_ids': [(4, v.move_id.id, False)]

            })

            move_id = v.move_ids[0].move_id.id

            move_line_obj.write(cr, uid, [x.id for x in v.move_ids], {'statement_id': st_line.statement_id.id}, context=context)

            account_move_obj.post(cr, uid, [move_id], context=context)

            return move_id

        return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line.id, company_currency_id, next_number, context=context)

account_bank_statement()
