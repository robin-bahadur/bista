import time
import datetime
from datetime import date, timedelta
import thread
import threading
from cStringIO import StringIO
from dateutil import parser
import decimal

from report import report_sxw


class sales_annual_analysis(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sales_annual_analysis, self).__init__(cr, uid, name, context=context)
        self.total_quantity = 0.0
        self.total_all = 0.0
        self.localcontext.update({
            'time': time,
            'split_qty' : self._split_qty,
            'get_all_qty' : self._get_all_qty,
            'get_total_all' : self._get_total_all,
            'date_time_split' : self._date_time_split,
            'new_split' : self._new_split,
            'get_present_date' : self._get_present_date,
            'get_name' : self._get_name,
            'direct_debit' : self._direct_debit,
            'get_invoice_lines' : self._get_invoice_lines,
        })
        

    def _get_invoice_lines(self, dict_customer_info):
        x = 0.0
        self.cr.execute('''
                    select ai.date_invoice,ai.type,pc.name as category_name,pt.name as template_name,\
                           pp.default_code,ail.quantity,ail.price_unit,ail.price_unit * ail.quantity as price_subtotal
                    from account_invoice ai,account_invoice_line ail,res_partner rp,\
                         product_product pp,product_category pc,product_template pt
                    where ail.invoice_id = ai.id and ai.partner_id = rp.id and ail.product_id=pp.id and \
                          pp.product_tmpl_id = pt.id and pt.categ_id = pc.id and rp.id = %s and \
                          ai.period_id in (select id from account_period where fiscalyear_id=%s) order by pp.default_code
        
        '''%(dict_customer_info['customer'],dict_customer_info['fiscal_year']))
        
        sale_partner_info = self.cr.dictfetchall()

        for each_line in sale_partner_info:
            
            if each_line['type'] == 'out_invoice':
                x += each_line['price_subtotal']
                self.total_quantity += each_line['quantity']
                self.total_all += each_line['price_subtotal']
            else:
                x += each_line['price_subtotal']
                each_line.update({'quantity': -(each_line['quantity'])})
                each_line.update({'price_subtotal' : -(each_line['price_subtotal'])})  
                test = each_line['price_subtotal']
                
                self.total_quantity += each_line['quantity']
                self.total_all += each_line['price_subtotal']

       
        return sale_partner_info    

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


    def _get_all_qty(self):

        return self.total_quantity or 0
    
    def _get_total_all(self):
         
        return self.total_all or 0.0


    def _split_qty(self,quantity):

        qty = int(quantity)
        return qty





report_sxw.report_sxw(
    'report.sales.annual.analysis',
    'sale.order',
    'addons/kalpa/report/sales_annual_analysis.rml',
    parser=sales_annual_analysis,
    header=False,
)
