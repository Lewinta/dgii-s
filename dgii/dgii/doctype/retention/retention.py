# Copyright (c) 2023, Soldeva, SRL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Retention(Document):
    def on_update(self):
        self.clear_retention_category_if_applies()

    def clear_retention_category_if_applies(self):
        if self.retention_type != "ISR":
            self.db_set("retention_category", "")
