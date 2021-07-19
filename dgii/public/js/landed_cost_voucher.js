frappe.ui.form.on("Landed Cost Voucher", {
    refresh(frm) {
        frm.trigger("set_queries");
    },
    set_queries(frm){
        frm.set_query("expense_account", "taxes", () => {
            return {
                filters: {
                    "account_type": "Expense Account",
                    "company": frm.doc.company,
                }
            }
        })
        frm.set_query("cost_center", "taxes", () => {
            return {
                filters: {
                    "is_group": 0,
                    "company": frm.doc.company,
                }
            }
        })

    }
});

frappe.ui.form.on("Landed Cost Taxes and Charges", {
	total(frm, cdt, cdn) {
		frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
	},
    currency(frm, cdt, cdn) {
        frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
    },
	purchase_taxes_and_charges_template(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "tax_amount", 0.00);
        frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
	},
    exchange_rate(frm, cdt, cdn) {
        frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
    },
    tax_amount(frm, cdt, cdn) {
        frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
    },
    supplier_invoice(frm, cdt, cdn) {
        frm.script_manager.trigger("validate_ncf", cdt, cdn);
    },
	calculate_tax_amount(frm, cdt, cdn) {
		let {
            tax, total, purchase_taxes_and_charges_template,
            currency, exchange_rate, tax_amount
        } = frappe.get_doc(cdt, cdn);
        const method = "dgii.hook.landed_cost_voucher.get_rate_from_template";
        const args = { "template": purchase_taxes_and_charges_template };
        if (currency != 'DOP')
            total = flt(total) * flt(exchange_rate)

        if (total && purchase_taxes_and_charges_template)
            frappe.call(method, args).then(({message}) => {
                const tax = !!tax_amount && tax_amount > 0 ? tax_amount : flt(total * (flt(message) / 100)) ;
                const amount = total + tax ;
                
                frappe.model.set_value(cdt, cdn, "tax_amount", tax);
                frappe.model.set_value(cdt, cdn, "amount", amount);
            })
        else
            frappe.model.set_value(cdt, cdn, "amount", total);

	},
    validate_ncf(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let len = row.supplier_invoice.length;
        let valid_prefix = ["B01", "B11", "B13", "B14", "B15", "E31"];
        if (![11, 13].includes(len)) {
            frappe.msgprint(`El numero de comprobante tiene <b>${len}</b> caracteres, deben ser <b>11</b> o <b>13</b> para la serie E.`);
            validated = false;
            return
        }
        if (row.bill_no && !valid_prefix.includes(row.bill_no.substr(0, 3))) {
            frappe.msgprint(`El Prefijo <b>${row.bill_no.substr(0, 3)}</b> del NCF ingresado no es valido`);
            validated = false;
            return
        }
    },
});

frappe.ui.form.on("Landed Cost Item", {
    item_code: (frm, cdt, cdn) => {
        frappe.throw("Ran")
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn, "weight", flt(row.qty) * flt(row.weight_per_unit))
    }
});