# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
from tools.translate import _
import crm
import time



import decimal_precision as dp
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule

from service import web_services
import pytz
import re
import tools

class crm_phonecall(osv.osv):
    """ Phonecall Cases """

    _inherit = "crm.phonecall"

    def action_make_meeting(self, cr, uid, ids, context=None):
        """
        This opens Meeting's calendar view to schedule meeting on current Phonecall
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Phonecall to Meeting IDs
        @param context: A standard dictionary for contextual values

        @return : Dictionary value for created Meeting view
        """
        print"IDcrm",ids
        value = {}
        for phonecall in self.browse(cr, uid, ids, context=context):
            data_obj = self.pool.get('ir.model.data')

            # Get meeting views
            result = data_obj._get_id(cr, uid, 'crm', 'view_crm_case_meetings_filter')
            res = data_obj.read(cr, uid, result, ['res_id'])
            id1 = data_obj._get_id(cr, uid, 'crm', 'crm_case_calendar_view_meet')
            id2 = data_obj._get_id(cr, uid, 'crm', 'crm_case_form_view_meet')
            id3 = data_obj._get_id(cr, uid, 'crm', 'crm_case_tree_view_meet')
            if id1:
                id1 = data_obj.browse(cr, uid, id1, context=context).res_id
            if id2:
                id2 = data_obj.browse(cr, uid, id2, context=context).res_id
            if id3:
                id3 = data_obj.browse(cr, uid, id3, context=context).res_id

            context = {
                        'default_phonecall_id': phonecall.id,
                        'default_partner_id': phonecall.partner_id and phonecall.partner_id.id or False,
                        'default_email': phonecall.email_from ,
                        'default_name': phonecall.name,
                    }

            value = {
                'name': _('Meetings'),
                'domain' : "[('user_id','=',%s)]" % (uid),
                'context': context,
                'view_type': 'form',
                'view_mode': 'calendar,form,tree',
                'res_model': 'crm.meeting',
                'view_id': False,
                'views': [(id1, 'calendar'), (id2, 'form'), (id3, 'tree')],
                'type': 'ir.actions.act_window',
                'search_view_id': res['res_id'],
                'nodestroy': True
                }

        return value

    _defaults = {
                'duration': '0.01',

    }

crm_phonecall()

class customer_check(osv.osv):
    _name='customer.check'
    _columns = {
            'name':fields.char('Name',size=125, required=True),
    }
customer_check()


class res_partner(osv.osv):
	_inherit = "res.partner"

        def default_get(self, cr, uid, fields, context=None):
            data = super(res_partner, self).default_get(cr, uid, fields, context=context)
            
            for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]:
                check=self.pool.get('customer.check').search(cr,uid,[('name','ilike',i)])    
                data['m2o'+str(i)]=check[0]
                
                
                
            
            return data
        
        
        
        
        def copy(self, cr, uid, id, default=None, context=None):
            if True:
                raise osv.except_osv(_('Warning!'), _('You can not duplicate a partner,Instead create new one through create button'))  ###server_update
            return super(res_partner, self).copy(cr, uid, id, default, context)

        def _m2o1_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'call')
               
                
                return result[1]
            except Exception, ex:
                return False
        def _m2o2_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'consignatie')
                return result[1]
            except Exception, ex:
                return False
        def _m2o3_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'k_l_apart')
                return result[1]
            except Exception, ex:
                return False
        def _m2o4_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'dreamnotes')
                return result[1]
            except Exception, ex:
                return False
        def _m2o5_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'vulling_current')
                return result[1]
            except Exception, ex:
                return False
        def _m2o6_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'vulling_previous')
                return result[1]
            except Exception, ex:
                return False
        def _m2o7_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'ledi_current')
                return result[1]
            except Exception, ex:
                return False
        def _m2o8_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'ledi_previous')
                return result[1]
            except Exception, ex:
                return False
        def _m2o9_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'iny_Kalpa')
                return result[1]
            except Exception, ex:
                return False
        def _m2o10_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'iny_rss')
                return result[1]
            except Exception, ex:
                return False
        def _m2o11_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'kado_papier')
                return result[1]
            except Exception, ex:
                return False
        def _m2o12_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'helma_current')
                return result[1]
            except Exception, ex:
                return False
        def _m2o13_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'helma_previous')
                return result[1]
            except Exception, ex:
                return False
        def _m2o14_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', '14')
                return result[1]
            except Exception, ex:
                return False
        def _m2o15_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', '15')
                return result[1]
            except Exception, ex:
                return False
        def _m2o16_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', '16')
                return result[1]
            except Exception, ex:
                return False
        def _m2o17_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'no_mail')
                return result[1]
            except Exception, ex:
                return False
        def _m2o18_id(self, cr, uid, *args):
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'kalpa', 'no_call')
                return result[1]
            except Exception, ex:
                return False


	_columns = {
		#'vat_new': fields.char('VAT Number',size=124,invisible=True),
#########################################################################################
                'm2o1':fields.many2one('customer.check','m2o1'),
                'm2o2':fields.many2one('customer.check','m2o2'),
                'm2o3':fields.many2one('customer.check','m2o3'),
                'm2o4':fields.many2one('customer.check','m2o4'),
                'm2o5':fields.many2one('customer.check','m2o5'),
                'm2o6':fields.many2one('customer.check','m2o6'),
                'm2o7':fields.many2one('customer.check','m2o7'),
                'm2o8':fields.many2one('customer.check','m2o8'),
                'm2o9':fields.many2one('customer.check','m2o9'),
                'm2o10':fields.many2one('customer.check','m2o10'),
                'm2o11':fields.many2one('customer.check','m2o11'),
                'm2o12':fields.many2one('customer.check','m2o12'),
                'm2o13':fields.many2one('customer.check','m2o13'),
                'm2o14':fields.many2one('customer.check','m2o14'),
                'm2o15':fields.many2one('customer.check','m2o15'),
                'm2o16':fields.many2one('customer.check','m2o16'),
                'm2o17':fields.many2one('customer.check','m2o17'),
                'm2o18':fields.many2one('customer.check','m2o18'),

                'boolean1':fields.boolean('Boolean1'),
                'boolean2':fields.boolean('Boolean2'),
                'boolean3':fields.boolean('Boolean3'),
                'boolean4':fields.boolean('Boolean4'),
                'boolean5':fields.boolean('Boolean5'),
                'boolean6':fields.boolean('Boolean6'),
                'boolean7':fields.boolean('Boolean7'),
                'boolean8':fields.boolean('Boolean8'),
                'boolean9':fields.boolean('Boolean9'),
                'boolean10':fields.boolean('Boolean10'),
                'boolean11':fields.boolean('Boolean11'),
                'boolean12':fields.boolean('Boolean12'),
                'boolean13':fields.boolean('Boolean13'),
                'boolean14':fields.boolean('Boolean14'),
                'boolean15':fields.boolean('Boolean15'),
                'boolean16':fields.boolean('Boolean16'),
                'boolean17':fields.boolean('Boolean17'),
                'boolean18':fields.boolean('Boolean18'),


		}

        _defaults={
                'm2o1':_m2o1_id,
                'm2o2':_m2o2_id,
                'm2o3':_m2o3_id,
                'm2o4':_m2o4_id,
                'm2o5':_m2o5_id,
                'm2o6':_m2o6_id,
                'm2o7':_m2o7_id,
                'm2o8':_m2o8_id,
                'm2o9':_m2o9_id,
                'm2o10':_m2o10_id,
                'm2o11':_m2o11_id,
                'm2o12':_m2o12_id,
                'm2o13':_m2o13_id,
                'm2o14':_m2o14_id,
                'm2o15':_m2o15_id,
                'm2o16':_m2o16_id,
                'm2o17':_m2o17_id,
                'm2o18':_m2o18_id,
      }
      
      
        

res_partner()



###########################################################################################



