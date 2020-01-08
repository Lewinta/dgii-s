import frappe

def update_series_ncf(ncf):
	if not ncf or not ncf.get('doctype') or ncf.get('doctype') != "NCF":
		return

	name = ncf.serie.split(".")[0]

	# Si la secuencia de NCF no existe vamos a crearla
	if not frappe.db.sql("SELECT name FROM `tabSeries` where name = %s", name):
		frappe.db.sql("""
				INSERT INTO
					`tabSeries` (name, current)
				VALUES
					(%s, %s)
			""", (name, ncf.current)
		)
	
		return
	# Si ya existe solo hay que modificarla 	 
	frappe.db.sql("""
			UPDATE 
				`tabSeries`
			SET 
				current = %s
			WHERE 
				name = %s
		""", (ncf.current, name)
	)
