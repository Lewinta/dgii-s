frappe.ui.form.on("Purchase Invoice", {
	
	validate: frm => {
		frm.trigger("bill_no");
	},
	bill_no: frm => {
		let {bill_no} = frm.doc;

		if (!bill_no)
			return

		if (bill_no.length != 11){
			frappe.msgprint("El numero de comprobante debe contener 11 " +
				"digitos, favor verificar."
			)
			frappe.validated = false;
		}
		
		frm.set_value("bill_no", bill_no.trim().toUpperCase())
	}
});