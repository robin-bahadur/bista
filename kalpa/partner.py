from mx import DateTime
import time
import math

from osv import fields, osv
from tools.translate import _
from osv import fields
from osv import osv
import time
import netsvc
from datetime import datetime
#from HTMLParser import HTMLParser
#import html2text

#import ir
import pooler
from tools import config

class partner(osv.osv):  
        _name="res.partner"
        _inherit="res.partner"
        _description="inherit to add date of joining field  When an candidate is selected his Employee Name is generated"
        _columns = {
                     'cust_consign' : fields.boolean("Consignment"),
                     'per_kalpa':fields.boolean("Direct Debit"),
                     'ow_dieneke' : fields.boolean('Dieneke'),
                     'ow_kalpa' : fields.boolean('Kalpa'),
                     'ow_rss' : fields.boolean('RSS'),
                     'ow_haza' : fields.boolean('Haza'),
                     'ow_michel' : fields.boolean('Michel'),
		     'meeting_id': fields.one2many('crm.meeting','partner_id','Meeting'),
		     'phonecall_id': fields.one2many('crm.phonecall','partner_id','Phonecall'),
                     #'mail_o2m': fields.one2many('mail.compose.message','partner_id','Partner Mail'),
                     'partner_o2m': fields.one2many('email.partner','partner_id','Partner Mail'),
                     
                     #'kalpa_customer' : fields.boolean('Customer',select=True),
                     'notes_o2m': fields.one2many("multi.notes", "partner_id", "Customer Notes"),
#		     'zip': fields.related('address', 'zip',string='ZIP',type='char',size=24,store=True),
#                     'contact_address': fields.related('address', 'name', type='char',size=64,store=True,string='Contact'),
#                     'city': fields.related('address', 'city', type='char', string='City',size=128,store=True),
#                     'phone': fields.related('address', 'phone', type='char', string='Phone',size=64,store=True),
               	     'partner_desc' : fields.text('General Notes'),
                     'cust_intrested' : fields.boolean('Interested'),
                     'cust_fillers' : fields.boolean('Fillers'),   
                     'cust_s1' : fields.boolean('S1'),   
                     'cust_s2' : fields.boolean('S2'),   
                     'cust_s3' : fields.boolean('S3'),   
                     'cust_s4' : fields.boolean('S4'),   
                     'cust_call' : fields.boolean('Call'),
                     'cust_cald' : fields.boolean('Calendars'),
                     'sub_number' : fields.char("Subnumber",size=10),
                     'phone_no_extra' : fields.char('Phone2',size=128),
		     'contact_name': fields.char('Contact Person',size=128),
                     }
partner()


class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def create(self, cr, uid, data, context=None):
        res = super(mail_compose_message, self).create(cr, uid, data, context=context)
        today = fields.datetime.now()
        if res:
            mail_obj = self.pool.get('email.partner')
            if data['subject']:
                partner_id = data['partner_ids'][0][2]

                for i in range(len(data['partner_ids'][0][2])):
#                    parser = HTMLParser()
                    if data['body']:
                        htmldata = html2text.html2text(data['body'])
                        htmldata = htmldata.replace("&nbsp_place_holder;", "")
                        print "data['body']>>>",data['body']
                        print "html2tezt>>>>>",htmldata
                    mail_obj.create(cr,uid,{'from':uid,'name':data['subject'],'partner_id':partner_id[i],'date':today,'body':htmldata},context=None)
        return res

mail_compose_message()



#class partner_address(osv.osv):
#    _name = "res.partner.address"
#    _inherit="res.partner.address"
#    _columns = {
#                'street2': fields.integer("Housenumber"),
#                'sub_number' : fields.char("Subnumber",size=10),
##                'email_o2m': fields.one2many("multi.email", "address_id", "Emails"),
#                'phone_no_extra' : fields.char('Phone2',size=128),
#                }
#
#    _defaults = {
#        	'country_id': 159,
#		}
#
#partner_address()

class multi_notes(osv.osv):
    _name = "multi.notes"
    _order= "date_note desc"

    _columns = {
                'partner_id' : fields.many2one('res.partner','Partner'),
                'date_note' : fields.date('Date'),
                'postal_code' : fields.char('Postal Code',size=32),
                'cust_note' : fields.text('Notes'),
		'date_in_char' : fields.char('Date Char',size=32),
                }
multi_notes()

class email_partner(osv.osv):
    _name = "email.partner"
    _order= "date desc"

    _columns = {
                'partner_id' : fields.many2one('res.partner','Partner'),
                #'mail_id' : fields.many2one('mail.compose.message','Mail'),
                'from' : fields.many2one('res.users','From'),
                'date' : fields.date('Date'),
                'name':fields.char('Subject',size=256),
                'body':fields.char('Mail',size=256),
                }
email_partner()


#class res_partner_bank_a(osv.osv):
#    _name    = "res.partner.bank"
#    _inherit = "res.partner.bank"
#    _columns = {
#                'iban_no' : fields.char("IBAN",size=8),
#                'bic_no'  : fields.char("BIC",size=18),
#                }    
#res_partner_bank_a() 
#class multi_email(osv.osv):
#    _name = "multi.email"
#    _columns = {
#                'address_id' : fields.many2one('res.partner.address','Partner Address'),
#                'email_address' : fields.char('Email Address',size=128),
#                }
#multi_email()
