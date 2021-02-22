frappe.ui.form.on("Supplier", {
	refresh(frm){
		frm.set_df_property('tipo_rnc', 'options', [
            { "value": "1", "label": "RNC" },
            { "value": "2", "label": "CEDULA" },
        ])
	},
	validate(frm){
		if(!frm.doc.tax_category)
			return
		if(frm.doc.tax_category == 'Consumidor Final')
			frappe.throw(`
				Me parece que la categoría de impuesto es incorrecta, un suplidor
				no puede tener asignado Consumidor Final. Favor verificar.
			`)
	}
})