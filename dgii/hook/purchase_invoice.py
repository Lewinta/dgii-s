import frappe

def validate(doc, event):
	set_taxes(doc)
	calculate_totals(doc)

def calculate_totals(doc):
	total_bienes = total_servicios = .000

	for item in doc.items:
		if item.item_type == "Bienes":
			total_bienes += item.amount
		
		if item.item_type == "Servicios":
			total_servicios += item.amount
	
	doc.monto_facturado_bienes = total_bienes
	doc.monto_facturado_servicios = total_servicios

def set_taxes(doc):	
	conf = frappe.get_single(
		"DGII Settings"
	)
	
	total_tip = total_excise = .000

	if conf.itbis_account:
		total_tip = sum( 
			[ row.tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.itbis_account,
					doc.taxes
				)
			]

		)
		doc.total_itbis = total_tip

	if conf.legal_tip_account:
		total_tip = sum( 
			[ row.tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.legal_tip_account,
					doc.taxes
				)
			]

		)
		doc.legal_tip = total_tip
		
	if conf.excise_tax:
		total_excise = sum( 
			[ row.tax_amount_after_discount_amount for row in filter(
					lambda x: x.account_head == conf.excise_tax,
					doc.taxes
				)
			]

		)
		doc.excise_tax = total_excise
	
	if conf.other_taxes:
		for tax in conf.other_taxes:
			total_amount = .000
			total_amount = sum( 
				[ row.tax_amount_after_discount_amount for row in filter(
						lambda x: x.account_head == tax.account,
						doc.taxes
					)
				]
			)
			doc.set(tax.tax_type, total_amount)


