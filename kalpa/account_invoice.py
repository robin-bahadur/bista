
from osv import osv, fields

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type=type, partner_id=partner_id, \
                                                                  date_invoice=date_invoice,payment_term=payment_term, \
                                                                      partner_bank_id=partner_bank_id,company_id=company_id)

        if res:
            vals = res['value']
            if vals.has_key('account_id'):
                acc_id = vals['account_id']
                print "aaa=",acc_id
                res['account_id'] = int(acc_id)

        partner_obj = self.pool.get('res.partner')

        if partner_id:
            partner_brows_obj=partner_obj.browse(cr, uid, partner_id)
            user_id = partner_brows_obj.user_id
            res['user_id']= user_id.id
            if partner_brows_obj.property_payment_term.id:
                res['payment_term']=partner_brows_obj.property_payment_term.id   #####new_new_new_server_update
            
        return {'value':res}



    def onchange_discount_all(self, cr, uid, ids, percent,invoice_line, context=None):
        result = {}
        invocie_line = invoice_line[0][2]
        
        new_invoice_line = []
        
        if invoice_line:
            if invoice_line[0][2]== False:
                for line in range(len(invoice_line)):
                    self.pool.get('account.invoice.line').write(cr, uid, [invoice_line[line][1]], {'discount':percent})
                return {'value':{'invoice_line':invoice_line}}
            else:
                for line in invoice_line:
                    print "line>>!!",line[2]['product_id']
                    line = line[2]
                    line.update({'discount':percent})
                    new_invoice_line.append([0, False,line])
                    print"new_invoice_line",new_invoice_line
                return {'value':{'invoice_line':new_invoice_line}}
        
        #if discount_on_total:
#
#
#
#            raise osv.except_osv(('Warnning !'), ('Entered amount is greater than Unit Price'))
#        else:
#            desc_per = (discount_amt * 100)/price_unit
#            result['discount'] = desc_per
        return {'value': result}

    
    _columns = {
		'user_id': fields.many2one('res.users', 'Salesperson',track_visibility='onchange', states={'paid':[('readonly',True)]}),
                'discount_on_total':fields.float('Discount on Total (%)',readonly=True, states ={'draft': [('readonly', False)]}),
                'discount_policy': fields.selection([
                       ('line', 'On Line Basis'),
                       ('total', 'On Total'),
                    ], 'Discount Type',readonly=True, states ={'draft': [('readonly', False)]}),
		}
    _defaults = {
                'discount_policy':'line',
    }

    def create(self, cr, uid, vals, context=None):
        res = super(account_invoice, self).create(cr, uid, vals, context=context)
        account_line_obj = self.pool.get('account.invoice.line')
        if res:
            discount_policy = self.browse(cr, uid, res).discount_policy
            if discount_policy == 'total':
                discount_on_total = self.browse(cr, uid, res).discount_on_total
                line_ids = account_line_obj.search(cr, uid, [('invoice_id', '=', res)])
                for line in account_line_obj.browse(cr, uid,line_ids):
                    account_line_obj.write(cr, uid, [line.id], {'discount':discount_on_total})
        return res

#    def _sale_person_record_rule(self,cr,uid,ids,vals,context=None):
#        group_obj = self.pool.get('res.groups')
#        if not vals.has_key('message_follower_ids'):
#            for id in ids:
#                cr.execute('select user_id,create_uid from account_invoice where id=%s', (tuple(map(int, [id])),))
#                rec = cr.fetchall()
#                print "create_uid>>>>>>>>>",res
#                user_id = res[0][0]
#                create_uid = res[0][1]
#                fdgfd
#                cr.execute('select gid from res_groups_users_rel where uid in %s', (tuple(map(int, [uid])),))
#                assigned_gid = cr.fetchall()
#                if assigned_gid:
#                    for gid in assigned_gid:
#                        group_name = group_obj.browse(cr,uid,gid[0],context).name
#                        if group_name == 'Sale Person Record Rule' and user_id or create_uid != uid:
#                            print "user_id[0][0]****",user_id[0][0]
#                            print "uid****",uid
#                            raise osv.except_osv(('Error !'), ('You are not authorized Person to Update the Record'))
#
#
#
#    def write(self,cr,uid,ids,vals,context=None):
#        print "vals>>>",vals
#        self._sale_person_record_rule(cr,uid,ids,vals,context=None)
#        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

account_invoice()

