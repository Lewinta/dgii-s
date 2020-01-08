# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	conditions = get_conditions(filters)
	cuentas_por_cobrar = frappe.db.sql("""SELECT customer, transaction_date, DATEDIFF(NOW(),transaction_date) AS days_late,
						grand_total, name, customer_rnc
						FROM `tabSales Order`
						WHERE delivery_date < NOW() AND status != "Closed" %s
					""" % (conditions,), filters, as_dict=1)
	monto_total = 0
	for cuenta in cuentas_por_cobrar:
		data.append([
			cuenta.transaction_date,
			cuenta.days_late,
			cuenta.name,
			cuenta.customer_rnc,
			cuenta.customer,
			cuenta.grand_total
		])
		monto_total = monto_total + cuenta.grand_total
	
	data.append(["","","","","", ""])
	data.append(["","","","","", monto_total])
	return columns, data


def get_columns():
	return [
		"Fecha" + ":Date",
		"Dias de vencimiento" + "::120",
		"Numero de conduce" + "::130",
		"NCF" + "::130",
		"Nombre del cliente" + "::400",
		"Monto Total" + ":Currency"
	]

def get_conditions(filters):
	conditions = ''
	if filters.get("company"):
		conditions += ' and company=%(company)s'

	if filters.get("from"):
		conditions += ' and transaction_date >= %(from)s'
	if filters.get("to"):
		conditions += ' and transaction_date < %(to)s'
	return conditions
