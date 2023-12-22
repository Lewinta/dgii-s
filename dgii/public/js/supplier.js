frappe.ui.form.on("Supplier", {
	refresh(frm) {
		const events = [
			"add_custom_buttons",
			"set_properties",
		]
		$.map(events, (event) => {
			frm.trigger(event);
		});
	},
	validate(frm){
		if(!frm.doc.tax_category)
			return
		if(frm.doc.tax_category == 'Consumidor Final')
			frappe.throw(`
				Me parece que la categoría de impuesto es incorrecta, un suplidor
				no puede tener asignado Consumidor Final. Favor verificar.
			`)
	},
	set_properties(frm){
		frm.set_df_property('tipo_rnc', 'options', [
            { "value": "1", "label": "RNC" },
            { "value": "2", "label": "CEDULA" },
        ])
	},
	add_custom_buttons(frm) {
		frm.trigger("add_consult_rnc_button");
	},
	add_consult_rnc_button(frm) {
		if (!frm.is_new())
			return;
		frm.add_custom_button(__('Consultar RNC'), () => {
			frm.trigger("get_rnc_details");
		}).addClass("btn-primary");
	},
	get_rnc_details(frm) {
		const method = "dgii.api.get_rnc_details"
		const fields = [
			{
				"fieldname": "tax_id",
				"label": __("RNC/Cedula"),
				"fieldtype": "Data",
				"reqd": 1,
				onchange: () => {
					// Let's replace the "-" and " " characters if any
					const { tax_id } = d.get_values();
					if (tax_id.match(/-| /)) {
						// Let's replace them
						d.set_value("tax_id", tax_id.replace(/-| /g, ""));
					}
					

				}
			},
			{
				"fieldname": "status",
				"label": __("Status"),
				"fieldtype": "Read Only",
				"read_only": 1,
			},
			{ 
				"fieldtype": "Button", 
				"label": "Consultar",
				onchange: () => {
					console.log("Consultar");
				}
			},
			{ "fieldtype": "Column Break" },
			{
				"fieldname": "brand_name",
				"label": __("Razon Social"),
				"fieldtype": "Read Only",
				"read_only": 1,
			},
			{
				"fieldname": "company_name",
				"label": __("Nombre Comercial"),
				"fieldtype": "Read Only",
				"read_only": 1,
			},
		]

		const primary_action_label = __("Consultar RNC")
		const action = __("Guardar")
		const primary_action = (values) => {
			const { tax_id, brand_name, company_name } = values;
			frm.set_value("tax_id", tax_id);
			frm.set_value("commercial_name", brand_name);
			frm.set_value("supplier_name", company_name);
		}
		let d = frappe.prompt(fields, primary_action, primary_action_label, action);
		d.show();
		d.$wrapper.find('.btn-primary').hide();
		d.$wrapper.find('.btn-default').addClass('btn-primary');
		d.$wrapper.find('.btn-default').on('click', () => {
			const { tax_id } = d.get_values();
			frappe.call({
				method: method,
				args: {tax_id},
				callback: function (r) {
					if (r.message) {
						// d.set_value("tax_id", r.message.tax_id);
						d.set_value("status", r.message.status);
						d.set_value("brand_name", r.message.brand_name);
						d.set_value("company_name", r.message.company_name);

						if (r.message.status === "ACTIVO") {
							d.$wrapper.find('.btn-default').removeClass('btn-primary');
							d.$wrapper.find('.btn-primary').show();
						}
					}
				},
				freeze: true,
				freeze_message: __("Consultando RNC...")
			})
		});
	}
})