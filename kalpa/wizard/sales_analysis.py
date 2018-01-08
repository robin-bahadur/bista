# -*- coding: utf-8 -*-
import base64
from tools.translate import _
from osv import osv, fields
import re


class sales_analysis(osv.osv_memory):
    
    _name = "sales.analysis"
    _description = "Sales Analysis"
    
    _columns = {
        'customer' : fields.many2one('res.partner','Customer'),
        'fiscal_year' : fields.many2one('account.fiscalyear','Fiscal Year'),
    }
    
    
    def generate_report(self ,cr, uid, ids, context):
        
    
        obj_company = self.pool.get('res.company')
        obj_sales_analysis = self.browse(cr, uid, ids[0])
        obj_current_customer = obj_sales_analysis.customer
        obj_current_fiscal_year = obj_sales_analysis.fiscal_year        
#        cr.execute("""
#              select min(ail.id) as id,
#                    ai.date_invoice as date,
#                    to_char(ai.date_invoice, 'YYYY') as year,
#                    to_char(ai.date_invoice, 'MM') as month,
#                    to_char(ai.date_invoice, 'YYYY-MM-DD') as day,
#                    ail.product_id,
#                    ai.partner_id as partner_id,
#                    ai.payment_term as payment_term,
#                    ai.period_id as period_id,
#                    (case when u.uom_type not in ('reference') then
#                        (select name from product_uom where uom_type='reference' and active and category_id=u.category_id LIMIT 1)
#                    else
#                        u.name
#                    end) as uom_name,
#                    ai.currency_id as currency_id,
#                    ai.journal_id as journal_id,
#                    ai.fiscal_position as fiscal_position,
#                    ai.user_id as user_id,
#                    ai.company_id as company_id,
#                    count(ail.*) as nbr,
#                    ai.type as type,
#                    ai.state,
#                    pt.categ_id,
#                    ai.date_due as date_due,
#                    ai.address_contact_id as address_contact_id,
#                    ai.address_invoice_id as address_invoice_id,
#                    ai.account_id as account_id,
#                    ai.partner_bank_id as partner_bank_id,
#                    sum(case when ai.type in ('out_refund','in_invoice') then
#                         ail.quantity / u.factor * -1
#                        else
#                         ail.quantity / u.factor
#                        end) as product_qty,
#                    sum(case when ai.type in ('out_refund','in_invoice') then
#                         ail.quantity*ail.price_unit * -1
#                        else
#                         ail.quantity*ail.price_unit
#                        end) / cr.rate as price_total,
#                    sum(case when ai.type in ('out_refund','in_invoice') then
#                         ai.amount_total * -1
#                        else
#                         ai.amount_total
#                         end) / (CASE WHEN 
#                              (select count(l.id) from account_invoice_line as l
#                               left join account_invoice as a ON (a.id=l.invoice_id)
#                               where a.id=ai.id) <> 0 
#                            THEN 
#                              (select count(l.id) from account_invoice_line as l
#                               left join account_invoice as a ON (a.id=l.invoice_id)
#                               where a.id=ai.id) 
#                            ELSE 1 
#                            END) / cr.rate as price_total_tax,
#                    (case when ai.type in ('out_refund','in_invoice') then
#                      sum(ail.quantity*ail.price_unit*-1)
#                    else
#                      sum(ail.quantity*ail.price_unit)
#                    end) / (CASE WHEN
#                         (case when ai.type in ('out_refund','in_invoice') 
#                          then sum(ail.quantity/u.factor*-1)
#                          else sum(ail.quantity/u.factor) end) <> 0 
#                       THEN 
#                         (case when ai.type in ('out_refund','in_invoice') 
#                          then sum(ail.quantity/u.factor*-1)
#                          else sum(ail.quantity/u.factor) end) 
#                       ELSE 1 
#                       END)
#                     / cr.rate as price_average,
#
#                    cr.rate as currency_rate,
#                    sum((select extract(epoch from avg(date_trunc('day',aml.date_created)-date_trunc('day',l.create_date)))/(24*60*60)::decimal(16,2)
#                        from account_move_line as aml
#                        left join account_invoice as a ON (a.move_id=aml.move_id)
#                        left join account_invoice_line as l ON (a.id=l.invoice_id)
#                        where a.id=ai.id)) as delay_to_pay,
#                    sum((select extract(epoch from avg(date_trunc('day',a.date_due)-date_trunc('day',a.date_invoice)))/(24*60*60)::decimal(16,2)
#                        from account_move_line as aml
#                        left join account_invoice as a ON (a.move_id=aml.move_id)
#                        left join account_invoice_line as l ON (a.id=l.invoice_id)
#                        where a.id=ai.id)) as due_delay,
#                    (case when ai.type in ('out_refund','in_invoice') then
#                      ai.residual * -1
#                    else
#                      ai.residual
#                    end)/ (CASE WHEN 
#                        (select count(l.id) from account_invoice_line as l
#                         left join account_invoice as a ON (a.id=l.invoice_id)
#                         where a.id=ai.id) <> 0 
#                       THEN
#                        (select count(l.id) from account_invoice_line as l
#                         left join account_invoice as a ON (a.id=l.invoice_id)
#                         where a.id=ai.id) 
#                       ELSE 1 
#                       END) / cr.rate as residual
#                from account_invoice_line as ail
#                left join account_invoice as ai ON (ai.id=ail.invoice_id)
#                left join product_template pt on (pt.id=ail.product_id)# -*- coding: utf-8 -*-
#                left join product_uom u on (u.id=ail.uos_id),
#                res_currency_rate cr
#                where cr.id in (select id from res_currency_rate cr2  where (cr2.currency_id = ai.currency_id)
#                and ((ai.date_invoice is not null and cr.name <= ai.date_invoice) or (ai.date_invoice is null and cr.name <= NOW())) limit 1)
#                group by ail.product_id,
#                    ai.date_invoice,
#                    ai.id,
#                    cr.rate,
#                    to_char(ai.date_invoice, 'YYYY'),
#                    to_char(ai.date_invoice, 'MM'),
#                    to_char(ai.date_invoice, 'YYYY-MM-DD'),
#                    ai.partner_id,
#                    ai.payment_term,
#                    ai.period_id,
#                    u.name,
#                    ai.currency_id,
#                    ai.journal_id,
#                    ai.fiscal_position,
#                    ai.user_id,
#                    ai.company_id,
#                    ai.type,
#                    ai.state,
#                    pt.categ_id,
#                    ai.date_due,
#                    ai.address_contact_id,
#                    ai.address_invoice_id,
#                    ai.account_id,
#                    ai.partner_bank_id,
#                    ai.residual,
#                    ai.amount_total,
#                    u.uom_type,
#                    u.category_id
#            
#        """)
#        
#        x = cr.dictfetchone()

        data = {}
        obj_cur_company = obj_company.browse(cr, uid, 1)
        data['form']={
            'customer':obj_current_customer.id,
            'fiscal_year': obj_current_fiscal_year.id,
            'fiscal_year_name' : obj_current_fiscal_year.code,
        }
        data['form'].update({'company_info': {
            'street' : obj_cur_company.partner_id.street,
            'street2' : obj_cur_company.partner_id.street2,
            'zip' : obj_cur_company.partner_id.zip,
            'city' : obj_cur_company.partner_id.city,
            'phone' : obj_cur_company.partner_id.phone,
            'email' : obj_cur_company.partner_id.email,
        }})
        
        
        cr.execute('''
                        select rp.id,rp.name as name,rp.ref,rp.vat,CASE WHEN rp.per_kalpa = True THEN
                                                          'ja'
                                                          ELSE 'nee'
                                                          END,
                               rp.email,rp.phone,rp.contact_name as contact_name,\
                               rp.street,rp.zip,rp.city,rp.title,ru.signature
                                                                     
                        
                        from res_partner rp,res_users ru
                        where rp.id = %s and rp.user_id=ru.id
                              
        
        '''%(obj_current_customer.id))
        test_partner_data = cr.dictfetchone()
        if not test_partner_data:
            test_partner_data = {}
        cr.execute("select acc_number from res_partner_bank where partner_id=%s"%(obj_current_customer.id))
        acc_data = cr.dictfetchone()
        if acc_data:
            test_partner_data.update({'acc_number':acc_data['acc_number']})
        else:
            test_partner_data.update({'acc_number': None})
            
        if test_partner_data.get('title',''):
            title_name = self.pool.get('res.partner.title').browse(cr, uid, test_partner_data['title']).name
        else:
            title_name =""
        
#        name = test_partner_data['poonam']
        name = test_partner_data.get('name','')
        name = name.replace("&","")
      
        data['form'].update({'customer_info': {
            'case' : test_partner_data.get('case',''),
            'city' : test_partner_data.get('city',obj_current_customer.city), 
#            'poonam' : name,
            'name':test_partner_data.get('name',obj_current_customer.name),
            'zip' : test_partner_data.get('zip',obj_current_customer.zip),
            'title' : title_name,
            'phone' : test_partner_data.get('phone',obj_current_customer.phone),
            'street' : test_partner_data.get('street',obj_current_customer.street),
            'contact_name' : test_partner_data.get('contact_name',obj_current_customer.contact_name),
            'ref' : test_partner_data.get('ref',obj_current_customer.ref),
            'email' : test_partner_data.get('email',obj_current_customer.email),
            'vat' : test_partner_data.get('val',obj_current_customer.vat),
            'acc_number' : test_partner_data.get('acc_number',''),
            'signature' : test_partner_data.get('signature',''),
                        
        }})
       
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales.annual.analysis',
            'datas': data,
            
        }
    
sales_analysis()
