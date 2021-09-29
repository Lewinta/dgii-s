frappe.ui.form.on("Reporte 606", {
	onload: function(frm) {
		frm.set_value("from_date", frappe.datetime.month_start());
		frm.set_value("to_date", frappe.datetime.month_end());
		frm.disable_save();
		frm.set_query("cost_center", () => {
			return {
				"filters": {
					"is_group": 0
				}
			}
		})
	},
	run_report: function(frm){
		var file_url = __("/api/method/dgii.dgii.doctype.reporte_606.reporte_606.get_file_address?from_date={0}&to_date={1}&cost_center={2}",
			[frm.doc.from_date, frm.doc.to_date, frm.doc.cost_center]);

		window.open(file_url);
	}
});

