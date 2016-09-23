from osv import fields, osv
from tools.translate import _
import xlrd
#import StringIO
import base64
import datetime
import re
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
                in_ref = ''
                inv_no = ''
                inv_type = ''
                six_dig_no = ''
                partner_id = False
                inv_srch = ''
                tax_amount = 0.0 
                flag = False
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
                        if count==4 and value and row_count == 4: 
                            starting_balance = value
                            if float(starting_balance) != last_ending_bal:      #checking starting balance of a sheet with ending of last bank stmnt record
                                raise osv.except_osv(_('Warning!'), _('''You cannot import bank statement 
                                                  as last statement's ending balance and current starting balance did not match!!!'''))
                        if count==2 and value and row_count >=4: 
                            transaction_date = value
                        if count==7 and value and row_count >=4: 
                            desc_str = value
                            six_dig_list = []
                            six_dig = []
                            split_descr = desc_str.split(' ')
                            for word in split_descr:
                                #logic to extract digits 
                                if word and not '.' in word :
                                     six_dig = re.findall(r'\b\d{6}\b' , word)                                 
                                elif word.isdigit():
                                     if len(word) == 6:
                                        six_dig.append(word)  #appending six digit 
                                        
                    if row_count >=4:        #starting condition to append values in line_ids           
                        for key in bank_dict:   
                            if key.strip() in desc_str and (s1 and s2) not in desc_str and not six_dig: # checking if key is present in description                               
                                 for val in bank_dict.items():
                                     account_id = val[1].get('account')
                                     if  key == str(val[0]):     # checking condition if key(search word) of dict matches with val
                                         if val[1].get('sales_tax'):     # checking sales tax is true if true then create another line                                      
                                            tax_amount = float(amount) * 0.21
                                            #take sales tax account for sales tax line
                                            acc_id = account_obj.search(cr,uid,['|',('name', '=','BTW VAT Paid'),('code','=','110300')])
                                            statement_line_list.append((0,0,
                                                        {
                                                         'date':transaction_date if  transaction_date else False,
                                                         'name':desc_str if desc_str else False,
                                                         'type':'general',
                                                         'account_id':acc_id[0] if acc_id else False ,
                                                         'amount':tax_amount,                                                         
                                                             }))
                                            flag = True
                                     if not inv_type and key == str(val[0]):  # checking condition if key of dict matches with val and there is no inv type
                                             inv_type= 'general'
                                             #creating line if key(search word) is present
                                             statement_line_list.append((0,0,
                                                                    {
                                                                     'date':transaction_date ,
                                                                     'name':desc_str if desc_str else False,
                                                                     'ref': inv_no if inv_no else '',
                                                                     'type':inv_type,
                                                                     'account_id':account_id ,
                                                                     'amount':amount,                                                                     
                                                                     })) 
                                             account_id = '' 
                                             flag = True 
                        if flag == False:
                            if s1 in desc_str:          # checking if s1='KP' is present in description                   
                                    index_kp = desc_str.find(s2)  #find index of KP
                                    s_ref = desc_str[desc_str.find("KP"):].replace("KP ", "KP") 
                                    inv_ref = s_ref.find('KP')
                                    in_ref = s_ref[inv_ref:inv_ref+8]
                                    #searching invoice which is not in paid state
                                    inv_srch = invoice_obj.search(cr,uid,[('number', 'ilike',in_ref),('state', '!=','paid')])
                                    if inv_srch:
                                        inv_type = 'customer'
                                        #take account debtors if invoice is present
                                        account_id = account_obj.search(cr,uid,['|',('name', '=','Debtors'),('code','=','110200')])
                                        account_id = account_id[0]
                                    inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                    if inv_brws:
                                        inv_no = inv_brws[0].number
                                        partner_id = inv_brws[0].partner_id.id                      
            
                            elif s2 in desc_str:  # checking if s2='kp' is present in description 
                                index_kp = desc_str.find(s2)
                                s_ref = desc_str[desc_str.find("kp"):].replace("kp ", "kp")
                                inv_ref = s_ref.find('kp')
                                in_ref = s_ref[inv_ref:inv_ref+8]
                                #searching invoice which is not in paid state
                                inv_srch = invoice_obj.search(cr,uid,[('number', 'ilike',in_ref),('state', '!=','paid')])
                                if inv_srch:
                                    inv_type = 'customer'
                                    #take account debtors if invoice type is customer
                                    account_id = account_obj.search(cr,uid,['|',('name', '=','Debtors'),('code','=','110200')])
                                    account_id = account_id[0]
                                inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                if inv_brws:
                                    inv_no = inv_brws[0].number
                                    partner_id = inv_brws[0].partner_id.id
                                    
                            elif six_dig and (s1 and s2) not in desc_str: # checking if six digit no is there in description
                                        for no in six_dig:
                                            invoice_no = 'KP' + no
                                            #searching invoice which is not in paid state
                                            inv_srch = invoice_obj.search(cr,uid,[('number', 'ilike',invoice_no),('state', '!=','paid')])
                                            if inv_srch:
                                               inv_type = 'customer'
                                               #take account debtors if invoice is present
                                               account_id = account_obj.search(cr,uid,['|',('name', '=','Debtors'),('code','=','110200')])
                                               account_id = account_id[0]
                                            inv_brws = invoice_obj.browse(cr,uid,inv_srch)
                                            
                                            if inv_brws:
                                                inv_no = inv_brws[0].number
                                                partner_id = inv_brws[0].partner_id.id
                        
                        if inv_srch and inv_type == 'customer': # creating line if invoice is present and invoice type is customer
                            statement_line_list.append((0,0,
                                                    {
                                                     'date':transaction_date,
                                                     'name':desc_str if desc_str else False,
                                                     'ref': inv_no if inv_no else '',
                                                     'type':inv_type,
                                                     'account_id':account_id ,
                                                     'amount':amount,
                                                     'partner_id':partner_id if partner_id else False
                                                     
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
                if float(end_bal_list[-1]) != stmnt_brws.balance_end:
                    stmnt_brws.write({'balance_end_real':stmnt_brws.balance_end})           
        else:
            raise osv.except_osv(_('Warning!'), _('Please select csv file!!'))
