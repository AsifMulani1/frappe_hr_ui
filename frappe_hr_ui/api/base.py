# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Shared base layer — permission/company helpers and module-level constants."""

import frappe
from frappe.utils import getdate

__all__ = [
	"LEAVE_COLORS",
	"LEAVE_CODE",
	"HR_ROLES",
	"COMPLIANCE_META",
	"_STATUTORY_FIELDS",
	"SELF_EDITABLE_FIELDS",
	"_CREATE_HR",
	"_CREATE_SELF",
	"_LINK_OK",
	"_current_employee",
	"_emp",
	"_require",
	"_require_hr",
	"_require_manager",
	"_company",
	"COMPANY_NAME",
	"_india_payroll_installed",
	"_component_total",
	"_latest_slip_period",
	"_tenure",
	"_shift_label",
	"_manager_name",
]


LEAVE_COLORS = {
	"Casual Leave": "blue",
	"Sick Leave": "green",
	"Earned Leave": "violet",
	"Comp Off": "orange",
}


LEAVE_CODE = {
	"Casual Leave": "CL",
	"Sick Leave": "SL",
	"Earned Leave": "EL",
	"Comp Off": "CO",
}


HR_ROLES = ("HR Manager", "HR User", "System Manager")


COMPLIANCE_META = {
	"pf": {"title": "Provident Fund (EPF)", "code": "PF", "authority": "EPFO", "component": "Provident Fund",
		   "sub": "Employees' Provident Fund · monthly ECR filing", "rate": "12% of basic (₹15,000 wage ceiling for EPS)"},
	"esi": {"title": "Employees' State Insurance", "code": "ESI", "authority": "ESIC", "component": "Employee State Insurance",
			"sub": "Medical & cash benefits for employees ≤ ₹21,000", "rate": "4% of gross (employee + employer)"},
	"pt": {"title": "Professional Tax", "code": "PT", "authority": "State govt.", "component": "Professional Tax",
		   "sub": "State-levied tax · slabs vary by state", "rate": "Slab-based, by employment state"},
	"lwf": {"title": "Labour Welfare Fund", "code": "LWF", "authority": "State labour dept.", "component": "Labour Welfare Fund",
			"sub": "State welfare fund · employee + employer contribution", "rate": "Slab-based, by state (half-yearly in most)"},
	"tds": {"title": "Tax Deducted at Source", "code": "TDS", "authority": "Income Tax Dept.", "component": ["TDS", "Income Tax"],
			"sub": "Salary TDS under Section 192 · quarterly 24Q filing", "rate": "As per slab and chosen regime"},
}


_STATUTORY_FIELDS = ["pf_registration_number", "esic_registration_number", "pt_registration_number", "tan_number"]


SELF_EDITABLE_FIELDS = {
	# personal
	"gender", "blood_group", "marital_status",
	# contact
	"personal_email", "cell_number", "current_address", "permanent_address",
	# emergency
	"person_to_be_contacted", "emergency_phone_number", "relation",
	# bank (own salary account)
	"bank_name", "bank_ac_no", "ifsc_code",
	# statutory id
	"pan_number",
}


_CREATE_HR = {
	"Job Opening", "Job Applicant", "Interview", "Job Offer",
	"Employee Onboarding", "Employee Separation", "Employee Transfer",
	"Additional Salary", "Salary Structure Assignment", "Salary Component",
	"Shift Assignment", "Department", "Designation",
}


_CREATE_SELF = {
	"Employee Tax Exemption Declaration", "Employee Advance",
	"Compensatory Leave Request", "Leave Encashment",
}


_LINK_OK = {
	"Company", "Department", "Designation", "Gender", "Employee", "Shift Type",
	"Salary Component", "Salary Structure", "Appraisal Cycle", "Interview Type",
	"Job Opening", "Job Applicant", "Job Offer", "Payroll Period", "Currency",
	"Leave Type", "Employee Onboarding Template", "Employee Separation Template",
	"Holiday List", "Branch", "Employment Type", "Employee Grade",
}


def _current_employee():
	emp = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user, "status": "Active"},
		[
			"name", "employee_number", "first_name", "employee_name", "designation",
			"department", "company", "reports_to", "branch", "default_shift",
			"date_of_joining", "image", "cell_number", "personal_email", "company_email",
			"holiday_list",
		],
		as_dict=True,
	)
	return emp


def _emp():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user, "status": "Active"}, "name")


def _require(*roles):
	"""Block the call unless the session user holds one of the given roles."""
	if frappe.session.user == "Administrator":
		return
	if not (set(roles) & set(frappe.get_roles())):
		frappe.throw(frappe._("You are not permitted to access this resource."), frappe.PermissionError)


def _require_hr():
	_require(*HR_ROLES)


def _require_manager():
	"""HR, or anyone who actually manages people / approves requests."""
	roles = set(frappe.get_roles())
	if set(HR_ROLES) & roles or {"Leave Approver", "Expense Approver"} & roles:
		return
	emp = _emp()
	if emp and frappe.db.exists("Employee", {"reports_to": emp, "status": ["!=", "Left"]}):
		return
	frappe.throw(frappe._("You are not permitted to access this resource."), frappe.PermissionError)


def _company():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "company") or COMPANY_NAME()


def COMPANY_NAME():
	# Prefer the configured default company; fall back to the one that actually
	# has employees (handles multi-company / demo setups), then any company.
	default = frappe.defaults.get_global_default("company")
	if default:
		return default
	by_emp = frappe.db.sql("""select company, count(*) c from `tabEmployee`
		where status='Active' and company is not null group by company order by c desc limit 1""")
	return by_emp[0][0] if by_emp else frappe.db.get_value("Company", {}, "name")


def _india_payroll_installed():
	"""The india_payroll app provides the ESI/PT/LWF statutory engine + registers.
	India builds assume it's present; UI degrades gracefully when it isn't."""
	return "india_payroll" in frappe.get_installed_apps()


def _component_total(component, parentfield="deductions"):
	# `component` may be a single name or a list of aliases (e.g. TDS is booked
	# as "Income Tax" or "TDS" depending on the salary-component setup).
	comps = list(component) if isinstance(component, (list, tuple)) else [component]
	rows = frappe.db.sql(
		"""select coalesce(sum(sd.amount),0) from `tabSalary Detail` sd
		join `tabSalary Slip` ss on ss.name = sd.parent
		where ss.docstatus=1 and sd.parentfield=%s and sd.salary_component in %s""",
		(parentfield, tuple(comps)),
	)
	return rows[0][0] if rows else 0


def _latest_slip_period():
	row = frappe.get_all("Salary Slip", filters={"docstatus": 1}, fields=["end_date"], order_by="end_date desc", limit=1)
	return getdate(row[0].end_date) if row else getdate()


def _tenure(doj):
	if not doj:
		return "—"
	doj = getdate(doj)
	today = getdate()
	months = (today.year - doj.year) * 12 + (today.month - doj.month)
	if today.day < doj.day:
		months -= 1
	years, mons = divmod(max(0, months), 12)
	parts = []
	if years:
		parts.append(f"{years} year{'s' if years != 1 else ''}")
	parts.append(f"{mons} month{'s' if mons != 1 else ''}")
	return ", ".join(parts)


def _shift_label(employee):
	shift = employee.get("default_shift")
	if shift:
		st = frappe.db.get_value("Shift Type", shift, ["name", "start_time", "end_time"], as_dict=True)
		if st:
			def hhmm(t):
				# t is a timedelta
				total = int(t.total_seconds()) if t else 0
				return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
			return f"{st.name} ({hhmm(st.start_time)} – {hhmm(st.end_time)})", st
	return "General (10:00 – 19:00)", frappe._dict({"start_time": None, "end_time": None})


def _manager_name(employee):
	if employee.get("reports_to"):
		return frappe.db.get_value("Employee", employee["reports_to"], "employee_name")
	return None
