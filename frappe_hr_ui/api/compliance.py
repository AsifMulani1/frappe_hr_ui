# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Statutory compliance screens — registers, challans, company statutory identity."""

import frappe

from .core import (
	COMPANY_NAME,
	COMPLIANCE_META,
	_STATUTORY_FIELDS,
	_company,
	_component_total,
	_india_payroll_installed,
	_require_hr,
)


@frappe.whitelist()
def get_compliance(kind):
	_require_hr()
	c = COMPLIANCE_META.get(kind)
	if not c:
		return {}
	amount = _component_total(c["component"])
	comps = c["component"] if isinstance(c["component"], (list, tuple)) else [c["component"]]
	covered = frappe.db.sql(
		"""select count(distinct ss.employee) from `tabSalary Slip` ss
		join `tabSalary Detail` sd on sd.parent=ss.name
		where ss.docstatus=1 and sd.parentfield='deductions' and sd.salary_component in %s and sd.amount>0""",
		(tuple(comps),))[0][0]
	# real registration number this authority identifies the company by (from Company)
	company = COMPANY_NAME()
	reg_field = {"pf": "pf_registration_number", "esi": "esic_registration_number",
				 "pt": "pt_registration_number", "lwf": "pt_registration_number", "tds": "tan_number"}.get(kind)
	cmeta = frappe.get_meta("Company")
	establishment = frappe.db.get_value("Company", company, reg_field) if (reg_field and cmeta.get_field(reg_field)) else None
	return {
		"title": c["title"], "code": c["code"], "authority": c["authority"], "sub": c["sub"], "rate": c["rate"],
		"amount": amount, "covered": covered, "company": company, "establishment": establishment or None,
		"stats": [
			{"label": "Total contribution", "value": frappe.utils.fmt_money(amount, currency="INR"), "sub": "across slips", "icon": "rupee", "tone": "accent"},
			{"label": "Employees covered", "value": covered, "sub": "with this deduction", "icon": "users", "tone": "neutral"},
			{"label": "Filing status", "value": "Filed", "sub": "last cycle", "icon": "check", "tone": "success"},
			{"label": "Next due", "value": "15th", "sub": "monthly", "icon": "calendar", "tone": "warning"},
		],
	}


@frappe.whitelist()
def get_challan():
	_require_hr()
	rows = []
	for k, c in COMPLIANCE_META.items():
		amt = _component_total(c["component"])
		if amt:
			rows.append({"ref": f"{c['code']}-2606", "type": c["code"], "period": "Jun 2026",
				"amt": frappe.utils.fmt_money(amt, currency="INR"), "due": "15 Jun", "st": "Generated", "tone": "warning"})
	return {"rows": rows}


@frappe.whitelist()
def get_statcal():
	_require_hr()
	events = [
		{"date": "07", "mon": "Jun", "title": "TDS deposit + 24Q Q1 return", "tag": "TDS", "tone": "danger"},
		{"date": "15", "mon": "Jun", "title": "PF ECR + ESI contribution", "tag": "PF / ESI", "tone": "warning"},
		{"date": "15", "mon": "Jun", "title": "Issue Form 16 to employees", "tag": "TDS", "tone": "warning"},
		{"date": "20", "mon": "Jun", "title": "Professional Tax (Maharashtra)", "tag": "PT", "tone": "info"},
		{"date": "30", "mon": "Jun", "title": "June payroll disbursement", "tag": "Payroll", "tone": "accent"},
	]
	return {"events": events}


@frappe.whitelist()
def get_company_statutory(company=None):
	"""The company's statutory registration numbers (PF/ESI/PT/TAN) — for the
	statutory-profile screen and to stamp on registers/challans."""
	_require_hr()
	from frappe_hr_ui import india_defaults
	india_defaults.ensure_statutory_fields()  # idempotent — works even if setup wasn't run
	company = company or COMPANY_NAME()
	vals = frappe.db.get_value("Company", company, _STATUTORY_FIELDS + ["company_name", "tax_id"], as_dict=True) or {}
	vals["company"] = company
	return vals


@frappe.whitelist(methods=["POST"])
def save_company_statutory(values, company=None):
	_require_hr()
	if not frappe.has_permission("Company", "write"):
		frappe.throw(frappe._("You are not permitted to edit company settings."), frappe.PermissionError)
	company = company or COMPANY_NAME()
	data = frappe.parse_json(values) or {}
	cmeta = frappe.get_meta("Company")
	for f in _STATUTORY_FIELDS:
		if f in data and cmeta.get_field(f):
			frappe.db.set_value("Company", company, f, (data.get(f) or "").strip())
	frappe.db.commit()
	return {"company": company}
