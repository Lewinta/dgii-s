frappe.ui.form.on("Landed Cost Voucher", {
    refresh(frm) {
        frm.trigger("set_queries");
    },
    set_queries(frm) {
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
    currency(frm, doctype, name) {
        const doc = frappe.get_doc(doctype, name);

        if (!doc.currency) {
            return "Clear Exchange rate when currency is set";
        }

        const fieldname = "exchange_rate";
        const value = 1.000;

        frappe.model.set_value(doctype, name, fieldname, value);
    },
    tax_amount(frm, doctype, name) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, doctype, name);
    },
    exchange_rate(frm, doctype, name) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, doctype, name);
    },
    non_base_sub_total(frm, doctype, name) {
        const event = "calculate_total_amounts";
        frm.script_manager.trigger(event, doctype, name);
    },
    purchase_taxes_and_charges_template(frm, doctype, name) {
        const { model } = frappe;

        const doc = frappe.get_doc(doctype, name);

        if (doc.purchase_taxes_and_charges_template) {
            return "Purchase Taxes and Charges is Required";
        }

        const method = "dgii.hook.landed_cost_voucher.get_rate_from_template";
        const args = {
            "template": doc.purchase_taxes_and_charges_template,
        };

        const callback = response => {
            const { message } = response;

            if (message) {
                const fieldname = "tax_amount";
                const value = flt(message);

                model.set_value(doctype, name, fieldname, value);
            }
        };

        frappe.call({ method, args, callback });
    },
    calculate_total_amounts(frm, doctype, name) {
        const events = [
            "calculate_base_tax_amount",
            "calculate_amount",
            "calculate_total",
        ];

        events.map(event => {
            frm.script_manager.trigger(event, doctype, name);
        });
    },
    calculate_base_tax_amount(frm, doctype, name) {
        const { model } = frappe;

        const doc = frappe.get_doc(doctype, name);

        const base_tax_amount = flt(doc.tax_amount) * flt(doc.exchange_rate);
        model.set_value(doctype, name, "base_tax_amount", base_tax_amount);
    },
    calculate_amount(frm, doctype, name) {
        // base amount
        const { model } = frappe;

        const doc = frappe.get_doc(doctype, name);
        const base_amount = flt(doc.non_base_sub_total) * flt(doc.exchange_rate);
        model.set_value(doctype, name, "amount", base_amount);
    },
    calculate_total(frm, doctype, name) {
        const { model } = frappe;

        const doc = frappe.get_doc(doctype, name);

        // base_amount + base_tax_amount
        const base_total = flt(doc.amount) + flt(doc.base_tax_amount);
        model.set_value(doctype, name, "total", base_total);
    },

    //
    supplier_invoice(frm, cdt, cdn) {
        frm.script_manager.trigger("validate_ncf", cdt, cdn);
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
        frappe.model.set_value(cdt, cdn, "weight", flt(row.qty) * flt(row.weight_per_unit))
    }
});