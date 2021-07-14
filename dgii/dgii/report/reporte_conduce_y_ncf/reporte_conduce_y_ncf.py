# Copyright (c) 2013, TzCode, S. R. L. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	data = []
	columns = get_columns()

	for invoice in get_invoices(filters):
		data.append([
			invoice.posting_date,
			invoice.name.split("-")[1],
			invoice.customer_rnc,
			invoice.customer,
			invoice.base_total_taxes_and_charges,
			invoice.net_total,
			invoice.grand_total
		])

	for order in get_orders(filters):
		data.append([
			order.transaction_date,
			order.name,
			order.customer_rnc,
			order.customer,
			order.base_total_taxes_and_charges,
			order.net_total,
			order.grand_total
		])

	data.sort()
	return columns, data
def get_columns():
	return [
		_("Posting Date") + ":Date:100",
		_("Invoice") + ":Data:160",
		_("Customer RNC") + "::130",
		_("Customer Name") + ":Link/Customer:250",
		_("Taxes") + "::100",
		_("Total Neto") + "::100",
		_("Gran Total") + "::100"
	]

def get_conditions(filters,doctype):
	conditions = ""
	so_conditions = ""
	si_conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"

	if filters.get("from_date"): si_conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): si_conditions += " and posting_date <= %(to_date)s"

	if filters.get("from_date"): so_conditions += " and transaction_date >= %(from_date)s"
	if filters.get("to_date"): so_conditions += " and transaction_date <= %(to_date)s"

	if doctype == "Invoice":
		return conditions + si_conditions
	else:
		return conditions + so_conditions

def get_invoices(filters):
	conditions = get_conditions(filters,"Invoice")
	return frappe.db.sql("""select name, posting_date, customer, customer_rnc, 
		grand_total,base_total_taxes_and_charges, net_total
		from `tabSales Invoice`
		where docstatus = 1 %s order by posting_date desc, name desc""" %
		conditions, filters, as_dict=1)

def get_orders(filters):
	conditions = get_conditions(filters,"Order")
	return frappe.db.sql("""select name, transaction_date, customer, customer_rnc, 
		grand_total,base_total_taxes_and_charges, net_total
		from `tabSales Order`
		where docstatus = 1 %s order by transaction_date desc, name desc""" %
		conditions, filters, as_dict=1)
