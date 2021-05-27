# -*- coding: utf-8 -*-
# Copyright (c) 2019, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import db as database
from frappe.utils.background_jobs import enqueue_doc

class ComprobantesConf(Document):
	def on_change(self):
		pass
		# self.method = "update_naming_series"
		# enqueue_doc(self.doctype, self.name, self.method, timeout=1000)

	def on_trash(self):
		pass
		# self.method = "update_naming_series"
		# enqueue_doc(self.doctype, self.name, self.method, timeout=1000)

	def update_naming_series(self):
		setter = frappe.new_doc("Property Setter")

		filters = {			
			'doc_type': "Sales Invoice",
			'field_name': 'naming_series',
			'doctype_or_field': 'DocField',
			'property': "options",
			'property_type': "Select"
		}

		if database.exists("Property Setter", filters):
			setter = frappe.get_doc("Property Setter", filters)

		series = [""] 

		series += self.get_series()
			
		setter.update({
			'doc_type': "Sales Invoice",
			'field_name': 'naming_series',
			'doctype_or_field': 'DocField',
			'property': "options",
			'property_type': "Select",
			'value': "\n".join(series)
		})

		setter.save()

		database.commit()

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