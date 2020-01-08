# -*- coding: utf-8 -*-
# Copyright (c) 2017, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, formatdate, format_datetime
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter
import time

class Reporte608(Document):
	pass

@frappe.whitelist()
def get_file_address(from_date, to_date):

	result = frappe.db.sql(
		query = """SELECT ncf, posting_date, tipo_de_anulacion 
			FROM `tabSales Invoice` 
			WHERE docstatus = %(cancelled)s 
			AND posting_date >= '%(from_date)s' 
			AND posting_date <= '%(to_date)s'""" % 
		{ 
			"cancelled": 2,
			"from_date": from_date,
			"to_date": to_date
		}, 
		as_dict = True, 
		as_utf8 = 1
	)

	w = UnicodeWriter(encoding='Windows-1252')
	w.writerow([
		"Numero de Comprobante Fiscal",
		"",
		"Fecha de Comprobante",
		"Tipo de Anulacion",
		"Estatus"
	])
		
	for row in result:
		#bill_no = row.bill_no.split("-")[1] if(len(row.bill_no.split("-")) > 1) else row.bill_no # NCF-A1##% || A1##%
		year  = str(row.posting_date).split("-")[0]
		month  = str(row.posting_date).split("-")[1]
		date  = str(row.posting_date).split("-")[2]

		w.writerow([
			row.ncf,
			"",
			year + month + date,
			row.tipo_de_anulacion,
			""
		])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Reporte_608_" + str(int(time.time()))