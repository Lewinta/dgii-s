# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

# from .hook.landed_cost_voucher import landed_cost_voucher_validate_override

app_name = "dgii"
app_title = "DGII"
app_publisher = "TzCode, S. R. L."
app_description = "Una aplicacion para la generacion de los reportes que son enviados a la Direccion General de Impuestos Internos en la Republica Dominicana"
app_icon = "octicon octicon-flame"
app_color = "#469"
app_email = "servicios@soldeva.com"
app_license = "MIT"


# Fixtures
# --------

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": {
			"name": (
				"in", (
					"Customer-tipo_rnc",
					"Item-item_type",
					"Landed Cost Taxes and Charges-column_break_7",
					"Landed Cost Taxes and Charges-total",
					"Landed Cost Taxes and Charges-tax_rate",
					"Landed Cost Taxes and Charges-create_invoice",
					"Landed Cost Taxes and Charges-description_sb",
					"Landed Cost Taxes and Charges-invoice",
					"Landed Cost Taxes and Charges-totals",
					"Landed Cost Taxes and Charges-supplier_invoice",
					"Landed Cost Taxes and Charges-date",
					"Landed Cost Taxes and Charges-currency",
					"Landed Cost Taxes and Charges-exchange_rate",
					"Landed Cost Taxes and Charges-supplier",
					"Landed Cost Taxes and Charges-expiry_date",
					"Landed Cost Taxes and Charges-purchase_taxes_and_charges_template",
					"Landed Cost Taxes and Charges-cost_center",
					"Landed Cost Taxes and Charges-tipo_bienes_y_servicios_comprados",
					"Landed Cost Taxes and Charges-is_petty_cash",
					"Landed Cost Taxes and Charges-supplier_invoice_no",
					"Landed Cost Taxes and Charges-tax_amount",
					"Purchase Invoice Item-item_type",
					"Purchase Invoice-column_break_80",
					"Purchase Invoice-excise_tax",
					"Purchase Invoice-include_isr",
					"Purchase Invoice-include_retention",
					"Purchase Invoice-is_petty_cash",
					"Purchase Invoice-isr_amount",
					"Purchase Invoice-isr_rate",
					"Purchase Invoice-legal_tip",
					"Purchase Invoice-monto_facturado_bienes",
					"Purchase Invoice-monto_facturado_servicios",
					"Purchase Invoice-other_taxes",
					"Purchase Invoice-retenciones",
					"Purchase Invoice-retention_amount",
					"Purchase Invoice-retention_rate",
					"Purchase Invoice-retention_type",
					"Purchase Invoice-return_against_ncf",
					"Purchase Invoice-return_sb",
					"Purchase Invoice-section_break_88",
					"Purchase Invoice-supplier_invoice_no",
					"Purchase Invoice-tax_id",
					"Purchase Invoice-tipo_bienes_y_servicios_comprados",
					"Purchase Invoice-total_itbis",
					"Purchase Invoice-vencimiento_ncf",
					"Sales Invoice-tipo_de_anulacion",
					"Sales Invoice-tipo_de_factura",
					"Sales Invoice-return_against_ncf",
					"Sales Invoice-ncf",
					"Sales Invoice-tipo_de_ingreso",
					"Sales Taxes and Charges-tax_type",
					"Supplier-tipo_rnc",
				)
			)
		}
	},
	{
		"doctype": "Property Setter",
		"filters": {
			"name": (
				"in", (
					"Landed Cost Taxes and Charges-editable_grid",
					"Landed Cost Taxes and Charges-invoice-no_copy",
					"Landed Cost Taxes and Charges-supplier_invoice-no_copy",
					"Landed Cost Taxes and Charges-amount-read_only",
					"Landed Cost Taxes and Charges-amount-default",
					"Landed Cost Taxes and Charges-read_only_onload",
					"Landed Cost Taxes and Charges-transaction_group-width",
					"Landed Cost Taxes and Charges-description-reqd",
					"Landed Cost Taxes and Charges-amount-columns",
					"Landed Cost Taxes and Charges-description-in_list_view",
					"Purchase Invoice-bill_date-reqd",
					"Purchase Invoice-bill_no-in_standard_filter",
					"Purchase Invoice-bill_no-label",
					"Customer-tax_id-label",
					"Customer-quick_entry",
					"Supplier-tax_id-in_list_view",
					"Supplier-pan-hidden",
					"Supplier-tax_id-in_standard_filter",
				)
			)
		}
	}	
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_js = "/assets/dgii/js/dgii.js"

# include js, css files in header of web template
# web_include_css = "/assets/dgii/css/dgii.css"
# web_include_js = "/assets/dgii/js/dgii.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "dgii.utils.get_home_page"

# Doctype JS
# ----------
doctype_js = {
	"Purchase Invoice": "public/js/purchase_invoice.js",
	"Customer": "public/js/customer.js",
	"Supplier": "public/js/supplier.js",
	"Landed Cost Voucher": "public/js/landed_cost_voucher.js",
	"Company": "public/js/company.js",
	"Purchase Order": "public/js/purchase_order.js",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "dgii.install.before_install"
# after_install = "dgii.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dgii.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# erpnext
	"Purchase Invoice": {
		"validate": "dgii.hook.purchase_invoice.validate",
		"before_submit": "dgii.hook.purchase_invoice.before_submit",
	},
    "Sales Invoice": {
        "autoname": "dgii.hook.sales_invoice.autoname",
		"validate": "dgii.hook.sales_invoice.validate",
        "before_insert": "dgii.hook.sales_invoice.before_insert",
        "before_submit": "dgii.hook.sales_invoice.before_submit",
        "on_change": "dgii.hook.sales_invoice.on_change",
    },
	"Landed Cost Voucher": {
        "on_submit": "dgii.hook.landed_cost_voucher.on_submit",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"dgii.tasks.all"
# 	],
# 	"daily": [
# 		"dgii.tasks.daily"
# 	],
# 	"hourly": [
# 		"dgii.tasks.hourly"
# 	],
# 	"weekly": [
# 		"dgii.tasks.weekly"
# 	]
# 	"monthly": [
# 		"dgii.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "dgii.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dgii.event.get_events"
# }
	