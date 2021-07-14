import frappe
from frappe.utils import cint

def validate(doc, event):
	set_taxes(doc)
	calculate_totals(doc)
	validate_duplicate_ncf(doc)

def before_submit(doc, event):
	generate_new(doc)

def calculate_totals(doc):
	total_bienes = total_servicios = .000

	for item in doc.items:
		if item.item_type == "Bienes":
			total_bienes += item.amount
		
		if item.item_type == "Servicios":
			total_servicios += item.amount
	
	doc.monto_facturado_bienes = total_bienes
	doc.monto_facturado_servicios = total_servicios

def generate_new(doc):
	tax_category = frappe.db.get_value(
		"Supplier",
		doc.supplier,
		"tax_category"
	)
	if doc.bill_no or not tax_category:
		return

	conf = get_serie_for_(doc)

	current = cint(conf.current)

	if cint(conf.top) and current >= cint(conf.top):
		frappe.throw(
			"Ha llegado al máximo establecido para esta serie de comprobantes!")

	current += 1

	conf.current = current
	conf.db_update()

	doc.bill_no = '{0}{1:08d}'.format(conf.serie.split(".")[0], current)
	doc.vencimiento_ncf = conf.expiration
	doc.db_update()
	frappe.db.commit()


def get_serie_for_(doc):
	supplier_category = frappe.get_value("Supplier", doc.supplier, "tax_category")
	if not supplier_category:
		frappe.throw(
			"""Favor seleccionar una categoría de impuestos para el 
			suplidor <a href='/desk#Form/Supplier/{0}'>{0}</a>""".format(doc.supplier_name)
		)
	
	filters = {
		"company": doc.company,
		"tax_category": supplier_category,
		# "serie": "B11.##########"
	}
	if not frappe.db.exists("Comprobantes Conf", filters):
		frappe.throw("No existe una secuencia de NCF para el tipo {}".format(supplier_category))

	return frappe.get_doc("Comprobantes Conf", filters)

def set_taxes(doc):	
	conf = frappe.get_single(
		"DGII Settings"
	)
	
	total_tip = total_excise = .000

	if conf.itbis_account:
		total_tip = sum( 
			[ row.base_tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.itbis_account,
					doc.taxes
				)
			]

		)
		doc.total_itbis = total_tip

	if conf.legal_tip_account:
		total_tip = sum( 
			[ row.base_tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.legal_tip_account,
					doc.taxes
				)
			]

		)
		doc.legal_tip = total_tip
		
	if conf.excise_tax:
		total_excise = sum( 
			[ row.base_tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.excise_tax,
					doc.taxes
				)
			]

		)
		doc.excise_tax = total_excise
	
	if conf.other_taxes:
		for tax in conf.other_taxes:
			total_amount = .000
			total_amount = sum( 
				[ row.base_tax_amount_after_discount_amount for row in filter(
						lambda x: x.account_head == tax.account,
						doc.taxes
					)
				]
			)
			doc.set(tax.tax_type, total_amount)

def validate_duplicate_ncf(doc):
	if not doc.bill_no:
		return 

	filters = {
		"tax_id": doc.tax_id,
		"bill_no": doc.bill_no,
		"docstatus": 1,
		"name": ["!=", doc.name],
	}
	if frappe.db.exists("Purchase Invoice", filters):
		frappe.throw("""
			Ya existe una factura registrada a nombre de <b>{supplier_name}</b> 
			con el mismo NCF <b>{bill_no}</b>, favor verificar!
		""".format(**doc.as_dict()))