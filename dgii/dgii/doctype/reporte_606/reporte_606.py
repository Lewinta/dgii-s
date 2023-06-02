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


class ReferenceNotFound(Exception):
    pass


class Reporte606(Document):
    pass


@frappe.whitelist()
def get_file_address(from_date, to_date):
    result = frappe.db.sql(f"""
		SELECT 
			pinv.name,
			pinv.tax_id,
			supl.tipo_rnc,
			pinv.tipo_bienes_y_servicios_comprados,
			pinv.bill_no,
			pinv.bill_date,
			pinv.excise_tax,
			pinv.base_taxes_and_charges_added,
			pinv.retention_amount,
			pinv.isr_amount,
			pinv.retention_type,
			pinv.total_itbis,
			pinv.total_taxes_and_charges,
			pinv.other_taxes,
			pinv.legal_tip,
			pinv.base_total,
			pinv.monto_facturado_servicios,
			pinv.monto_facturado_bienes,
			pinv.mop
		FROM 
			`tabPurchase Invoice` AS pinv
	    INNER JOIN 
			`tabSupplier` AS supl
		ON 
			supl.name = pinv.supplier
        LEFT JOIN
            `tabPayment Entry Reference` AS per
        ON
            per.reference_name = pinv.name
        LEFT JOIN
            `tabPayment Entry` AS pe
        ON
            pe.name = per.parent
		WHERE
			pinv.docstatus = 1 
            AND pinv.bill_date BETWEEN {from_date!r} AND {to_date!r}
            OR pe.posting_date BETWEEN {from_date!r} AND {to_date!r}
	""", as_dict=True, debug=True)

    w = UnicodeWriter()
    w.writerow([
        'RNC o Cedula',                                                   # 01
        'Tipo Id',                                                        # 02
        'Tipo Bienes y Servicios Comprados',                              # 03
        'NCF',                                                            # 04
        'NCF o Documento Modificado',                                     # 05
        'Fecha Comprobante',                                              # 06
        '',                                                               # 07
        'Fecha Pago',                                                     # 08
        '',                                                               # 09
        'Monto Facturado en Servicios',                                   # 10
        'Monto Facturado en Bienes',                                      # 11
        'Total Monto Facturado',                                          # 12
        'ITBIS Facturado',                                                # 13
        'ITBIS Retenido',                                                 # 14
        # 15
        'ITBIS sujeto a Proporcionalidad (Art. 349)',
        'ITBIS llevado al Costo',                                         # 16
        'ITBIS por Adelantar',                                            # 17
        'ITBIS percibido en compras',                                     # 18
        'Tipo de Retencion en ISR',                                       # 19
        'Monto Retencion Renta',                                          # 20
        'ISR Percibido en compras',                                       # 21
        'Impuesto Selectivo al Consumo',                                  # 22
        'Otros Impuesto/Tasas',                                           # 23
        'Monto Propina Legal',                                            # 24
        'Forma de Pago',                                                  # 25
    ])

    for row in result:
        bill_no = ''
        if row.bill_no:
            bill_no = row.bill_no.split(
                "-")[1] if (len(row.bill_no.split("-")) > 1) else row.bill_no  # NCF-A1##% || A1##%
        w.writerow([
            row.tax_id.replace("-", "") if row.tax_id else "", 	# RNC
            row.tipo_rnc, 	# Tipo de RNC
            row.tipo_bienes_y_servicios_comprados,
            bill_no,		# NCF
            '',				# NCF modificado
            row.bill_date.strftime("%Y%m"),  # FC AAAAMM
            row.bill_date.strftime("%d"),  # FP DD
            get_retention_date(row),  # FP AAAAMM
            row.bill_date.strftime("%d"),  # FP DD
            row.monto_facturado_servicios,  # Monto Facturado en Servicios
            row.monto_facturado_bienes,		# Monto Facturado en Bienes
            row.base_total,					# Monto Facturado
            # row.total_taxes_and_charges,	# ITBIS Facturado Cecilia lo pidio actualizar on 25 feb 21
            row.total_itbis,				# ITBIS Facturado
            get_retention_amount(row, typeof="ITBIS"),  	# ITBIS Retenido
            '0',  							# ITBIS sujeto a Proporcionalidad (Art. 349)
            '0',  							# ITBIS por Adelantar
            row.total_itbis or 0, 			# ITBIS llevado al Costo
            '0',  							# ITBIS percibido en compras
            # row.retention_type.split("-")[0] if row.retention_type else '',  							# Tipo de Retención en ISR
            get_retention_type(row),				# Tipo de Retención en ISR
            # Monto Retención Renta
            get_retention_amount(row, typeof="ISR"),
            '0',  							# ISR Percibido en compras
            row.excise_tax or 0,  			# Impuesto Selectivo al Consumo
            row.other_taxes or 0,  			# Otros Impuesto/Tasas
            row.legal_tip,  				# Monto Propina Legal
            row.mop, 						# Forma de Pago
        ])

    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Reporte_606_" + str(int(time.time()))


def get_retention_date(row):
    try:
        reference_row = get_reference_row(row)
    except ReferenceNotFound:
        return 0
    else:
        posting_date = frappe.get_value(
            "Payment Entry", reference_row.parent, "posting_date")
        return frappe.utils.getdate(posting_date).strftime("%Y%m")


def get_retention_amount(row, typeof):
    if typeof not in ["ITBIS", "ISR"]:
        return 0

    try:
        reference_row = get_reference_row(row, typeof)
    except ReferenceNotFound:
        return 0
    else:
        return reference_row.retention_amount


def get_retention_type(row):
    # will return the retention_category of the retention selected in the Payment Entry
    # if set, else will return empty string
    try:
        reference_row = get_reference_row(row, typeof="ISR")
    except ReferenceNotFound:
        return ""
    else:
        return reference_row.retention_category


def get_reference_row(row, typeof=None):
    # will return the row of the Payment Entry that has the same reference as the Purchase Invoice
    # if set, else will return empty string
    doctype = "Payment Entry Reference"
    filters = {
        "reference_doctype": "Purchase Invoice",
        "reference_name": row.name,
        # "doctatus": "1",
    }

    if typeof is not None:
        filters["retention_type"] = typeof

    if frappe.db.exists(doctype, filters):
        return frappe.get_doc(doctype, filters)

    raise ReferenceNotFound()
