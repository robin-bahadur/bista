import time
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw


class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'


    def _check_amount(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.voucher_id:
                diff = abs(obj.amount) - abs(obj.voucher_id.amount)
                if not self.pool.get('res.currency').is_zero(cr, uid, obj.statement_id.currency, diff):
                    return False
        return True
    _constraints = [
        (_check_amount, 'The amount of the voucher must be the same amount as the one on the statement line.', ['amount']),
    ]
    
    
account_bank_statement_line()


###new_server_update