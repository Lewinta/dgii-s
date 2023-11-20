import frappe
from frappe.utils import cint

TAX_CATEGORIES_PERMITTED = ['Proveedor Informal','Gastos Menores']

def validate(doc, event):
	calculate_totals(doc)
	set_taxes(doc)
	validate_duplicate_ncf(doc)
	set_against_ncf(doc)

def before_submit(doc, event):
	generate_new(doc)

def calculate_totals(doc):
	total_bienes = total_servicios = .000

	for item in doc.items:
		if item.item_type == "Bienes":
			total_bienes += item.base_amount
		
		if item.item_type == "Servicios":
			total_servicios += item.base_amount
	
	doc.monto_facturado_bienes = total_bienes
	doc.monto_facturado_servicios = total_servicios

def generate_new(doc):
	tax_category = frappe.db.get_value(
		"Supplier",
		doc.supplier,
		"tax_category"
	)
	if doc.bill_no or not tax_category or not tax_category in TAX_CATEGORIES_PERMITTED:
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
	set_other_taxes(doc)
	set_isr(doc)
	set_retention(doc)

def set_other_taxes(doc):	
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


def set_isr(doc):
	if doc.include_isr or  not doc.total or not doc.isr_rate:
		doc.isr_amount = 0
	amount = doc.total * float(doc.isr_rate) / 100.00
	doc.isr_amount = amount
	doc.base_isr_amount = amount * doc.conversion_rate

def set_retention(doc):
	if doc.include_retention or not doc.total_taxes_and_charges or not doc.retention_rate:
		doc.retention_amount = 0
	retention_rate = 0
	
	amount = 0
	
	if doc.retention_rate == '30%':
		# Se le calcula el 30% del de los items marcados como servicios
		retention_rate = 0.30
		amount = doc.monto_facturado_servicios
	if doc.retention_rate == '100%':
		amount = doc.total_taxes_and_charges
		retention_rate = 1
	
	doc.retention_amount = amount * 0.18 * retention_rate
	doc.base_retention_amount = amount * doc.conversion_rate * retention_rate

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

def set_against_ncf(doc):
	if not doc.return_against:
		return
	return_ncf = frappe.get_value(doc.doctype, doc.return_against, "bill_no")
	doc.return_against_ncf = return_ncf