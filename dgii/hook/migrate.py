import frappe 

def add_comprobantes_conf_constraints():
	doctype = "Comprobantes Conf"
	fields = ["tax_category", "company"]
	constraint_name = "one_comprobantes_conf_tax_category_company_constraint"

	def exists_constraint(constraint_name):
		result = frappe.db.sql("""
			Select
				CONSTRAINT_NAME 
			From
				INFORMATION_SCHEMA.TABLE_CONSTRAINTS
			Where
				CONSTRAINT_NAME = %s
		""", (constraint_name,))

		return True if result else False

	if exists_constraint(constraint_name):
		return "Contraint {} already exists" \
			.format(constraint_name)

	frappe.db.add_unique(doctype, fields, constraint_name)


def after_migrate():
    add_comprobantes_conf_constraints()
