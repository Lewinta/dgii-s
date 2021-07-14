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
			invoice.name,
			invoice.customer_rnc,
			invoice.customer,
			invoice.base_total_taxes_and_charges,
			invoice.net_total,
			invoice.grand_total
		])

	return columns, data


def get_columns():
	return [
		_("Posting Date") + ":Date:100",
		_("Invoice") + ":Link/Sales Invoice:120",
		_("Customer RNC") + "::120",
		_("Customer Name") + ":Link/Customer:120",
		_("Taxes") + "::80",
		_("Total Neto") + "::80",
		_("Gran Total") + "::90"
	]

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"

	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"

	return conditions

def get_invoices(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date, customer, customer_rnc, 
		grand_total,base_total_taxes_and_charges, net_total
		from `tabSales Invoice`
		where docstatus = 1 %s order by posting_date asc, name desc""" %
		conditions, filters, as_dict=1)
