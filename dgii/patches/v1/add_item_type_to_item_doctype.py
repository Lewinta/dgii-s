import frappe

def execute():
	if frappe.db.exists("Custom Field", "Item-item_type"):
		print("Custom Field Already exists")
		return

	print("Custom Field doesn't exists let's create it!")
	frappe.get_doc({
		'allow_on_submit': 0,
 		'bold': 0,
		'collapsible': 0,
		'collapsible_depends_on': None,
		'columns': 0,
		'default': None,
		'depends_on': None,
		'description': 'Para ser usado en el Reporte 606',
		'doctype': 'Custom Field',
		'dt': 'Item',
		'fieldname': 'item_type',
		'fieldtype': 'Select',
		'hidden': 0,
		'ignore_user_permissions': 0,
		'ignore_xss_filter': 0,
		'in_global_search': 0,
		'in_list_view': 0,
		'in_standard_filter': 0,
		'insert_after': 'item_group',
		'label': 'Item Type',
		'no_copy': 0,
		'options': 'Bienes\nServicios',
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
