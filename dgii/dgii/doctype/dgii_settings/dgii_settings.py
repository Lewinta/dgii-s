# -*- coding: utf-8 -*-
# Copyright (c) 2019, Soldeva, SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dgii.hook.ncf import update_series_ncf

class DGIISettings(Document):
	pass