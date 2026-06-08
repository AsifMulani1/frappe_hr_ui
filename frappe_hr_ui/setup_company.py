"""One-shot: run ERPNext's setup wizard to create the sample company with all
default masters (warehouses, chart of accounts, UOMs, etc.). Idempotent — does
nothing if the company already exists.

Run:  bench --site hrms.localhost execute frappe_hr_ui.setup_company.run
"""

import frappe

COMPANY = "Frappe Technologies Pvt. Ltd."
ABBR = "FT"


def run():
	if frappe.db.exists("Company", COMPANY):
		print(f"  = Company {COMPANY} already exists; skipping setup wizard")
		return

	from erpnext.setup.setup_wizard.setup_wizard import setup_complete

	args = frappe._dict(
		{
			"language": "English",
			"country": "India",
			"timezone": "Asia/Kolkata",
			"currency": "INR",
			"company_name": COMPANY,
			"company_abbr": ABBR,
			"chart_of_accounts": "Standard",
			"fy_start_date": "2026-04-01",
			"fy_end_date": "2027-03-31",
			"bank_account": "HDFC Bank",
			"full_name": "Administrator",
			"email": "admin@example.com",
			"password": "admin",
		}
	)
	setup_complete(args)
	frappe.db.commit()
	print(f"  + Setup wizard complete; company {COMPANY} created")
