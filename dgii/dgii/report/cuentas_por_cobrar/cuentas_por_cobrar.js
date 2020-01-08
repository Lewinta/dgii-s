// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Cuentas por cobrar"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
            "options": "Customer",
		},		
		{
			"fieldname":"from_date",
			"label": __("Desde"),
			"fieldtype": "Date"
		},
		{
            "fieldname":"to_date",
            "label": __("Hasta"),
            "fieldtype": "Date"
        }
	]

}
