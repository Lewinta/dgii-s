frappe.ui.form.on("Landed Cost Voucher", {
    refresh(frm) {
        frm.trigger("set_queries");
    },
    set_queries(frm){
        frm.set_query("expense_account", "taxes", (frm, cdt,cdn) => {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    "account_type": ["in", ["Expense Account", "Cost of Goods Sold"]],
                    "company": frm.company,
                    "account_currency": row.currency,
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

    },
    validate(frm) {
        $.map(frm.doc.taxes, ({doctype, name}) => { 
            let row = locals[doctype][name];
            if (!row.supplier_invoice)
                return
            let len = row.supplier_invoice.length;
            let valid_prefix = ["B01", "B11", "B13", "B14", "B15", "E31"];
            if (![11, 13].includes(len)) {
                frappe.msgprint(`
                    El numero de comprobante en la linea <b>${row.idx}</b> es incorrecto:\n
                    Tiene <b>${len}</b> caracteres, deben ser <b>11</b> o <b>13</b> para la serie E.
                `);
                validated = false;
                return
            }
            if (row.bill_no && !valid_prefix.includes(row.bill_no.substr(0, 3))) {
                frappe.msgprint(`
                    El Prefijo <b>${row.bill_no.substr(0, 3)}</b> del NCF ingresado en la linea <b>${row.idx}</b> no es valido
                `);
                validated = false;
                return
            }
        })
    }
});

frappe.ui.form.on("Landed Cost Taxes and Charges", {
	total(frm, cdt, cdn) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, cdt, cdn);
	},
    currency(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.currency == 'DOP')
            frappe.model.set_value(cdt, cdn, "exchange_rate", 1);
        
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, cdt, cdn);
    },
	purchase_taxes_and_charges_template(frm, cdt, cdn) {
		const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, cdt, cdn);
	},
    exchange_rate(frm, cdt, cdn) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, cdt, cdn);
	},
    tax_amount(frm, cdt, cdn) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, cdt, cdn);
    },
    supplier_invoice(frm, cdt, cdn) {
        frm.script_manager.trigger("validate_ncf", cdt, cdn);
    },
    calculate_total_amounts(frm, cdt, cdn) {
        const events = [
            "calculate_tax_amount",
            "calculate_amount",
        ];

        events.map(event => {
            frm.script_manager.trigger(event, cdt, cdn);
        });
    },
	calculate_tax_amount(frm, cdt, cdn) {
		let {
            tax_amount, total, purchase_taxes_and_charges_template,
            currency, exchange_rate
        } = frappe.get_doc(cdt, cdn);
        if (!!tax_amount)
            return;
        const method = "dgii.hook.landed_cost_voucher.get_rate_from_template";
        const args = { "template": purchase_taxes_and_charges_template };
        if (currency != 'DOP')
            total = flt(total) * flt(exchange_rate)

        if (total && purchase_taxes_and_charges_template)
            frappe.call(method, args).then(({message}) => {
                const tax_amount = total * (flt(message) / 100);
                const amount = total * (1 + flt(message) / 100);
                frappe.model.set_value(cdt, cdn, "tax_amount", tax_amount);
            })
        // else {
        //     frappe.model.set_value(cdt, cdn, "tax_amount", 0);
        // }
    },
    calculate_amount(frm, cdt, cdn) {
        // base amount
        const { model } = frappe;

        const doc = frappe.get_doc(cdt, cdn);
        const amount = flt(doc.total) + flt(doc.tax_amount);
        const base_amount = (flt(doc.total) + flt(doc.tax_amount)) * flt(doc.exchange_rate);

        model.set_value(cdt, cdn, "amount", amount);
        model.set_value(cdt, cdn, "base_amount", base_amount);
    }
});

frappe.ui.form.on("Landed Cost Item", {
    item_code: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn, "weight", flt(row.qty) * flt(row.weight_per_unit))
    }
});