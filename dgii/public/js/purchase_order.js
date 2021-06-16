frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        frm.trigger("set_queries");
    },
    set_queries(frm) {
        frm.set_query("cost_center", () => {
            return {
                filters: {
                    is_group: 0
                }
            }
        })
    },
    calculate_total_weight: frm => {
        let total_weight = 0.0;
        $.map(frm.doc.items, item => {
            total_weight += item.total_weight
        });
        frm.set_value("total_net_weight", total_weight);
    }
});

frappe.ui.form.on("Purchase Order Item", {
    weight_per_unit: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        frappe.model.set_value(
            cdt,
            cdn,
            "total_weight",
            flt(row.qty) * flt(row.weight_per_unit)
        )
        frm.trigger("calculate_total_weight");
    }
});