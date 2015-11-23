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

import time
from dateutil import parser
from report import report_sxw

class quotation_normal(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(quotation_normal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'split_qty' : self._split_qty,
            'get_all_consignment_quantity' : self._get_qty,
            'date_time_split' : self._date_time_split,
            'new_split' : self._new_split,
            'get_present_date' : self._get_present_date,
            'get_name' : self._get_name,
            'direct_debit' : self._direct_debit,
        })

    def _direct_debit(self, o):

        if o.partner_id.per_kalpa:
            return "ja"
        else:
            return "nee"

    def _get_name(self):

        return "xxx"

    def _get_present_date(self):

        present_date = time.strftime('%d %b %Y')
        return present_date

    def _new_split(self, o):


        obj_sale = self.pool.get('sale.order').browse(self.cr, self.uid, o.id)
        dt = obj_sale.create_date
        date_part = dt.split(' ')
        new_date = date_part[0].strip()
        parse_date = parser.parse(new_date) # to convert from string to datetime
        formatted_date = parse_date.strftime("%d-%b-%Y") # to change the format of date
        return formatted_date

    def _date_time_split(self, dt):

        parse_date = parser.parse(dt) # to convert from string to datetime
        formatted_date = parse_date.strftime("%d-%b-%Y")
        return formatted_date


    def _get_qty(self,o):

        obj_sale_lines = o.order_line
        total_qty = 0
        for each_line in obj_sale_lines:
            total_qty+= each_line.product_uom_qty

        total_qty = int(total_qty)
        return total_qty


    def _split_qty(self,quantity):

        qty = int(quantity)
        return qty





report_sxw.report_sxw(
    'report.quotation.normal',
    'sale.order',
    'addons/kalpa/report/quotation_report_normal.rml',
    parser=quotation_normal
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
