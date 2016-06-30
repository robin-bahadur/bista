from osv import osv, fields
class crm_phonecall(osv.osv):
	_inherit = "crm.phonecall"
	def default_get(self,cr,uid,ids,context=None):
		cr.execute("select setval('crm_phonecall_id_seq',(select max(id) from crm_phonecall))")
		return osv.osv.default_get(self,cr,uid,ids,context=context)

crm_phonecall()
