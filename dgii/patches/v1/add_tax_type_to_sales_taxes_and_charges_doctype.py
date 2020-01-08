import frappe

def execute():
	if frappe.db.exists("Custom Field", "Sales Taxes and Charges-tax_type"):	return

	frappe.get_doc({
		'allow_on_submit': 0,
		'bold': 1,
		'collapsible': 0,
		'collapsible_depends_on': None,
		'columns': 0,
		'default': 'ITBIS Facturado',
		'depends_on': None,
		'description': None,
		'doctype': 'Custom Field',
		'dt': 'Sales Taxes and Charges',
		'fieldname': 'tax_type',
		'fieldtype': 'Select',
		'hidden': 0,
		'ignore_user_permissions': 0,
		'ignore_xss_filter': 0,
		'in_global_search': 0,
		'in_list_view': 0,
		'in_standard_filter': 0,
		'insert_after': 'cb_tax_type',
		'label': 'Tax Type',
		'name': 'Sales Taxes and Charges-tax_type',
		'no_copy': 0,
		'options': 'ITBIS Facturado\nITBIS Retenido por Terceros\nITBIS Percibido\nRetencion Renta por Terceros\nISR Percibido\nImpuesto Selectivo al Consumo\nOtros Impuestos/Tasas\nMonto Propina Legal',
		'permlevel': 0,
		'precision': '',
		'print_hide': 0,
		'print_hide_if_no_value': 0,
		'print_width': None,
		'read_only': 0,
		'report_hide': 0,
		'reqd': 1,
		'search_index': 0,
		'unique': 0,
		'width': None
	}).insert()