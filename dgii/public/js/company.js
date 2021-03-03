frappe.ui.form.on("Company", {
	refresh(frm){
		frm.set_query("default_payable_account_usd", () => {
			return {
				filters: {
					"company": frm.doc.name,
					"account_type": "Payable",
					"account_currency": "USD",
				}
			}
		})
	}
});