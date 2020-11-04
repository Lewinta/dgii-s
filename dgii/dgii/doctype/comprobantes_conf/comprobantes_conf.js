// Copyright (c) 2020, Yefri Tavarez and contributors
// For license information, please see license.txt

frappe.ui.form.on('Comprobantes Conf', {
	refresh: function (frm) {
		jQuery.map([
			"update_document_type_field"
		], frm.events.update_document_type_field.bind(frm));
	},
	update_document_type_field: function (frm) {
		const options = this.events.get_options(this);
		this.set_df_property("document_type", "options", options);
	},
	get_options: function (frm) {
		return jQuery.map({
			"Consumidor Final": 0,
			"Derecho a Credito Fiscal": 1,
			"Nota de Credito Final": 2,
			"Nota de Credito Fiscal": 3,
			"Consumidor Final sin ITBIS": 4,
			"Derecho a Credito Fiscal sin ITBIS": 5,
			"Nota de Credito Final sin ITBIS": 6,
			"Nota de Credito Fiscal  sin ITBIS": 7,
		}, frm.events.get_option.bind(frm));
	},
	get_option: function (value, label) {
		return {
			label,
			value,
		};
	},
});
