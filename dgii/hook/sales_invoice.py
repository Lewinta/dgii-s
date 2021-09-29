# -*- coding: utf-8 -*-
# Copyright (c) 2019, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import json
from frappe.utils import cstr, cint, flt, now_datetime
from frappe.model.naming import make_autoname

from frappe import _ as translate

MAX_VALUE_AVALIABLE = 250000
TEMPORAL_USER_PREFIX_ALLOWED = ["dylan.nunez@logomarca.com.do","maryolin.ovalle@logomarca.com.do", "ernestonunez@tzcode.tech"]
PREFIX = "ACC-TSINV-.YYYY.-"

def autoname(doc, event):
    if frappe.session.user in TEMPORAL_USER_PREFIX_ALLOWED:
        reference = make_autoname(PREFIX)
        doc.name = reference.replace("TSINV", "SINV")
    else:
        doc.name = make_autoname(doc.naming_series)

def validate(doc, event):
    get_return_against_ncf(doc)
    
def before_insert(doc, event):
    generate = frappe.db.get_single_value("DGII Settings", "generate_ncf_on_submit")
    if not generate:
        generate_ncf(doc)

def before_submit(doc, event):
    generate = frappe.db.get_single_value("DGII Settings", "generate_ncf_on_submit")
    if doc.base_total >= MAX_VALUE_AVALIABLE:
        ct = frappe.get_doc('Customer',doc.customer)
        if not ct.tax_id:
            frappe.throw('Para realizar ventas por un monto igual o mayor a los RD$250,000. El cliente debe de tener un RNC o Cédula asociado.')
    if generate:
        generate_ncf(doc)

def generate_ncf(doc):
    if not doc.naming_series:
        return False

    # if doc.amended_from:
    #     return False

    if doc.is_pos and doc.ncf:
        return False

    if doc.ncf:
       return False

    if doc.is_return and doc.return_against:
       doc.ncf = ''
       doc.return_against_ncf = frappe.get_value(doc.doctype, doc.return_against, "ncf")
    
    doc.ncf = generate_new(doc)

    get_document_type(doc)

    return True

def on_change(doc, event):
    fetch_print_heading_if_missing(doc)

def get_document_type(doc):
    conf = get_serie_for_(doc)
    doc.document_type = conf.document_type

def generate_new(doc):
    conf = get_serie_for_(doc)
    
    if not conf.serie:
        return ''
    current = cint(conf.current)

    if cint(conf.top) and current >= cint(conf.top):
        frappe.throw(
            "Ha llegado al máximo establecido para esta serie de comprobantes!")

    current += 1

    conf.current = current
    conf.db_update()

    return '{0}{1:08d}'.format(conf.serie.split(".")[0], current)


def get_serie_for_(doc):
    if not doc.tax_category:
        frappe.throw("Favor seleccionar en el cliente alguna categoria de impuestos")
    
    if doc.is_return:
        return frappe.get_doc("Comprobantes Conf", {
            "company": doc.company,
            "document_type": 4
        })
    else:
        return frappe.get_doc("Comprobantes Conf", {
            "company": doc.company,
            "tax_category": doc.tax_category
        })

def fetch_print_heading_if_missing(doc, go_silently=False):
    if doc.select_print_heading:
        return False

    try:
        conf = get_serie_for_(doc)
    except:
        return False

    if not conf.select_print_heading:
        infomsg = \
            translate(
                "Print Heading was not specified on {doctype}: {name}")

        if not go_silently:
            frappe.msgprint(infomsg
                            .format(**conf.as_dict()))

        return False

    doc.select_print_heading = conf.select_print_heading

    doc.db_update()

def get_return_against_ncf(doc):
    if(doc.is_return == 1):
        doc.ncf = ''
        ncf = frappe.get_value("Sales Invoice", doc.return_against, "ncf")
        doc.return_against_ncf = ncf