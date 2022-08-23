// Copyright (c) 2020, Yefri Tavarez and contributors
// For license information, please see license.txt

frappe.ui.form.on('Comprobantes Conf', {
	refresh: function (frm) {
		frm.set_df_property('document_type', 'options', [
			{"value": 1, "label": "Factura de Crédito Fiscal"},
			{"value": 2, "label": "Factura de Consumo"},
			{"value": 3, "label": "Notas de Débito"},
			{"value": 4, "label": "Notas de Crédito"},
			{"value": 11, "label": "Comprobante de Compras"},
			{"value": 12, "label": "Registro Único de Ingresos"},
			{"value": 13, "label": "Comprobante para Gastos Menores"},
			{"value": 14, "label": "Comprobante de Regímenes Especiales"},
			{"value": 15, "label": "Comprobante Gubernamental"},
			{"value": 16, "label": "Comprobante para exportaciones"},
			{"value": 17, "label": "Comprobante para Pagos al Exterior"},
		]);
	},
});
