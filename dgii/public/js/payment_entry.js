frappe.ui.form.on("Payment Entry", {
    validate (frm){
        $.map(frm.doc.references, ({doctype, name}) => {
            frm.script_manager.trigger("retention_type", doctype, name);
        })
    }
});

frappe.ui.form.on("Payment Entry Reference", { 
    reference_name (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.reference_doctype == "Sales Invoice") {
            frappe.db.get_value(row.reference_doctype, row.reference_name, "base_total_taxes_and_charges").then(({message}) => {
                let taxes = message.base_total_taxes_and_charges;
                frappe.model.set_value(cdt, cdn, "taxes_and_charges", taxes);
            });
        }
    },
    retention_type (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.run_serially([
            () => frm.script_manager.trigger("reference_name", cdt, cdn),
            () => frm.script_manager.trigger("calculate_retention", cdt, cdn),

        ]);
    },
    calculate_retention (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let tps = row.retention_type != "30%" ? 0.3 : 0;
        frappe.model.set_value(cdt, cdn, "retention_amount", row.taxes_and_charges * tps);
    }

})