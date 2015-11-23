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



#class res_partner_address(osv.osv):
#    _inherit = 'res.partner.address'
#
#
#
#    def name_get(self, cr, user, ids, context={}):
#        if not len(ids):
#            return []
#        res = []
#        for r in self.read(cr, user, ids, ['name', 'zip', 'country_id', 'city', 'partner_id', 'street', 'phone' ,'street2']):
##            print 'r----------------',r
##            print 'context----------------',context
#            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
#                res.append((r['id'], r['partner_id'][1]))
#            else:
#                addr = r['name'] or ''
#                if r['name'] and (r['city'] or r['country_id']):
#                    addr += ', '
#
#                addr += (r['country_id'] and r['country_id'][1] or '') + ' ' + (r['city'] or '') + ' '  + (r['street'] or '')+ ' ' + (str(r['street2']) or '')+ ', ' + (str(r['phone']) or '')+ ', ' + (str(r['zip']) or '')
#                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
#                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr.strip() or '/')))
#                else:
#                    res.append((r['id'], addr.strip() or '/'))
#
#        return res
#
#
#res_partner_address()


class crm_meeting(osv.osv):
    _inherit = 'crm.meeting'
    
#    def _default_partner_address(self, cr, uid, ids, context=None):
#
##         res = self.pool.get('res.partner').address_get(cr, uid, [invoice.partner_id.id], ['default','contact', 'invoice','delivery'])
#
#        print"IdsCrm",ids
#        if ids.has_key('active_model'):
#            if ids['active_model'] == 'res.partner':
#                pid = ids['active_id']
#                print"ParentID",pid
#
#                obj_partner_address =self.pool.get('res.partner.address')
#                partner_addr_ids =  obj_partner_address.search(cr, uid, [('partner_id', '=', pid)])
#
#                obj_partner_info = obj_partner_address.browse(cr, uid, partner_addr_ids[0])
#
#
#                return partner_addr_ids[0]
#        else:
#            return False



        
    def onchange_dates(self, cr, uid, ids, start_date, duration=False, end_date=False, allday=False, context=None):


        print"ID's",ids
        print"Start Date",start_date



        if context is None:
            context = {}

        value = {}

        if start_date:
            str_app_date = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            str_app_date = time.strftime("%Y-%m-%d",str_app_date)
            value['app_date'] = str_app_date
        


        if not start_date:
            return value
        if not end_date and not duration:
            duration = 2.00
            value['duration'] = duration

        if allday: # For all day event
            value = {'duration': 24}
            duration = 24.0

        start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if end_date and not duration:
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value['duration'] = round(duration, 2)
        elif not end_date:
            end = start + timedelta(hours=duration)
            value['date_deadline'] = end.strftime("%Y-%m-%d %H:%M:%S")
        elif end_date and duration and not allday:
            # we have both, keep them synchronized:
            # set duration based on end_date (arbitrary decision: this avoid
            # getting dates like 06:31:48 instead of 06:32:00)
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value['duration'] = round(duration, 2)

        return {'value': value}


    _columns = {
        'appointment_date': fields.datetime('Create Date'),
        'app_date': fields.date('Appointment Date'),
	'partner_id': fields.many2one('res.partner','Customer',size=124),
        
    }

    

    _defaults = {
#        'partner_address_id' : _default_partner_address,
        'duration' : 2,
	

    }

    _order = "date desc"

crm_meeting()



class res_partner(osv.osv):
    _inherit = 'res.partner'

#    def open_consignment(self, cr, uid, ids, context=None):
#
#        location_id = self.pool.get('stock.location').search(cr, uid, [('partner_id','=',ids[0])])
#
#        if not location_id:
#            raise osv.except_osv(_('Partner Error !'), _(' This partner does not possess a Consignment Location'))
#
#        print "consignment locations"
#
##        str_url ="http://localhost:8080/openerp/menu?active=275#url=%2Fopenerp%2Fform%2Fedit%3Fmodel%3Dstock.location%26id%3D"
##        str_url+=str(location_id[0])+"%26ids%3D%255B16%252C%252018%252C%252017%252C%252015%252C%252011%252C%252014%252C%252012%252C%252019%252C%252020%252C%252021%252C%252022%252C%252023%252C%252024%252C%252025%252C%252026%252C%252027%252C%252028%252C%252029%252C%252030%252C%252031%255D%26view_ids%3D%255B891%252C%2520890%255D%26view_mode%3D%255Bu%2527tree%2527%252C%2520u%2527form%2527%255D%26view_type%3Dtree%26domain%3D%255B(%2527usage%2527%252C%2520%2527%253D%2527%252C%2520%2527internal%2527)%255D%26context%3D%257B%2527lang%2527%253A%2520u%2527en_US%2527%252C%2520%2527tz%2527%253A%2520False%252C%2520%2527active_model%2527%253A%2520%2527ir.ui.menu%2527%252C%2520%2527section_id%2527%253A%2520False%252C%2520%2527active_id%2527%253A%2520392%252C%2520%2527_terp_view_name%2527%253A%2520u%2527Consignment%2520Locations%2527%252C%2520%2527client%2527%253A%2520%2527web%2527%252C%2520%2527active_ids%2527%253A%2520%255B392%255D%252C%2520%2527department_id%2527%253A%2520False%257D%26offset%3D0%26limit%3D20%26count%3D145%26search_domain%3D%255B(%2527usage%2527%252C%2520%2527%253D%2527%252C%2520%2527internal%2527)%255D%26filter_domain%3D%255B%255D%26notebook_tab%3D0%26action_id%3D539"
#        mod_obj = self.pool.get('ir.model.data')
#        res = mod_obj.get_object_reference(cr, uid, 'kalpa', 'view_consignment_location')
#        res_id = res and res[1] or False,
##        print "location_id",location_id[0]
##        print "strurl",str_url
##        return {
##        'type': 'ir.actions.act_url',
##        'url': str_url,
##        'target': 'new'
##        }
#
#        return {
#            'domain': "[('id','=',"+str(location_id[0])+")]",
#            'name': 'Consignment Locations',
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'stock.location',
#            'view_id': [res_id],
#            'target': 'current',
#            'type': 'ir.actions.act_window',
#            'res_id': location_id and location_id[0] or False,
#
#        }
#
#    def open_sales_order(self, cr, uid, ids, context=None):
#
#        partner_id = ids[0]
#        obj_sale = self.pool.get('sale.order')
#        sale_ids = obj_sale.search(cr, uid, [('partner_id','=', partner_id)])
#        if not sale_ids:
#            raise osv.except_osv(_('Sales Order Error !'), _('There are no sales order for this Customer'))
#
#        return {
#            'domain': "[('partner_id','=',"+str(partner_id)+")]",
#            'name': 'Sales Orders',
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'res_model': 'sale.order',
#            'view_id': False,
#            'target': 'current',
#            'type': 'ir.actions.act_window',
##            'res_id': location_id and location_id[0] or False,
#
#        }
#
#    def open_invoices(self, cr, uid, ids, context=None):
#
#
#        partner_id = ids[0]
#        obj_invoice = self.pool.get('account.invoice')
#        invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=', partner_id)])
#        if not invoice_ids:
#            raise osv.except_osv(_('Invoice Error !'), _('There are no Invoices for this Customer'))
#
#        return {
#            'domain': "[('partner_id','=',"+str(partner_id)+")]",
#            'name': 'Account Invoices',
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'res_model': 'account.invoice',
#            'view_id': False,
#            'target': 'current',
#            'type': 'ir.actions.act_window',
##            'res_id': location_id and location_id[0] or False,
#
#        }

    def _sale_person_record_rule(self,cr,uid,ids,vals,context=None):
        group_obj = self.pool.get('res.groups')
	if not isinstance(ids,list):
           ids = [ids]                        ##server_update
        if not vals.has_key('message_follower_ids'):
            for id in ids:
                cr.execute('select user_id from res_partner where id=%s', (tuple(map(int, [id])),))
                user_id = cr.fetchall()
                cr.execute('select gid from res_groups_users_rel where uid in %s', (tuple(map(int, [uid])),))
                assigned_gid = cr.fetchall()
                if assigned_gid:
                    for gid in assigned_gid:
                        group_name = group_obj.browse(cr,uid,gid[0],context).name
                        if group_name == 'Sale Person Record Rule' and user_id[0][0] != uid:
			  if group_name == user_id[0][0] != None:
                            print "create_uid[0][0]****",user_id[0][0]
                            print "uid****",uid
                            raise osv.except_osv(('Error !'), ('You are not authorized Person to Update the Record'))


    def write(self,cr,uid,ids,vals,context=None):
        print "vals>>>",vals
        print"_____________________"
        self.pool.get('res.partner')._sale_person_record_rule(cr,uid,ids,vals,context=None)
        return super(res_partner, self).write(cr, uid, ids, vals, context=context)


    def _get_consignment_value(self, cr, uid, ids, field_name, arg, context=None):
        print"_____________________"

        location_obj = self.pool.get('stock.location')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            location_id = location_obj.search(cr, uid, [('partner_id','=',line.id)])
            if not location_id:
		gross_total = 0.0
		res[line.id] = gross_total
                continue
            gross_total = location_obj.browse(cr, uid, location_id[0]).gross_total
            res[line.id] = gross_total
        return res

    def _get_quotation_value(self, cr, uid, ids, field_name, arg, context=None):

        print"_____________________"
        no_quotation = 0
        quotation_value = 0.00
        sale_obj = self.pool.get('sale.order')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            print "line id",line.id
            sale_ids = sale_obj.search(cr, uid, [('partner_id','=',line.id),('state','=',['draft','sent'])])
            for each_id in sale_ids:
                quotation_value += sale_obj.browse(cr, uid, each_id).amount_total
                no_quotation +=1

            res[line.id] = {
                    'no_quotation' : no_quotation,
                    'quotation_value' : quotation_value
                }

        return res
            
    def _get_invoice_value_unpaid(self, cr, uid, ids, field_name, arg, context=None):

        obj_invoice = self.pool.get('account.invoice')
        invoice_value_unpaid_in = 0.00
        invoice_value_unpaid_refund = 0.00
        no_invoices_unpaid = 0
        res = {}

        for line in self.browse(cr, uid, ids, context=context):

            in_invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=',line.id),('state','<>','paid'),('state','<>','cancel'),('type','=','out_invoice')])
            refund_invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=',line.id),('state','<>','paid'),('state','<>','cancel'),('type','=','out_refund')])

            for each_invoice_id in in_invoice_ids:
                invoice_value_unpaid_in += obj_invoice.browse(cr, uid, each_invoice_id).amount_total
                no_invoices_unpaid +=1

            for each_invoice_id in refund_invoice_ids:
                invoice_value_unpaid_refund += obj_invoice.browse(cr, uid, each_invoice_id).amount_total
                no_invoices_unpaid +=1

            invoice_value_unpaid = invoice_value_unpaid_in - invoice_value_unpaid_refund

            res[line.id] = {
                    'invoice_value_unpaid' : invoice_value_unpaid,
                    'no_invoices_unpaid' : no_invoices_unpaid,
                }
        
        return res

    def _get_invoice_value(self, cr, uid, ids, field_name, arg, context=None):

        obj_invoice = self.pool.get('account.invoice')
        invoice_value_2012_in = 0.00
        invoice_value_2012_refund = 0.00
        no_invoices_2012 = 0
        res = {}

        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)

        for line in self.browse(cr, uid, ids, context=context):

            in_invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=',line.id),('date_invoice','>=',first_date),('date_invoice','<=',last_date),('type','=','out_invoice')])
            refund_invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=',line.id),('date_invoice','>=',first_date),('date_invoice','<=',last_date),('type','=','out_refund')])


            for each_invoice_id in in_invoice_ids:
                invoice_value_2012_in += obj_invoice.browse(cr, uid, each_invoice_id).amount_total
                no_invoices_2012 +=1

            for each_invoice_id in refund_invoice_ids:
                invoice_value_2012_refund += obj_invoice.browse(cr, uid, each_invoice_id).amount_total
                no_invoices_2012 +=1

            invoice_value_2012 = invoice_value_2012_in - invoice_value_2012_refund

            res[line.id] = {
                    'invoice_value_2012' : invoice_value_2012,
                    'no_invoices_2012' : no_invoices_2012,
                }
        
        return res

    def _get_invoice_value_previous(self, cr, uid, ids, field_name, arg, context=None):

        obj_invoice = self.pool.get('account.invoice')
        invoice_value_previous = 0.00
        no_invoices_previous = 0
        res = {}

        first_date = date(date.today().year-1, 1, 1)
        last_date = date(date.today().year-1, 12, 31)
        print "first_date",first_date
        print "last_date",last_date

        for line in self.browse(cr, uid, ids, context=context):

            invoice_ids = obj_invoice.search(cr, uid, [('partner_id','=',line.id),('date_invoice','>=',first_date),('date_invoice','<=',last_date)])

            for each_invoice_id in invoice_ids:
                invoice_value_previous += obj_invoice.browse(cr, uid, each_invoice_id).amount_total
                no_invoices_previous +=1

            res[line.id] = {
                    'invoice_value_previous' : invoice_value_previous,
                    'no_invoices_previous' : no_invoices_previous,
                }

        return res


    _columns = {
        'contact_date' : fields.date('Contact Date'),
        'qt_number' : fields.char('Quantore Number',size=64),
        'show_sales_order' : fields.boolean('Show Sales Orders'),
        'no_quotation' : fields.function(_get_quotation_value, method=True,multi="_get_quotation_value", string="Total Quotations",type="integer"),
        'quotation_value' : fields.function(_get_quotation_value, multi="_get_quotation_value",method=True, string="Quotation Total", type="float", digits=(12,2)),
        'show_invoices' : fields.boolean('Show Invoices'),
        'invoice_value_2012' : fields.function(_get_invoice_value, multi="_get_invoice_value",method=True, string="Invoice Value", type="float", digits=(12,2)),
        'invoice_value_unpaid' : fields.function(_get_invoice_value_unpaid,multi="_get_invoice_value_unpaid",method=True, string="Invoice Value", type="float", digits=(12,2)),
        'no_invoices_2012' : fields.function(_get_invoice_value, multi="_get_invoice_value",method=True, string="Total Invoices", type="integer"),
        'no_invoices_unpaid' : fields.function(_get_invoice_value_unpaid,multi="_get_invoice_value_unpaid",method=True, string="Total Invoices", type="integer"),
        'invoice_value_previous' : fields.function(_get_invoice_value_previous, multi="_get_invoice_value_previous",method=True, string="Invoice Value", type="float", digits=(12,2)),
        'no_invoices_previous' : fields.function(_get_invoice_value_previous, multi="_get_invoice_value_previous",method=True, string="Total Invoices", type="integer"),
        'consignment_value_function' : fields.function(_get_consignment_value, method=True, string='Consignment Value function', type="float" ,digits=(12,2)),
        'consignment_value' : fields.float('Consignment Value'),
#        'property_payment_term': fields.property(
#            'account.payment.term',
#            type='many2one',
#            relation='account.payment.term',
#            string ='Payment Term',
#            method=True,
#            store=True,
#            view_load=True,
#            help="This payment term will be used instead of the default one for the current partner"),
        'ref_companies': fields.one2many('res.company', 'partner_id',
            'Companies that refers to partner'),
        'last_reconciliation_date': fields.datetime('Latest Reconciliation Date', help='Date on which the partner accounting entries were reconciled last time')
    

    }

#    _defaults = {
#        'consignment_value' : _get_consignment_value,
#
#    }

    _order = "zip"

    _sql_constraints = [
        ('code_reference_partner', 'unique (ref)', 'The reference of the partner must be unique !')
    ]




res_partner()

#class smtpclient(osv.osv):
#
#    _inherit = 'email.smtpclient'
#
#    _columns = {
#        'alternate_email' : fields.char('Email Cc', size=64, required=True),
#        'default_server' : fields.boolean('Default server'),
#
#    }


#smtpclient()
