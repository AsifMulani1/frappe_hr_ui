"""India statutory + payroll defaults pack.

Idempotent seeding of the masters a new Indian company needs to run payroll —
standard salary components, a salary structure, Indian leave types, and a starter
holiday list. Applied from the in-UI Setup Wizard (no Desk) or via:

    bench --site <site> execute frappe_hr_ui.india_defaults.apply

Production-oriented (no demo employees). Re-runnable: skips anything that exists.
"""

import frappe
from frappe.utils import getdate

# (component, type, amount_based_on_formula, formula/amount)
SALARY_COMPONENTS = [
	("Basic", "Earning", "base * 0.40"),
	("House Rent Allowance", "Earning", "base * 0.20"),
	("Special Allowance", "Earning", "base * 0.28"),
	("Conveyance Allowance", "Earning", "1600"),
	("Leave Travel Allowance", "Earning", "base * 0.05"),
	("Provident Fund", "Deduction", "base * 0.12"),
	("Professional Tax", "Deduction", "200"),
	("TDS", "Deduction", "0"),
]

# (leave type, annual allocation, is_lwp, is_carry_forward)
LEAVE_TYPES = [
	("Casual Leave", 12, 0, 0),
	("Sick Leave", 8, 0, 0),
	("Earned Leave", 18, 0, 1),
	("Comp Off", 0, 0, 0),
	("Leave Without Pay", 0, 1, 0),
]

# Fixed-date national holidays (festival dates vary year to year — edit after seeding).
NATIONAL_HOLIDAYS = [
	("01-26", "Republic Day"),
	("08-15", "Independence Day"),
	("10-02", "Gandhi Jayanti"),
	("12-25", "Christmas"),
]

STRUCTURE_NAME = "Standard Salary Structure"


def _company(company=None):
	return company or frappe.defaults.get_global_default("company") \
		or frappe.db.get_value("Company", {}, "name")


def _require_admin():
	if not frappe.has_permission("Salary Component", "create"):
		frappe.throw(frappe._("You are not permitted to apply defaults."), frappe.PermissionError)


@frappe.whitelist(methods=["POST"])
def create_company(company_name, country="India", currency="INR", abbr=None):
	"""Create the company if it doesn't exist and make it the default — so a fresh
	site never needs Desk. Employee/payroll all require a company."""
	if not frappe.has_permission("Company", "create"):
		frappe.throw(frappe._("You are not permitted to create a company."), frappe.PermissionError)
	company_name = (company_name or "").strip()
	if not company_name:
		frappe.throw(frappe._("Company name is required."))
	if frappe.db.exists("Company", company_name):
		company = company_name
	else:
		doc = frappe.get_doc({
			"doctype": "Company",
			"company_name": company_name,
			"country": country or "India",
			"default_currency": currency or "INR",
		})
		if abbr:
			doc.abbr = abbr
		doc.insert(ignore_permissions=True)  # ERPNext builds the chart of accounts here
		company = doc.name
	# make it the default everywhere
	gd = frappe.get_single("Global Defaults")
	gd.default_company = company
	gd.save(ignore_permissions=True)
	frappe.db.set_default("company", company)
	frappe.db.commit()
	return {"company": company}


def ensure_components(company, log):
	for name, ctype, _formula in SALARY_COMPONENTS:
		if not frappe.db.exists("Salary Component", name):
			frappe.get_doc({"doctype": "Salary Component", "salary_component": name,
							"type": ctype, "company": company}).insert(ignore_permissions=True)
			log["components"].append(name)


# Statutory deduction components india_payroll INJECTS at runtime. They must
# exist first or its ESI/LWF hooks skip silently (they `return` when the
# component is absent). NOT added to the structure — india_payroll appends them
# to each slip itself. Professional Tax already comes via SALARY_COMPONENTS.
STATUTORY_COMPONENTS = [("Employee State Insurance", "Deduction"), ("Labour Welfare Fund", "Deduction")]


def ensure_statutory_components(company, log):
	if "india_payroll" not in frappe.get_installed_apps():
		return
	for name, ctype in STATUTORY_COMPONENTS:
		if not frappe.db.exists("Salary Component", name):
			frappe.get_doc({"doctype": "Salary Component", "salary_component": name,
							"type": ctype, "company": company}).insert(ignore_permissions=True)
			log.setdefault("statutory_components", []).append(name)


def ensure_leave_types(log):
	for name, alloc, is_lwp, cf in LEAVE_TYPES:
		if not frappe.db.exists("Leave Type", name):
			frappe.get_doc({"doctype": "Leave Type", "leave_type_name": name,
							"max_leaves_allowed": alloc, "is_lwp": is_lwp,
							"is_carry_forward": cf}).insert(ignore_permissions=True)
			log["leave_types"].append(name)


def ensure_structure(company, log):
	# Already a submitted structure for THIS company? (Salary Structure is
	# company-scoped — checking by global name skips fresh companies.)
	if frappe.db.exists("Salary Structure", {"company": company, "docstatus": 1}):
		return
	# Names are globally unique, so suffix with the company abbr if "Standard
	# Salary Structure" is already taken by another company.
	name = STRUCTURE_NAME
	if frappe.db.exists("Salary Structure", name):
		abbr = frappe.db.get_value("Company", company, "abbr") or ""
		name = f"{STRUCTURE_NAME} - {abbr}".strip(" -")
	currency = frappe.db.get_value("Company", company, "default_currency") or "INR"
	earnings = [(n, f) for n, t, f in SALARY_COMPONENTS if t == "Earning"]
	deductions = [(n, f) for n, t, f in SALARY_COMPONENTS if t == "Deduction"]
	ss = frappe.get_doc({
		"doctype": "Salary Structure", "name": name, "company": company,
		"payroll_frequency": "Monthly", "currency": currency,
		"earnings": [{"salary_component": n, "amount_based_on_formula": 1, "formula": f} for n, f in earnings],
		"deductions": [{"salary_component": n, "amount_based_on_formula": 1, "formula": f} for n, f in deductions],
	})
	ss.insert(ignore_permissions=True)
	ss.submit()
	log["structure"] = name


def ensure_holiday_list(company, log):
	year = getdate().year
	name = f"India Holidays {year}"
	if not frappe.db.exists("Holiday List", name):
		hl = frappe.get_doc({
			"doctype": "Holiday List", "holiday_list_name": name,
			"from_date": f"{year}-01-01", "to_date": f"{year}-12-31", "weekly_off": "Sunday",
			"holidays": [{"holiday_date": f"{year}-{md}", "description": desc} for md, desc in NATIONAL_HOLIDAYS],
		})
		hl.insert(ignore_permissions=True)
		log["holiday_list"] = name
	# hrms v16 resolves an employee/company's holidays via a SUBMITTED
	# "Holiday List Assignment" — NOT Company.default_holiday_list. Without one,
	# payroll throws "No Holiday List was found". Create a company-level assignment.
	if not frappe.db.exists("Holiday List Assignment", {"assigned_to": company, "docstatus": 1}):
		hla = frappe.get_doc({
			"doctype": "Holiday List Assignment",
			"applicable_for": "Company",
			"assigned_to": company,
			"holiday_list": name,
			"from_date": f"{year}-01-01",
		})
		hla.insert(ignore_permissions=True)
		hla.submit()
		log["holiday_assignment"] = name
	# keep the legacy field set too (harmless; some ERPNext flows read it)
	if not frappe.db.get_value("Company", company, "default_holiday_list"):
		frappe.db.set_value("Company", company, "default_holiday_list", name)
		frappe.clear_document_cache("Company", company)
	return name


def ensure_statutory(log):
	"""Turn on the India statutory engine (PT / ESI / LWF) in Payroll Settings.
	Only meaningful when india_payroll is installed — it provides both the
	enable_* fields and the calculation that injects these deductions."""
	if "india_payroll" not in frappe.get_installed_apps():
		log["statutory"] = "india_payroll not installed"
		return
	meta = frappe.get_meta("Payroll Settings")
	enabled = []
	for f in ("enable_professional_tax", "enable_esic", "enable_lwf"):
		if meta.get_field(f) and not frappe.db.get_single_value("Payroll Settings", f):
			frappe.db.set_single_value("Payroll Settings", f, 1)
			enabled.append(f)
	log["statutory"] = enabled or "already enabled"


# Statutory registration numbers a company files returns under. Added to Company
# so registers/challans can carry the real codes (not a placeholder).
COMPANY_STATUTORY_FIELDS = [
	{"fieldname": "stat_registration_section", "label": "Statutory Registration (India)",
	 "fieldtype": "Section Break", "insert_after": "registration_details", "collapsible": 1},
	{"fieldname": "pf_registration_number", "label": "PF Establishment Code", "fieldtype": "Data",
	 "insert_after": "stat_registration_section"},
	{"fieldname": "esic_registration_number", "label": "ESIC Employer Code", "fieldtype": "Data",
	 "insert_after": "pf_registration_number"},
	{"fieldname": "stat_col_break", "fieldtype": "Column Break", "insert_after": "esic_registration_number"},
	{"fieldname": "pt_registration_number", "label": "Professional Tax Reg. No.", "fieldtype": "Data",
	 "insert_after": "stat_col_break"},
	{"fieldname": "tan_number", "label": "TAN (for TDS / 24Q)", "fieldtype": "Data",
	 "insert_after": "pt_registration_number"},
]


def ensure_statutory_fields(log=None):
	"""Idempotently add the statutory-registration fields to Company."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
	create_custom_fields({"Company": COMPANY_STATUTORY_FIELDS}, ignore_validate=True)
	if log is not None:
		log["statutory_fields"] = "ready"


def apply(company=None):
	"""Idempotently apply the India defaults pack; returns a summary of what was created."""
	company = _company(company)
	if not company:
		frappe.throw("No company found. Create a company first.")
	log = {"company": company, "components": [], "leave_types": [], "structure": None, "holiday_list": None, "statutory": None}
	ensure_components(company, log)
	ensure_statutory_components(company, log)
	ensure_leave_types(log)
	ensure_structure(company, log)
	ensure_holiday_list(company, log)
	ensure_statutory(log)
	ensure_statutory_fields(log)
	frappe.db.commit()
	print(f"India defaults applied to {company}: {log}")
	return log


@frappe.whitelist(methods=["POST"])
def apply_defaults(company=None):
	"""Permission-gated entry point for the in-UI setup wizard."""
	_require_admin()
	return apply(company)


@frappe.whitelist()
def defaults_status(company=None):
	"""What's already configured — drives the setup wizard's checklist."""
	company = _company(company)
	cdoc = frappe.db.get_value("Company", company, ["country", "default_currency", "abbr"], as_dict=True) if company else None
	return {
		"company": company,
		"has_company": bool(company),
		"country": cdoc.country if cdoc else None,
		"currency": cdoc.default_currency if cdoc else None,
		"abbr": cdoc.abbr if cdoc else None,
		"has_components": bool(frappe.db.exists("Salary Component", {"name": ["in", [c[0] for c in SALARY_COMPONENTS]]})),
		"components": frappe.db.count("Salary Component"),
		"leave_types": frappe.db.count("Leave Type"),
		"has_structure": bool(frappe.db.exists("Salary Structure", {"docstatus": 1})),
		"holiday_lists": frappe.db.count("Holiday List"),
		"employees": frappe.db.count("Employee", {"status": "Active"}),
		"india_payroll": "india_payroll" in frappe.get_installed_apps(),
		"statutory_enabled": "india_payroll" in frappe.get_installed_apps() and all(
			frappe.db.get_single_value("Payroll Settings", f)
			for f in ("enable_professional_tax", "enable_esic", "enable_lwf")
		),
	}
