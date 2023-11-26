# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import os
import json

import frappe


def execute():
    create_retention_doctype()
    create_custom_fields()


def create_retention_doctype():
    filepath = get_absolute_path("retention.json")
    with open(filepath) as archive:
        doc = json.load(archive)

    if frappe.db.exists("DocType", doc.get("name")):
        return

    doc = frappe.get_doc(doc)
    doc.insert()


def create_custom_fields():
    """Create required custom fields for Retention to work"""
    filepath = get_absolute_path("retention_fields.json")
    with open(filepath) as archive:
        docfields = json.load(archive)

    for df in docfields:
        create_custom_field(df)


def create_custom_field(df):
    doc = get_custom_field(df)

    doc.update(df)

    doc.save()


def get_custom_field(df):
    doctype = df.get("doctype")
    name = df.get("name")

    if frappe.db.exists(doctype, name):
        return frappe.get_doc(doctype, name)

    return frappe.new_doc(doctype)


def get_absolute_path(filename):
    """Return the absolute path of the current python file"""

    self = "introduce_retention.py"

    return os.path.abspath(__file__) \
        .replace(self, filename)
