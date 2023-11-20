frappe.ui.form.on("Purchase Invoice", {
	
	validate(frm){
		frm.trigger("bill_no");
		frm.trigger("validate_cost_center");
	},
	bill_no(frm){
		let {bill_no} = frm.doc;

		frm.set_df_property("vencimiento_ncf", "reqd", !!bill_no);
		
		if (!bill_no)
			return
		
		frm.set_value("bill_no", bill_no.trim().toUpperCase())
		frm.trigger("validate_ncf")
	},
	validate_ncf(frm){
		let len = frm.doc.bill_no.length;
		let valid_prefix = ["B01", "B04", "B11", "B13", "B14", "B15", "E31", "E34"];
		if (![11, 13].includes(len)) {
			frappe.msgprint(`El numero de comprobante tiene <b>${len}</b> caracteres, deben ser <b>11</b> o <b>13</b> para la serie E.`);
			validated = false;
			return
		}
		if (frm.doc.bill_no && !valid_prefix.includes(frm.doc.bill_no.substr(0, 3))) {
			frappe.msgprint(`El Prefijo <b>${frm.doc.bill_no.substr(0, 3)}</b> del NCF ingresado no es valido`);
			validated = false;
			return
		}
	},
	validate_rnc(frm){
		let len = frm.doc.tax_id.length;

		if (![9, 11].includes(len)) {
			frappe.msgprint(`El RNC/Cedula ingresados tiene <b>${len}</b> caracteres favor verificar, deben ser 9 u 11.`);
			validated = false;
			return
		}
	},
	validate_cost_center(frm){
		if(!frm.doc.cost_center)
			return
		$.map(frm.doc.taxes, tax => {
			if (!tax.cost_center)
				tax.cost_center = frm.doc.cost_center;
		})
		$.map(frm.doc.items, tax => {
			if (!tax.cost_center)
				tax.cost_center = frm.doc.cost_center;
		})

	},
	tax_id(frm){
		if (!frm.doc.tax_id)
			return
		frm.set_value("tax_id", replace_all(frm.doc.tax_id.trim(), "-", ""));
		frm.trigger("validate_rnc");
	},
	include_isr(frm){
		frm.trigger("calculate_isr");
		$.map(["retention_rate", "retention_type"], field => {
			frm.set_df_property(field, 'reqd', frm.doc.include_isr);
		})
	},
	isr_rate(frm){
		frm.trigger("calculate_isr");
	},
	include_retention(frm){
		frm.set_df_property("retention_rate", 'reqd', frm.doc.include_retention);

		frm.trigger("calculate_retention");
	},
	retention_rate(frm){
		frm.trigger("calculate_retention");
	},
	calculate_retention(frm){
		if (!frm.doc.include_retention || !frm.doc.total_taxes_and_charges || !frm.doc.retention_rate)
			frm.set_value("retention_amount", 0);
		let retention_rate = 0;
		let amount = 0;
		if (frm.doc.retention_rate == '30%'){
			// Vamos a sumar todos los productos con el campo item_type = "Servicio"
			let monto_facturado_servicios = 0;
			frappe.run_serially([
				() => $.map(frm.doc.items, item => amount += item.item_type == "Servicios" ? item.amount: 0),
				() => frm.set_value("monto_facturado_servicios", monto_facturado_servicios),
				() => retention_rate = 0.30,
				() => frm.set_value("retention_amount", amount * retention_rate * 0.18),
				() => frm.set_value("base_retention_amount", amount * frm.doc.conversion_rate * retention_rate * 0.18)
			])		
		}
		if (frm.doc.retention_rate == '100%'){
			// Se retiene el 100% de los impuestos
			frm.set_value("retention_amount", frm.doc.total_taxes_and_charges);
			frm.set_value("base_retention_amount", frm.doc.total_taxes_and_charges * frm.doc.conversion_rate)
		}
	},
	calculate_isr(frm){
		if (!frm.doc.include_isr || !frm.doc.total || !frm.doc.isr_rate)
			frm.set_value("isr_amount", 0);
		let amount = frm.doc.total * (frm.doc.isr_rate/ 100);
		frm.set_value("isr_amount", amount);
		frm.set_value("base_isr_amount", amount * frm.doc.conversion_rate);
	}
});

