"""Read APIs for the Frappe HR UI screens.

These assemble screen-shaped payloads from real hrms/erpnext DocTypes so the Vue
frontend can bind one resource per screen. No mock data — every value is a live
query against the employee's records.
"""

import frappe

from .base import *  # noqa: F401,F403  re-export helpers/constants
from .home_data import *  # noqa: F401,F403  re-export builders
from frappe.utils import getdate, nowdate, now_datetime, get_datetime, time_diff_in_seconds, add_days, formatdate, flt, get_last_day


# Per-leave-type accent (token-ish hex; the UI maps these to theme classes).


@frappe.whitelist()
def get_employee_profile():
	emp = frappe.db.get_value(
		"Employee", {"user_id": frappe.session.user, "status": "Active"}, "name"
	)
	if not emp:
		return {"employee": None}

	fields = [
		"name", "employee_number", "salutation", "first_name", "middle_name", "last_name",
		"employee_name", "designation", "department", "company", "branch", "grade",
		"employment_type", "date_of_joining", "reports_to", "default_shift", "status",
		"image", "gender", "date_of_birth", "blood_group", "marital_status",
		"cell_number", "personal_email", "company_email", "emergency_phone_number",
		"person_to_be_contacted", "current_address", "permanent_address",
		"pan_number", "ifsc_code", "provident_fund_account", "bank_name", "bank_ac_no",
		"salary_mode", "ctc", "holiday_list",
	]
	meta = frappe.get_meta("Employee")
	fields = [f for f in fields if f == "name" or meta.get_field(f)]
	d = frappe.db.get_value("Employee", emp, fields, as_dict=True)

	d["manager_name"] = (
		frappe.db.get_value("Employee", d.reports_to, "employee_name") if d.get("reports_to") else None
	)
	shift_label, _ = _shift_label(d)
	d["shift_label"] = shift_label
	d["location"] = d.get("branch") or "—"
	d["tenure"] = _tenure(d.get("date_of_joining"))

	# reporting chain (self -> up to top)
	chain, cur, seen = [], d.get("reports_to"), set()
	while cur and cur not in seen:
		seen.add(cur)
		m = frappe.db.get_value("Employee", cur, ["employee_name", "designation", "employee_number"], as_dict=True)
		if not m:
			break
		chain.append(m)
		cur = frappe.db.get_value("Employee", cur, "reports_to")
	d_chain = list(reversed(chain))

	# peers in same department
	peers = frappe.get_all(
		"Employee",
		filters={"department": d.get("department"), "status": "Active", "name": ["!=", emp]},
		fields=["employee_name", "designation", "employee_number"],
		limit=8,
	)

	# documents attached to the employee record
	files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Employee", "attached_to_name": emp},
		fields=["file_name", "file_size", "file_url", "creation"],
		order_by="creation desc",
	)
	documents = [
		{
			"name": f.file_name,
			"size": f"{round((f.file_size or 0) / 1024)} KB",
			"url": f.file_url,
		}
		for f in files
	]

	# assigned assets (erpnext Asset custodian) — empty unless tracked
	assets = []
	if frappe.db.exists("DocType", "Asset"):
		assets = frappe.get_all(
			"Asset",
			filters={"custodian": emp} if meta else {},
			fields=["asset_name", "name"],
			limit=10,
		) if frappe.get_meta("Asset").get_field("custodian") else []

	return {
		"employee": d,
		"reporting_line": d_chain,
		"peers": peers,
		"documents": documents,
		"assets": assets,
	}


# ---------------------------------------------------------------- attendance


# ---------------------------------------------------------------- leave


# ---------------------------------------------------------------- payslips


# ---------------------------------------------------------------- directory


# ---------------------------------------------------------------- announcements feed


# ---------------------------------------------------------------- claims


# ---------------------------------------------------------------- performance


# ---------------------------------------------------------------- helpdesk (Issue)


# ---------------------------------------------------------------- tax & fbp


# ================================================================ MANAGER


# ================================================================ HR ADMIN


# ----------------------------------------------------------- payroll


# ----------------------------------------------------------- compliance


# Component names align with the india_payroll engine (ESI / PT / LWF) and hrms
# (Provident Fund, Income Tax/TDS). `component` may be a list of aliases.


# ----------------------------------------------------------- recruitment


# ----------------------------------------------------------- performance (HR)


# ----------------------------------------------------------- analytics


# ================================================================ WRITES (ESS)


# Fields an employee may maintain on their OWN Employee record. HR seeds the
# primary/system-of-record fields at onboarding (name, DOB, DOJ, employee
# number, work email, designation/department/grade, status, CTC); the employee
# owns everything personal below. Anything not in this set is ignored server-side.


# ================================================================ GENERIC UI-FIRST WRITES
# Link-field option lookups the SPA is allowed to read (names only, not sensitive).
# Doctypes HR may create from an in-app drawer.
# Employee self-service docs: created for the logged-in employee (forced employee=self
# unless an HR/manager is creating on someone's behalf). "Appraisal" is handled inline.


