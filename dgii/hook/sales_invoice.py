import frappe
from frappe.model.naming import make_autoname
from frappe.utils import cint

def autoname(doc, event):
	doc.name = make_autoname("FACT-.#####")

def before_insert(doc, event):
	if doc.amended_from or doc.ncf:
		return

	if doc.ncf and doc.against_ncf:
		return

	if doc.is_return:
		doc.against_ncf = doc.ncf

	doc.ncf = generate_new(doc)

def generate_new(doc):
	conf = get_serie_for_(doc)

	current = cint(conf.current)

	if cint(conf.max_limit) and current >= cint(conf.max_limit):
		frappe.throw("Ha llegado al maximo establecido para esta serie de comprobantes!")

	current += 1

	conf.current = current
	conf.db_update()

	return '{0}{1:08d}'.format(conf.serie.split(".")[0], current)

def get_serie_for_(doc):
	return frappe.get_doc("NCF", {
		"serie": doc.naming_series
	})