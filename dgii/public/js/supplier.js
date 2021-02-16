frappe.ui.form.on("Supplier", {
	refresh(frm){
		frm.set_df_property('tipo_rnc', 'options', [
            { "value": "1", "label": "RNC" },
            { "value": "2", "label": "CEDULA" },
        ])
	}
})