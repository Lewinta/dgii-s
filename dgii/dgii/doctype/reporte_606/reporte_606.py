# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, formatdate, format_datetime
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter
import time
from frappe import _

class Reporte606(Document):
	pass

@frappe.whitelist()
def get_file_address(from_date,to_date):
	result = frappe.db.sql("""
		SELECT 
			pinv.tax_id,
			supl.tipo_rnc,
			pinv.tipo_bienes_y_servicios_comprados,
			pinv.bill_no,
			pinv.bill_date,
			pinv.excise_tax,
			pinv.base_taxes_and_charges_added,
			pinv.retention_amount,
			pinv.isr_amount,
			pinv.total_itbis,
			pinv.other_taxes,
			pinv.legal_tip,
			pinv.base_total,
			pinv.monto_facturado_servicios,
			pinv.monto_facturado_bienes
		FROM 
			`tabPurchase Invoice` AS pinv
		LEFT JOIN 
			`tabSupplier` AS supl
		ON 
			supl.name = pinv.supplier
		WHERE
			pinv.docstatus = 1 
		AND 
			pinv.bill_date BETWEEN '%s' AND '%s' 

	""" % (from_date,to_date), debug=True, as_dict=True)
	w = UnicodeWriter()
	w.writerow([
		'RNC o Cedula',
		'Tipo Id',
		'Tipo Bienes y Servicios Comprados',
		'NCF',
		'NCF o Documento Modificado',
		'Fecha Comprobante',
		'',
		'Fecha Pago',
		'',
		'Monto Facturado en Servicios',
		'Monto Facturado en Bienes',
		'Total Monto Facturado',
		'ITBIS Facturado',
		'ITBIS Retenido',
		'ITBIS sujeto a Proporcionalidad (Art. 349)',
		'ITBIS llevado al Costo',
		'ITBIS por Adelantar',
		'ITBIS percibido en compras',
		'Tipo de Retencion en ISR',
		'Monto Retención Renta',
		'ISR Percibido en compras',
		'Impuesto Selectivo al Consumo',
		'Otros Impuesto/Tasas',
		'Monto Propina Legal',
		])
		
	for row in result:
		bill_no = row.bill_no.split("-")[1] if(len(row.bill_no.split("-")) > 1) else row.bill_no # NCF-A1##% || A1##%
		w.writerow([
			row.tax_id, 	# RNC
			row.tipo_rnc, 	# Tipo de RNC
			row.tipo_bienes_y_servicios_comprados,
			bill_no,		# NCF
			'',				# NCF modificado
			row.bill_date.strftime("%Y%m"), # FC AAAAMM
			row.bill_date.strftime("%d"),	# FP DD
			row.bill_date.strftime("%Y%m"), # FP AAAAMM
			row.bill_date.strftime("%d"),	# FP DD
			row.monto_facturado_servicios,	# Monto Facturado en Servicios
			row.monto_facturado_bienes,		# Monto Facturado en Bienes
			row.base_total,					# Monto Facturado
			row.total_itbis, # ITBIS Facturado
			row.retention_amount or 0,  			# ITBIS Retenido
			'0',  							# ITBIS sujeto a Proporcionalidad (Art. 349)
			row.total_itbis or 0, # ITBIS llevado al Costo
			'0',  							# ITBIS por Adelantar
			'0',  							# ITBIS percibido en compras
			'',  							# Tipo de Retención en ISR
			row.isr_amount  or 0,  				# Monto Retención Renta
			'0',  							# ISR Percibido en compras
			row.excise_tax or 0,  				# Impuesto Selectivo al Consumo
			row.other_taxes or 0,  			# Otros Impuesto/Tasas
			row.legal_tip,  				# Monto Propina Legal
		])
										
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Reporte_606_" + str(int(time.time()))
	