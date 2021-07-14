# -*- coding: utf-8 -*-
# Copyright (c) 2019, TzCode, S. R. L. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dgii.hook.ncf import update_series_ncf

class DGIISettings(Document):
	def validate(self):
		for ncf in self.comprobantes_fiscales:
			update_series_ncf(ncf)
