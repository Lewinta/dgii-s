frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		frappe.run_serially([
			_ => frm.trigger("set_queries"),
		]);
	},
	set_queries(frm) {
		frappe.run_serially([
			_ => frm.trigger("set_retention_query"),
		]);
	},
	set_retention_query(frm) {
		const { doc } = frm;

		const fieldname = "retention";
		const parentfield = "references";

		const get_query = function () {
			const supported_types = new Set([
				"Pay",
				"Receive",
			]);

			if (!supported_types.has(doc.payment_type)) {
				frappe.throw(`Payment Type '${doc.payment_type}' is not supported`);
			}

			const filters = {
				"applicable_for": doc.payment_type,
			};

			return { filters };
		};

		frm.set_query(fieldname, parentfield, get_query);
	},
});

frappe.ui.form.on("Payment Entry Reference", {
	retention(frm, doctype, name) {
		const { deductions, references } = frm.doc;

		const doc = frappe.get_doc(doctype, name);

		if (!doc.retention) {
			return "Skip for empty retention";
		}

		// if (doc.reference_doctype == "Sales Invoice") {
		frm.call("get_retention_details", {
			reference_doctype: doc.reference_doctype,
			reference_name: doc.reference_name,
			retention_id: doc.retention,
		}).then(({ message }) => {
			// account: "1511 - ITBIS Retenido Norma 02-05 - TZ"
			// amount: 16.2
			// cost_center: "Principal - TZ"
			// retention_category: null
			// retention_description: "Ret. 30% ITBIS Terceros-Sociedades"
			// retention_rate: 30
			// retention_type: "ITBIS"

			const {
				account,
				amount,
				cost_center,
				retention_category,
				retention_description,
				retention_rate,
				retention_type,
			} = message;

			frappe.model.set_value(doctype, name, "retention_amount", amount);

			const existing_deduction = deductions
				.find(deduction => deduction.account === account);

			// frappe.confirm(
			// 	"We noticed that you already have a deduction with the same account. Do you want to replace it?",
			// 	() => {
			// 		// todo
			// 	},
			// 	() => {
			// 		// todo
			// 	}
			// )
			if (existing_deduction) {
				// check to see if the is another row with the same retention_type
			}

			// doctype: Payment Entry Deduction
			frm.add_child("deductions", {
				"account": account,
				"cost_center": cost_center,
				"amount": amount,
				"description": retention_description,
			});

			frm.refresh_field("deductions");
		});
	},
});