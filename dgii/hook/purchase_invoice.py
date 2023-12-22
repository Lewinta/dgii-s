import frappe
import requests
from frappe import _
from frappe.utils import cint

def validate(doc, event):
	set_taxes(doc)
	calculate_totals(doc)
	validate_duplicate_ncf(doc)

def before_submit(doc, event):
	generate_new(doc)
	validate_against_dgii(doc)

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

def validate_unique_ncf_by_supplier(supplier, ncf):
	filters = {
		"bill_no": ncf,
		"supplier": supplier,
		"docstatus": 1
	}
	purchase_invoice = frappe.db.exists("Purchase Invoice", filters)
	if purchase_invoice:
		purchase_invoice_link = '<a class="bold" href="/app/purchase-invoice/' + purchase_invoice + '">' + purchase_invoice + '</a>'
		frappe.throw(_("NCF must be unique by Supplier. There is another Purchase Invoice with this bill no.: " + purchase_invoice_link))


def validate_ncf_with_dgii(rnc, ncf, my_rnc=None, sec_code=None, req_sec_code=0):
	url = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/ncf.aspx"

	template_B = "ctl00%24smMain=ctl00%24upMainMaster%7Cctl00%24cphMain%24btnConsultar&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=XCZ4rvqHtnwd7YM3b4U6mMfn0ItPGYkBoM12SSYTKJd1TaTnOHcMJD9anA71qiUum%2B%2B669VrHz1Bpak5Sl0Ck3cwpl10y9tWxXy7chZ1EkwkrniKCrMCfny72fLrv4EfZgQQ%2BA%3D%3D&__VIEWSTATEGENERATOR=43758EFE&__EVENTVALIDATION=WBF1Qy1VtSKoWmk4K3xV9vVDYUvFjNJlTU3lEBZOJnaodmVEWSnkbUbEyy3He1511rJEHxKQeHCYT2J3WZxVMo%2FSlrUKE%2B2EPrtNpqC%2BP3pOw2ddbieF7jna6LEVjwc08vUqV22f2ZseVLuDSMvIjSTrFiMllbR0dTghc9zxpXBVu6dB0rFnvFSffZNsTwY34ETro3oUmc4cNh1FmbEmAg6S26HMDIOVUJ2t3DU19k61MI5V&ctl00%24cphMain%24txtRNC={rnc}&ctl00%24cphMain%24txtNCF={ncf}&ctl00%24cphMain%24txtRncComprador=&ctl00%24cphMain%24txtCodigoSeg=&__ASYNCPOST=true&ctl00%24cphMain%24btnConsultar=Buscar"
	template_E = "ctl00%24smMain=ctl00%24upMainMaster%7Cctl00%24cphMain%24btnConsultar&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=XCZ4rvqHtnwd7YM3b4U6mMfn0ItPGYkBoM12SSYTKJd1TaTnOHcMJD9anA71qiUum%2B%2B669VrHz1Bpak5Sl0Ck3cwpl10y9tWxXy7chZ1EkwkrniKCrMCfny72fLrv4EfZgQQ%2BA%3D%3D&__VIEWSTATEGENERATOR=43758EFE&__EVENTVALIDATION=WBF1Qy1VtSKoWmk4K3xV9vVDYUvFjNJlTU3lEBZOJnaodmVEWSnkbUbEyy3He1511rJEHxKQeHCYT2J3WZxVMo%2FSlrUKE%2B2EPrtNpqC%2BP3pOw2ddbieF7jna6LEVjwc08vUqV22f2ZseVLuDSMvIjSTrFiMllbR0dTghc9zxpXBVu6dB0rFnvFSffZNsTwY34ETro3oUmc4cNh1FmbEmAg6S26HMDIOVUJ2t3DU19k61MI5V&ctl00%24cphMain%24txtRNC={rnc}&ctl00%24cphMain%24txtNCF={ncf}&ctl00%24cphMain%24txtRncComprador={my_rnc}&ctl00%24cphMain%24txtCodigoSeg={sec_code}&__ASYNCPOST=true&ctl00%24cphMain%24btnConsultar=Buscar"
	template = template_E if req_sec_code else template_B
	payload = template.format(rnc=rnc.strip(), ncf=ncf.strip(), my_rnc=my_rnc.strip(),sec_code=sec_code.strip() if sec_code else "")
	
	headers = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "en-US,en;q=0.9",
		"Cache-Control": "no-cache",
		"Connection": "keep-alive",
		"Content-Length": "874",
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Cookie": "NSC_EHJJ_OfxEfgbvmu_mcwt=ffffffffc3a0e04a45525d5f4f58455e445a4a423660; WSS_FullScreenMode=false; NSC_EHJJ_TTM_BQQ_MCWT=ffffffffc3a0e52245525d5f4f58455e445a4a42378b",
		"Host": "dgii.gov.do",
		"Origin": "https://dgii.gov.do",
		"Pragma": "no-cache",
		"Referer": "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/ncf.aspx",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
		"X-MicrosoftAjax": "Delta=true",
		"X-Requested-With": "XMLHttpRequest",
	}

	response = requests.request("POST", url, headers=headers, data=payload)
	response.encoding = 'utf-8'

	res = response.text

	return res.find("VIGENTE") > 0 or res.find("VENCIDO") > 0 or res.find("Aceptado") > 0


def validate_against_dgii(doc):
	if not (doc.tax_id):
		return

	if not doc.bill_no:
		frappe.throw("El numero de comprobante fiscal es obligatorio.")

	my_tax_id = frappe.get_value("Company", doc.company, "tax_id")
	if not my_tax_id:
		frappe.throw("Favor ingresar el RNC en la compañia (sin guiones).")

	validate_unique_ncf_by_supplier(doc.supplier, doc.bill_no)
	is_valid = validate_ncf_with_dgii(doc.tax_id, doc.bill_no, my_tax_id, doc.security_code, doc.require_security_code)

	if(is_valid):
		return

	frappe.throw(_("Numero de Comprobante Fiscal <b>NO VALIDO</b>."))
