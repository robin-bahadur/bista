from openerp.osv import fields, osv


class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
                'bank_lines':fields.one2many('bank.lines', 'bank_id', 'Bank Details'),              
                }
    
    
    
class bank_lines(osv.osv):
    _name = 'bank.lines'
    _description = 'Bank Lines'
    
    
    _columns = {
                'search_word':fields.char('Search Keyword'),
                'account': fields.many2one('account.account','Account'),
                'sales_tax':fields.boolean('Sale Tax'),
                'bank_id':fields.many2one('res.company','Bank Id')
                }