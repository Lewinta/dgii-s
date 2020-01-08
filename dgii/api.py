import frappe

def get_tax_amount_for(doctype, docname, tax_type):
	doc = frappe.get_doc(doctype, docname)

	for row in doc.taxes:
		tax_types = row.meta.get_field("tax_type").options
		
		if not tax_type in tax_types.split("\n"):
			frappe.throw(_("The tax type provided was not found in the system!"))

		if row.tax_type == tax_type:
			return row.tax_amount

	return 0.000
	
def update_taxes_to_purchases():
	from dgii.hook.purchase_invoice import validate
	for name, in frappe.get_list("Purchase Invoice", as_list=True):
		doc = frappe.get_doc("Purchase Invoice", name )
		validate(doc, {})
		if doc.excise_tax or doc.legal_tip:
			doc.db_update()
			# print(
			# 	"""Added to {name}\n
			# 		\tExcise:{excise_tax}
			# 		\tLegal:{legal_tip} """.format(**doc.as_dict())
			# )

@frappe.whitelist()
def validate_ncf_limit(serie):
	# serie : ABC.####
	# next: 3
	# Yefri este codigo es provisional, reservar cualquier comentario gracias!

	limit = frappe.get_doc("NCF",{"serie":serie}, "max_limit").max_limit
	serie = serie.replace(".","").replace("#","")
	current = frappe.get_doc("Series",{"name":serie},"current").current
	
	return True if  current + 1  <  limit else False