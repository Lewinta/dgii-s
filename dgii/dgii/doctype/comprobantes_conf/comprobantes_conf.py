# -*- coding: utf-8 -*-
# Copyright (c) 2019, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import db as database
from frappe.utils.background_jobs import enqueue_doc

class ComprobantesConf(Document):
	def get_series(self):
		return database.sql_list("""
			Select Distinct
				conf.serie
			FROM 
				`tabComprobantes Conf` As conf
			WHERE enabled = 1
			""")

def on_doctype_update():
	database.add_unique("Comprobantes Conf", 
		["company", "serie"], "unique_serie_for_company")