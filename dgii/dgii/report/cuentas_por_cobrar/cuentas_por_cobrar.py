# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from operator import itemgetter, attrgetter, methodcaller
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	conditions = get_conditions(filters,"Order")
	sales_orders = frappe.db.sql("""SELECT customer, transaction_date AS date, DATEDIFF(NOW(), transaction_date) AS days_late,
						grand_total, name
						FROM `tabSales Order`
						WHERE status != "Closed" AND status != "Cancelled" %s
						ORDER BY transaction_date, customer""" % (conditions), filters, as_dict=1)

	for order in sales_orders:
		data.append([
			order.date,
			order.days_late,
			order.name,
			"",
			order.customer,
			order.grand_total
		])

	conditions = get_conditions(filters,"Invoice")
	sales_invoices = frappe.db.sql("""SELECT customer, posting_date AS date, DATEDIFF(NOW(), posting_date) AS days_late,
						grand_total, ncf, serie
						FROM `tabSales Invoice`
						WHERE  outstanding_amount != 0.0 AND docstatus = 1 %s
						ORDER BY posting_date, customer""" % (conditions), filters, as_dict=1)

	for invoice in sales_invoices:
		data.append([
			invoice.date,
			invoice.days_late,
			invoice.serie,
			invoice.ncf,
			invoice.customer,
			invoice.grand_total
		])
	
	data = sorted(data, key=itemgetter(4, 0))
	data.sort()
	return columns, data


def get_columns():
	return [
		"Fecha" + ":Date",
		"Dias de vencimiento" + "::120",
		"Numero de conduce" + "::130",
		"NCF" + "::150",
		"Nombre del cliente" + "::380",
		"Monto Total" + ":Currency"
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
