frappe.ui.form.on("Customer", {
	refresh: frm => {
		console.log("loaded");
		frm.set_df_property('tipo_rnc', 'options', [{
        		"value": "1",
        		"label": "RNC"
        	},
        	{
        		"value": "2",
        		"label": "CEDULA"
        	},
        	{
        		"value": "3",
        		"label": "PASAPORTE"
        	},
        ]);
	}
})