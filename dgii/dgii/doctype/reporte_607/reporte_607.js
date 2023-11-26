frappe.ui.form.on("Reporte 607", {
	onload: function(frm) {
		frm.set_value("from_date", frappe.datetime.month_start());
		frm.set_value("to_date", frappe.datetime.month_end());
		frm.disable_save();
	},
	run_report: function(frm){
		var file_url = __("/api/method/dgii.dgii.doctype.reporte_607.reporte_607.get_file_address?from_date={0}&to_date={1}", 
			[frm.doc.from_date, frm.doc.to_date]);

		window.open(file_url);
	},

});

