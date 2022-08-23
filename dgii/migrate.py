import frappe

def after_migrate():
    pass
    # create_views()


def create_views():
    frappe.db.sql("""
    CREATE OR REPLACE VIEW `viewRetention By Invoice` as
        select
            `tabPayment Entry Reference`.reference_doctype,
            `tabPayment Entry Reference`.reference_name,
            `tabPayment Entry Reference`.retention_amount,
            `tabPayment Entry`.posting_date
        from 
            `tabPayment Entry`
        join
            `tabPayment Entry Reference`
        on
            `tabPayment Entry`.name = `tabPayment Entry Reference`.parent
        and	
            `tabPayment Entry`.docstatus = 1
        and
            `tabPayment Entry Reference`.retention_amount > 0
        and
            `tabPayment Entry Reference`.reference_doctype = 'Sales Invoice'
    """)
    
    frappe.db.sql("""
    CREATE OR REPLACE VIEW `view607 Payments` as
       SELECT 
        `tabSales Invoice`.`name` as `sinv_name`,
        SUM(
            IF(
                `tabSales Invoice`.`posting_date` = `tabPayment Entry`.`posting_date` AND
                `tabMode of Payment`.`type` = 'Cash' AND
                `tabSales Invoice`.`outstanding_amount` = 0,
                `tabPayment Entry Reference`.`allocated_amount`,
                0
            )
        ) `cash_payment`,
        SUM(
            IF(
                `tabSales Invoice`.`posting_date` = `tabPayment Entry`.`posting_date` AND
                `tabMode of Payment`.`type` = 'Bank' AND
                `tabSales Invoice`.`outstanding_amount` = 0,
                `tabPayment Entry Reference`.`allocated_amount`,
                0
            )
        ) `bank_payment`,
        SUM(
            IF(
                `tabSales Invoice`.`posting_date` = `tabPayment Entry`.`posting_date` AND
                `tabMode of Payment`.`type` = 'Credit Card' AND
                `tabSales Invoice`.`outstanding_amount` = 0,
                `tabPayment Entry Reference`.`allocated_amount`,
                0
            )
        ) `cc_payment`,
        IF(
                `tabSales Invoice`.`posting_date` != `tabPayment Entry`.`posting_date`,
                `tabSales Invoice`.`base_grand_total`,
                0
            ) as `credit`,

        `tabPayment Entry`.mode_of_payment
    FROM
        `tabSales Invoice`
    ON
        `tabPayment Entry Reference`.reference_doctype = 'Sales Invoice'
    AND
        `tabPayment Entry Reference`.reference_name = `tabSales Invoice`.name
    AND
        `tabSales Invoice`.docstatus = 1
    LEFT JOIN 
        `tabPayment Entry`
    LEFT JOIN
        `tabMode of Payment`
    ON
        `tabPayment Entry`.mode_of_payment = `tabMode of Payment`.name
    LEFT JOIN
        `tabPayment Entry Reference`
    ON
        `tabPayment Entry`.name = `tabPayment Entry Reference`.parent
    AND
        `tabPayment Entry`.docstatus = 1
    AND
        `tabPayment Entry Reference`.reference_doctype = 'Sales Invoice'
    GROUP BY 
        `tabSales Invoice`.name	

    """)
