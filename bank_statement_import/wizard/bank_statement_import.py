from osv import fields, osv
from tools.translate import _
#import xlrd
#import StringIO
import base64
from datetime import datetime
import re
import time
import csv
import StringIO as baseStringIO
from cStringIO import StringIO as csIO

class bank_stmnt_import(osv.osv_memory):
    
    _name = 'bank.stmnt.import'
    _columns = {
                'import_file':fields.binary('Choose Excel File (.csv)'),
                'filename':fields.char('File name'),
}
    csv.register_dialect(
        'mydialect',
        delimiter = ',',
        quotechar = '"',
        doublequote = True,
        skipinitialspace = True,
        lineterminator = '\r\n',
        quoting = csv.QUOTE_MINIMAL)
    
    def create_voucher_id(self, cr, uid, move_id, statement_id, ref, context=None):
        voucher_id = ''
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        line_obj = self.pool.get('account.move.line')
        line_date = time.strftime('%Y-%m-%d')
        if move_id:
            for line_move_ids in move_id.line_id:
                amount = 0.0
                if line_move_ids.debit > 0:
                    amount = line_move_ids.debit
                elif line_move_ids.credit > 0:
                    amount = -line_move_ids.credit
                if line_move_ids.amount_currency:
                    amount = currency_obj.compute(cr, uid, line_move_ids.currency_id.id,
                    statement_id.currency.id, line_move_ids.amount_currency, context=ctx)
                elif (line_move_ids.invoice and line_move_ids.invoice.currency_id.id <> statement_id.currency.id):
                    amount = currency_obj.compute(cr, uid, line_move_ids.invoice.currency_id.id,
                    statement_id.currency.id, amount, context=ctx)
                ttype = amount < 0 and 'payment' or 'receipt'
                sign = 1
                if line_move_ids.journal_id.type in ('sale', 'sale_refund'):
                    ttype = 'receipt'
                elif line_move_ids.journal_id.type in ('purchase', 'purhcase_refund'):
                    ttype = 'payment'
                    sign = -1
                context.update({'move_line_ids': [line_move_ids.id],
                            'invoice_id': line_move_ids.invoice.id})
                result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line_move_ids.partner_id.id, journal_id=statement_id.journal_id.id, amount=1*amount, currency_id= statement_id.currency.id, ttype='receipt', date=line_date, context=context)
                voucher_res = { 'type': ttype,
                        'name': line_move_ids.name,
                        'partner_id': line_move_ids.partner_id.id,
                        'journal_id': statement_id.journal_id.id,
                        'account_id': result['value'].get('account_id', statement_id.journal_id.default_credit_account_id.id),
                        'company_id': statement_id.company_id.id,
                        'currency_id': statement_id.currency.id,
                        'date': statement_id.date,
                        'amount': sign*amount,
                        'payment_rate': result['value']['payment_rate'],
                        'payment_rate_currency_id': result['value']['payment_rate_currency_id'],
                        'period_id':statement_id.period_id.id}
                voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
                voucher_line_dict =  {}
                for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
                    move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                    if line_move_ids.move_id.id == move_line.move_id.id:
                        voucher_line_dict = line_dict
                if voucher_line_dict:
                    voucher_line_dict.update({'voucher_id': voucher_id})
                    voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                if voucher_id:
                    return voucher_id
        return voucher_id
    
    def imp_file(self, cr, uid, ids,context):
        """ function to import bank statement csv file  """
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        journal_obj =  self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        invoice_obj = self.pool.get('account.invoice')
        company_obj = self.pool.get('res.company')
        user_obj = self.pool.get('res.users')
        current_user = user_obj.browse(cr, uid, uid, context=context)
        company_brw = current_user.company_id
        word_list = []
        val_list = []
        all_val = []
        start_end_bal = True
        statement_line_list=[]
        bank_dict = {}  
        end_bal = []       
        date_val = []   
        descr_list = []
        inv_refrence= ''
        index_kp =''
        s1 = 'KP'
        s2 = 'kp'
        end_bal_list = []   
        strt_bal_lst = [] 
        strt_bal_lst = [] 
        row_count = 0
        amount = 0.0
        transaction_date = '' 
        search_ids = statement_obj.search(cr, uid, [])        
        last_id = search_ids and max(search_ids) #searching last record id
        last_stmnt_brw = statement_obj.browse(cr,uid,last_id)
        last_ending_bal = last_stmnt_brw.balance_end_real #getting ending balance of last record
        
        if isinstance(ids,list):
            ids= ids[0]
            
        for line in company_brw.bank_lines:
            search_word = str(line.search_word)            
            search_word_1 = search_word.strip()
            word_list.append(search_word_1)
        for word in word_list:
            for line in company_brw.bank_lines:
                if word == line.search_word:
                    bank_dict[word] = {'account':line.account.id,'sales_tax':line.sales_tax} #making dictionary as search word as key
      #  file_data = self.browse(cr,uid,ids).import_file
       # filename= self.browse(cr,uid,ids).filename
        csvfile = self.browse(cr,uid,ids).import_file
         
        if csvfile:
            csvfile = base64.b64decode(csvfile)
            for row in csv.reader(csIO(csvfile),dialect='mydialect'): # reading data from csv 
                s_ref = ''
                inv_ref = ''
		desc_str = ''
                in_ref = ''
                inv_no = ''
                inv_type = ''
                six_dig_no = ''
                partner_id = False
                csv_account_no = ''  
                inv_srch = ''
                tax_amount = 0.0 
                flag = False
                kp_flag = False
                else_flag = False
                if len(row):
                    count = len(row)
                    while count >= 0:
                        count = count-1
                        if count == -1:
                            count=0
                            break
                        
                        value = row[count]
                        if row_count==0 and value and count==3:
                            journal = value
                            journal_search = journal_obj.search(cr,uid,[('name', 'ilike',journal)])
                        if count==1 and value and row_count==0:
                            reference = value
                        if row_count==1 and value and count==1:
                            statement_date = value
                        if count==3 and value and row_count==1:
                            period = value
                            period_search = period_obj.search(cr,uid,[('name', 'ilike',period)])
                        if count==6 and value and row_count>=4: 
                            amount = value
                        if  count==5 and value and row_count>=4:
                            ending_balance = value                       
                            end_bal_list.append(ending_balance)
                        if  count==0 and value and row_count>=4:
                            csv_account_no = value
                        if count==4 and value and row_count == 4 and start_end_bal == True: 
                            start_end_bal = False
                            starting_balance = value
                            if float(starting_balance) != last_ending_bal:      #checking starting balance of a sheet with ending of last bank stmnt record
                                raise osv.except_osv(_('Warning!'), _('''You cannot import bank statement 
                                                  as last statement's ending balance and current starting balance did not match!!!'''))
                        if count==2 and value and row_count >=4: 
                            transac_date = value
                            datetimeobject = datetime.strptime(transac_date,'%Y%m%d')
                            transaction_date = datetimeobject.strftime('%Y/%m/%d')
                            
                        if count== 7 and value and row_count >= 4: 
                            
                            desc_str = value
                            upper_case_desc = desc_str.upper()
                            lower_case_desc = desc_str.lower()
                            six_dig_list = []
                            six_dig = []
                            split_descr = desc_str.split(' ')
#                            [int(s) 
                            for s in desc_str.split(): 
                                if s.isdigit():
                                    if len(s) == 6:
                                        ints = 'KP'+ s
                                        six_dig_list.append(ints)
#                            for word in split_descr:
#                                #logic to extract digits 
#                                if word and not '.' in word :
#                                     six_dig = re.findall(r'\b\d{6}\b' , word)                                 
#                                elif word.isdigit():
#                                     if len(word) == 6:
#                                        six_dig.append(word)  #appending six digit 
                                    
                    if row_count >=4:        #starting condition to append values in line_ids

                        if flag == False:
                            inv_ids = invoice_obj.search(cr,uid,[('number', 'in',six_dig_list),('state', '=','open')])
                            if six_dig_list and (s1 and s2) not in desc_str and inv_ids: # checking if six digit no is there in description
                                for no in six_dig_list:
                                    invoice_no = no
                                    inv_srch = invoice_obj.search(cr,uid,[('number', '=',invoice_no),'|',('state', '=','open'),('state', '=','paid')])
                                    #searching invoice which is not in paid state
                                    if inv_srch:
                                        if statement_line_list and statement_line_list[0]:
                                            for each_statement_line_list in statement_line_list:
                                                if each_statement_line_list[2].get('ref') == in_ref:
                                                    flag = False
                                                    inv_type = 'customer'
                                                    inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                                    inv_no = inv_brws[0].number
                                                    account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                                    account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                                    amount = amount
                                                    partner_id = inv_brws[0].partner_id.id
                                    if inv_srch:
                                        flag = False
                                        inv_type = 'customer'
                                        inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                        inv_no = inv_brws[0].number
                                        partner_id = inv_brws[0].partner_id.id
                                        account_id = inv_brws[0].account_id.id
                                        if float(amount) == inv_brws[0].amount_total:
                                            amount = amount
                                            break
                                        else:
                                            account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                            account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                            amount = amount
                                            partner_id = ''
                                            break
                                        if inv_brws[0].state == 'paid':
                                            account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                            account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                            amount = amount
                                            break
                                    else:
                                        flag = True
                            elif s1 in desc_str:          # checking if s1='KP' is present in description 
            #                                    index_kp = desc_str.find(s2)  #find index of KP
                                s_ref = desc_str[desc_str.find("KP"):].replace("KP ", "KP") 
                                inv_ref = s_ref.find('KP')
                                in_ref = s_ref[inv_ref:inv_ref+8]
                                #searching invoice which is not in paid state
                                inv_srch = invoice_obj.search(cr,uid,[('number', 'ilike',in_ref),'|',('state', '=','open'),('state', '=','paid')])
                                if inv_srch:
                                    flag = False
                                    inv_type = 'customer'
                                    inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                    inv_no = inv_brws[0].number
                                    partner_id = inv_brws[0].partner_id.id                      
                                    account_id = inv_brws[0].account_id.id
                                    if float(amount) == inv_brws[0].amount_total:
                                        amount = amount
                                    else:
                                        account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                        account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                        amount = amount
                                        partner_id = ''
                                    if inv_brws[0].state == 'paid':
                                        account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                        account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                        amount = amount
                                    if statement_line_list and statement_line_list[0]:
                                        for each_statement_line_list in statement_line_list:
                                            if each_statement_line_list[2].get('ref') == in_ref:
                                                flag = False
                                                inv_type = 'customer'
                                                inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                                inv_no = inv_brws[0].number
                                                account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                                account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                                amount = amount
                                                partner_id = inv_brws[0].partner_id.id
                                else:
                                    flag = True
                            elif s2 in desc_str:  # checking if s2='kp' is present in description 
            #                                index_kp = desc_str.find(s2)
                                s_ref = desc_str[desc_str.find("kp"):].replace("kp ", "kp")
                                inv_ref = s_ref.find('kp')
                                in_ref = s_ref[inv_ref:inv_ref+8]
                                #searching invoice which is not in paid state
                                inv_srch = invoice_obj.search(cr,uid,[('number', 'ilike',in_ref),'|',('state', '=','open'),('state', '=','paid')])
                                if inv_srch:
                                    flag = False
                                    inv_type = 'customer'
                                    inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                    inv_no = inv_brws[0].number
                                    partner_id = inv_brws[0].partner_id.id                      
                                    account_id = inv_brws[0].account_id.id
                                    if float(amount) == inv_brws[0].amount_total:
                                        amount = amount
                                    else:
                                        account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                        account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                        amount = amount
                                        partner_id = ''

                                    if inv_brws[0].state == 'paid':
                                            account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                            account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                            amount = amount
                                    if statement_line_list and statement_line_list[0]:
                                        for each_statement_line_list in statement_line_list:
                                            if each_statement_line_list[2].get('ref') == in_ref:
                                                flag = False
                                                inv_type = 'customer'
                                                inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                                inv_no = inv_brws[0].number
                                                account_ids = account_obj.search(cr,uid,[('code','=','99999')])
                                                account_id = invoice_obj.browse(cr,uid,account_ids[0]).id
                                                amount = amount
                                                partner_id = inv_brws[0].partner_id.id
                                else:
                                    flag = True
                            else:
                                flag = True
                            if inv_srch and inv_type == 'customer': # creating line if invoice is present and invoice type is customer
                                statement_line_list.append((0,0,
                                                        {
                                                         'date':transaction_date,
                                                         'name':desc_str if desc_str else False,
                                                         'ref': inv_no if inv_no else '',
                                                         'type':inv_type,
                                                         'account_id':account_id ,
                                                         'amount':amount,
                                                         'partner_id':partner_id,
                                
                                                       }))
                                count=0
                                row_count+=1
                                continue
                        if flag == True:
                            my_count = 0
                            else_count = 0  # this count is used for when all key not in csv description 
                            base_amount = 0.0
                            actual_amount = 0.0
                            for key in bank_dict:
                                if key.strip() in desc_str or key.upper() in upper_case_desc or key.lower() in lower_case_desc and (s1 and s2) not in desc_str and not six_dig_list: # checking if key is present in description
                                    else_count = 0
                                    for val in bank_dict.items():
                                        account_id = val[1].get('account')
                                        if key == str(val[0]):
                                            if val[1].get('sales_tax') and not my_count > 1:     # checking condition if key(search word) of dict matches with val
                                                # checking sales tax is true if true then create another line                                      
#                                               tax_amount = float(amount) * 0.21
                                                my_count += 1
                                                base_amount = float(amount) / 1.21
                                                actual_amount = float(base_amount) * 0.21
                                                #take sales tax account for sales tax line
                                                acc_id = account_obj.search(cr,uid,['|',('name', '=','BTW VAT Paid'),('code','=','110300')])
                                                statement_line_list.append((0,0,
                                                            {
                                                              'date':transaction_date if  transaction_date else False,
                                                              'name':desc_str if desc_str else False,
                                                              'ref': '',
                                                              'type':'general',
                                                              'account_id':acc_id[0] if acc_id else False ,
                                                              'amount':actual_amount,                                                         
                                                               }))
                                                flag = True
                                        if not inv_type and key == str(val[0]):  # checking condition if key of dict matches with val and there is no inv type
                                            inv_type= 'general'
                                            #creating line if key(search word) is present
                                            my_count += 1
                                            statement_line_list.append((0,0,
                                                                    {
                                                                     'date':transaction_date ,
                                                                     'name':desc_str if desc_str else False,
                                                                     'ref': '',
                                                                     'type':inv_type,
                                                                     'account_id':account_id ,
                                                                     'amount':base_amount or float(amount),                                                                    
                                                                     })) 
                                            account_id = '' 
                                            flag = True
                                else:
                                    else_count += 1
                            if  else_count == len(bank_dict) :  
                                if csv_account_no:
                                    account_id = account_obj.search(cr,uid,[('code','=', csv_account_no)])
                                    if not account_id:
                                        account_id = account_obj.search(cr,uid,[('code','=', '99999')])
                                else:
                                    account_id = account_obj.search(cr,uid,[('code','=', '99999')])
                                statement_line_list.append((0,0,
                                                                    {
                                                                     'date':transaction_date ,
                                                                     'name':desc_str if desc_str else False,
                                                                     'ref': '',
                                                                     'type':inv_type,
                                                                     'account_id':account_id[0] ,
                                                                     'amount':amount,                                                                     
                                                                     }))
                    
                    count=0
                    row_count+=1
                    
            stmnt_search = statement_obj.search(cr, uid, [('name','=',reference)])
            if stmnt_search:    
                    raise osv.except_osv(_('Warning!'), _('Bank Statement is already created for this reference!!'))         
            else:
                stmnt_id = statement_obj.create(cr,uid,{
                                       'name':reference,'journal_id':journal_search[0],
                                       'date':statement_date if statement_date else False,'period_id':period_search[0],
                                       'balance_start':starting_balance,
                                       'balance_end_real' :end_bal_list[-1],
                                       'line_ids':statement_line_list
                                    })
                stmnt_brws = statement_obj.browse(cr,uid,stmnt_id)
                for each_line in stmnt_brws.line_ids:
                    ref = each_line.ref
                    amount = each_line.amount
                    same_line_invoic = statement_line_obj.search(cr,uid,[('statement_id', '=', each_line.statement_id.id),('ref', '=', ref),('account_id','=', 173 ), ('id','=', each_line.id)])
                    # above serach if avoiding to creating voiucher if statement line have have 2 or more than 2 invoices
                    # if same_line_invoic is not found then vouche create for that id
                    inv_srch = invoice_obj.search(cr,uid,[('number', '=',ref),('state', '=','open'),('amount_total','=',amount)])
                    if inv_srch and not same_line_invoic:
                        move_id = invoice_obj.browse(cr,uid,inv_srch[0]).move_id
                        voucher_id = self.create_voucher_id(cr, uid, move_id, stmnt_brws,ref, context)
                        each_line.write({'voucher_id':voucher_id})
                if float(end_bal_list[-1]) != stmnt_brws.balance_end:
                    stmnt_brws.write({'balance_end_real':stmnt_brws.balance_end})           
        else:
            raise osv.except_osv(_('Warning!'), _('Please select csv file!!'))
