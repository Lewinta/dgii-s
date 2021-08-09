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

def autoname(doc, event):
    doc.name = make_autoname(doc.naming_series)


def before_insert(doc, event):

    if doc.base_total >= MAX_VALUE_AVALIABLE:
        ct = frappe.get_doc('Customer',doc.customer)
        if not ct.tax_id:
            frappe.throw('Para realizar ventas por un monto igual o mayor a los RD$250,000. El cliente debe de tener un RNC o Cédula asociado.')
  
    if not doc.naming_series:
        return False

    if doc.amended_from:
        return False

    if doc.is_pos and doc.ncf:
        return False

    if doc.ncf:
       return False

    if doc.is_return:
       doc.return_against_ncf = doc.ncf
    
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
