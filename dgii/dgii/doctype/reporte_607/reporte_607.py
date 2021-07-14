# -*- coding: utf-8 -*-
# Copyright (c) 2015, TzCode, S. R. L. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, formatdate, format_datetime
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter
import time

class Reporte607(Document):
	pass

@frappe.whitelist()
def get_file_address(from_date, to_date):
	result = frappe.db.sql("""
		SELECT 
			cust.tax_id, 
			sinv.ncf, 
			sinv.posting_date, 
			sinv.total_taxes_and_charges, 
			sinv.tipo_de_ingreso, 
			sinv.base_total 
		FROM 
			`tabSales Invoice` AS sinv 
		JOIN 
			tabCustomer AS cust on sinv.customer = cust.name 
		WHERE 
			sinv.ncf NOT LIKE '%s' AND cust.tax_id > 0 AND sinv.docstatus = 1 AND sinv.posting_date 
		BETWEEN
			'%s' AND '%s' 
	""" % ("SINV-%", from_date, to_date), as_dict=True)

	w = UnicodeWriter()
	w.writerow(['RNC', 'Tipo de RNC', 'NCF', 'NCF modificado', 'Fecha de impresion', 'ITBIS facturado', 'Tipo de Ingreso', 'Monto Total'])
		
	for row in result:
		tipo_rnc = frappe.get_value("Customer", {"tax_id": row.tax_id }, ["tipo_rnc"])
		w.writerow([row.tax_id.replace("-", ""), tipo_rnc, row.ncf, "", row.posting_date.strftime("%Y%m%d"), row.total_taxes_and_charges, row.tipo_de_ingreso, row.base_total])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Reporte_607_" + str(int(time.time()))






 	
