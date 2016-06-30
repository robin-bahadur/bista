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

from dateutil import parser
import time
from report import report_sxw

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_comment' : self._get_comment,
            'split_qty' : self._split_qty,
            'get_invoice_number' : self._get_invoice_number,
            'get_all_consignment_quantity' : self._get_qty,
            'get_invoice_lines' : self._get_invoice_lines,
            'payterm_check' : self._payterm_check,
            'get_invoice_logo' : self._get_invoice_logo,
            'direct_debit' : self._direct_debit,
        })

    def _direct_debit(self, o):

        if o.partner_id.per_kalpa:
            return "ja"
        else:
            return "nee"

    def _get_invoice_logo(self, o):

        if o.type == 'out_refund':
            return o.company_id.refund_invoice_logo
        else:
            return o.company_id.invoice_logo

    def _payterm_check(self, o):

        obj_payment_term = self.pool.get('account.payment.term')
        if o.type == 'out_refund':
            note = ""
            print "refund"
            payterm_ids = obj_payment_term.search(self.cr, self.uid, [('refund','=',True)])
            print "payterm_ids",payterm_ids
            if payterm_ids:
                note = obj_payment_term.browse(self.cr, self.uid, payterm_ids[0]).note
            print "refund note",note
            return note
        elif o.payment_term:
            if o.payment_term.direct_debit:
                ac_ids = o.partner_id.bank_ids
                print "ac_no",ac_ids
                note = o.payment_term.note
                if ac_ids:
                    ac_no = o.partner_id.bank_ids[0].acc_number
                    ac_note = note + ": " +str(ac_no)
                    print "ac_note",ac_note
                    return ac_note
                else:
                    return note
            else:
                return o.payment_term.note

    def _get_invoice_lines(self, o):

        line_ids = []
        for x in o.invoice_line:
            line_ids.append(x.id)
    
        line_ids = self.pool.get('account.invoice.line').search(self.cr, self.uid, [('id','in',line_ids)], order="ref_product")
        invoice_line_objects = self.pool.get('account.invoice.line').browse(self.cr, self.uid, line_ids)
        return invoice_line_objects

    def _get_qty(self,o):

        obj_invoice_lines = o.invoice_line
        total_qty = 0
        for each_line in obj_invoice_lines:
            total_qty+= each_line.quantity

        total_qty = int(total_qty)
        return total_qty

    def _get_invoice_number(self, ob):

        print "invoice number in get invoice----",ob
        inv_number = ob.number
        print"inv_number",inv_number
        return inv_number


    def _split_qty(self,quantity):

        strQty = str(quantity)
        qty_array = strQty.split('.')
        return qty_array[0]

    def _get_comment(self,o):

        if o.comment:
            x = ''
            location_id = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=',o.comment)])
            if location_id:
                x = 'Verkoop uit consignatie'
                return x
            else:
                return x
        else:
            return ''



        
report_sxw.report_sxw(
    'report.account.invoice2',
    'account.invoice',
    'addons/kalpa/report/account_print_invoice.rml',
    parser=account_invoice
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
