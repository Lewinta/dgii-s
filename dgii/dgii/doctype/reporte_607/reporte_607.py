# -*- coding: utf-8 -*-
# Copyright (c) 2015, Soldeva, SRL and contributors
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
			cust.tipo_rnc,
			sinv.ncf,
			sinv.return_against_ncf,
			sinv.tipo_de_ingreso,
			sinv.posting_date,
			(SELECT posting_date FROM `viewRetention By Invoice` WHERE reference_name = sinv.name) AS payment_date,
			sinv.base_total,
			sinv.base_grand_total,
			sinv.base_total_taxes_and_charges,
			(SELECT COALESCE(retention_amount, '') FROM `viewRetention By Invoice` WHERE reference_name = sinv.name) AS retention_amount,
			0 as itbis_percibido,
			0 as retention_renta_terceros,
			0 as isr_percibido,
			0 as impuesto_selectivo_al_consumo,
			0 as otros_impuestos_y_tasas,
			0 as monto_propina_legal,
			(SELECT cash_payment from `view607 Payments` WHERE sinv_name = sinv.name) as cash_payment,
			(SELECT bank_payment from `view607 Payments` WHERE sinv_name = sinv.name) as bank_payment,
			(SELECT cc_payment from `view607 Payments` WHERE sinv_name = sinv.name) as cc_payment,
			(SELECT credit from `view607 Payments` WHERE sinv_name = 'sinv.name') as credit,
			0 bonos_regalo,
			0 permuta_de_pago,
			0 otros
		FROM `tabSales Invoice` AS sinv 
		JOIN tabCustomer AS cust on sinv.customer = cust.name 
		WHERE sinv.ncf NOT LIKE '%s' AND cust.tax_id > 0 AND sinv.docstatus = 1 AND sinv.posting_date 
		BETWEEN '%s' AND '%s' """ % ("SINV-%", from_date, to_date), as_dict=True)

	w = UnicodeWriter()
	w.writerow([
		'RNC/Cedula o Pasaporte',
		'Tipo de Identificacion',
		'Numero de Comprobante Fiscal',
		'Numero de Comprobante Fiscal modificado',
		'Tipo de Ingreso',
		'Fecha de Comprobante',
		'Fecha de Retencion',
		'Monto Facturado',
		'ITBIS Facturado',
		'ITBIS Retenido por Terceros',
		'ITBIS Percibido',
		'Retencion Renta por Terceros',
		'ISR Percibido',
		'Impuesto Selectivo al Consumo',
		'Otros Impuestos y Tasas',
		'Monto Propina Legal',
		'Efectivo',
		'Cheque/Transferencia/Deposito',
		'Tarjeta de Debito/Credito',
		'Venta Credito',
		'Bonos o Certificados de Regalo',
		'Permuta',
		'Otras Formas de Venta'
	])
		
	for row in result:
		w.writerow([
			row.tax_id.replace("-", ""),
			row.tipo_rnc,
			row.ncf,
			row.return_against_ncf,
			row.tipo_de_ingreso,
			row.posting_date.strftime("%Y%m%d"),
			row.payment_date.strftime("%Y%m%d") if row.payment_date  else "",
			row.base_total,
			row.base_total_taxes_and_charges,
			row.retention_amount,
			row.itbis_percibido,
			row.retention_renta_terceros,
			row.isr_percibido,
			row.impuesto_selectivo_al_consumo,
			row.otros_impuestos_y_tasas,
			row.monto_propina_legal,
			row.cash_payment or .00,
			row.bank_payment or .00,
			row.cc_payment or .00,
			row.credit or row.base_grand_total,
			row.bonos_regalo or .00,
			row.permuta_de_pago or .00,
			row.otros or .00
		])

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Reporte_607_" + str(int(time.time()))






 	




