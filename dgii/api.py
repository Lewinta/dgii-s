import frappe
import requests
from bs4 import BeautifulSoup

def get_tax_amount_for(doctype, docname, tax_type):
	doc = frappe.get_doc(doctype, docname)

	for row in doc.taxes:
		tax_types = row.meta.get_field("tax_type").options
		
		if not tax_type in tax_types.split("\n"):
			frappe.throw(_("The tax type provided was not found in the system!"))

		if row.tax_type == tax_type:
			return row.tax_amount

	return 0.000
	
def update_taxes_to_purchases():
	from dgii.hook.purchase_invoice import validate
	for name, in frappe.get_list("Purchase Invoice", as_list=True):
		doc = frappe.get_doc("Purchase Invoice", name )
		validate(doc, {})
		if doc.excise_tax or doc.legal_tip:
			doc.db_update()
			# print(
			# 	"""Added to {name}\n
			# 		\tExcise:{excise_tax}
			# 		\tLegal:{legal_tip} """.format(**doc.as_dict())
			# )

@frappe.whitelist()
def validate_ncf_limit(serie):
	# serie : ABC.####
	# next: 3
	# Yefri este codigo es provisional, reservar cualquier comentario gracias!

	limit = frappe.get_doc("NCF",{"serie":serie}, "max_limit").max_limit
	serie = serie.replace(".","").replace("#","")
	current = frappe.get_doc("Series",{"name":serie},"current").current
	
	return True if  current + 1  <  limit else False

@frappe.whitelist()
def get_rnc_details(tax_id):
    url = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    payload = {
        "ctl00$smMain": "ctl00$cphMain$upBusqueda|ctl00$cphMain$btnBuscarPorRNC",
        "ctl00$cphMain$txtRNCCedula": tax_id,
        "ctl00$cphMain$btnBuscarPorRNC": "BUSCAR",
        "__VIEWSTATE": "ztXf81D1Yz6otaYQbMjsrXX6LvkgqDdvZsD986HiAKNILVttEdH0BkgexulEm3O4w5yoY6MCJeBmO93B+CNNbZsumWfLQ67HOYNVHYl1Z6DPAmZITxw3ar/wjpqxf/U7PUpYmH9YepeYuvLpv0R/dOA3xDiPa5HPb9w1yk+G2V0Dsm2Ls4thkP2pWtEDxfy169aTWsAUNiLATtV37Qngs4u39IwEREKS2vwaMHmAKP+1YhqMUAZ33L9hw0ltO09Y3YXJJOtAnSfYZaT3wOFP6z5khBChZGyVvYbBt/R+LkiggfS/sVBwmwS8qIlydW7pbsh6Ca4c6UyT5IBza3T70a66SOYtQJdIVBKTm30ghOLQCsyh9O6Bw2nfKj1iNh7ofBvyNRoS/fihu9KP9IgcLvlXI7SlRF1QpdSBgXW+cEUW+VpIimYrBpIuidnQCJhMdmuvjFor5unFKQFyvrb7+L4jxMtL5/IAAxQtwR881LPCPVB6rVTAsjiUO3Q8Ki2hzejpEOajBsuKi/d74nYG7M1j4kF7HwHzJxKYq58IfgvBQ/i/4OHUEg/frQ26jBw4dbEFtsD7I67OKH6ekpXzHwXn6DlVNDQ6+WY43kfwuuvR4ZGHY1Ai5yXC2OhoCF14WfmSwL8KX9wmOHr3dgC8wsadUqsmm6cKZnCrWVJIO2PsoWkxPmykPKULRFBBzFXvYVSvdUDrOmGdv/kTQT85+loPja7JumhrAv4v8SHoVKoIWABNXMfVK+AtwmFHPvttoMjo1U7G22g2IgXxheARPrY+58b5QZEwk/ZMdhQkZHg92zz37dZNa2NXk8hzsl9NhT4zZrcWp8N/T/rQt4mHZCE8+N8m/mOj/y1cFpvzPcMwdmF3eErMhj4wEoPfDHlzL2587DlCjc1jhpxupblQVRDQOjD2oC+7/wuJYc3WzD+0/NePvQ9TWwmOWH4JsRdCstQMIJmhs5xZsfdgKMv7hEexZOKRzqzGLwpRvibfX55qYbX8VBdhb+bxFkHEbn1+w6lEX1+lymmtpkJAtEkjojgrViDdZdhbcBF8Phz4EXWrKdfy4OKziGM62C1E3oI0LiOZGrMBUyicxrSlfhWM2mVZ6QoyjV/UOHuCaSsdkFRhOOOKz7yTIJsj3V64CaqjBbIrvwqYJTAnl/EhKvb4K2gBP1k=",
        "__VIEWSTATEGENERATOR": "4F4BAA71",
        "__EVENTVALIDATION": "8gdBgB8p+W4vlolbt+pqct/f1QKKTusWXiPnrwM1T+1qpk18NFvvOiKiEnBs+DfhYcmJMY8tu0XqtlIr1pYIykiQX0Ux5he7BuemC5rbbjwSlBqdA5buqKw7t4zTOHBQGPW8qpFcP6p1mo/I6kUjG31q3P8PIat9HgInq1/SqfbaviGrSF4q7C3/c93YLrhDaQr2Ery1cbrlASp4mXTOhy+r0ateZjB5bhBqjvoPqIfHZ/5r0Y0i8pZMAnu+Tq24oVGEYw==",
        "__ASYNCPOST": True
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Let's Find the table by ID
        table = soup.find('table', id='cphMain_dvDatosContribuyentes')
        if len(list(table.children)) < 2:
            # Is empty maybe there was an error
            return {}
        
        # Let's Extract the required data
        company_name = table.find_all('tr')[1].find_all('td')[1].text
        brand_name = table.find_all('tr')[2].find_all('td')[1].text
        status = table.find_all('tr')[5].find_all('td')[1].text

        return {
            "tax_id": tax_id,
            "company_name": company_name,
            "brand_name": brand_name,
            "status": status
        }
    else:
        return {}