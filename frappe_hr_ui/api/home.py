# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Employee home dashboard + quick lookups — leave days, docs, leave/expense types, check-in."""

import frappe
from frappe.utils import getdate, now_datetime

from .core import (
	_CREATE_SELF,
	_announcements,
	_attendance_summary,
	_celebrations,
	_current_employee,
	_emp,
	_holidays,
	_latest_payslip,
	_leave_balance,
	_manager_name,
	_shift_label,
	_tasks,
	_today_attendance,
	_week,
	_who_is_out,
)


@frappe.whitelist()
def get_leave_days(leave_type, from_date, to_date, half_day=0):
	"""Live preview for the apply-leave drawer — days + balance, computed by hrms."""
	emp = _current_employee()
	if not (emp and leave_type and from_date and to_date):
		return {"days": 0, "balance": None}
	from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days, get_leave_balance_on
	try:
		days = get_number_of_leave_days(emp["name"], leave_type, from_date, to_date, frappe.utils.cint(half_day))
		bal = get_leave_balance_on(emp["name"], leave_type, getdate(to_date),
			consider_all_leaves_in_the_allocation_period=True)
		return {"days": days, "balance": bal}
	except Exception:
		return {"days": 0, "balance": None}


@frappe.whitelist()
def get_my_docs(doctype):
	"""List the current employee's own records of an ESS self-service doctype."""
	if doctype not in _CREATE_SELF:
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	emp = _current_employee()
	if not emp:
		return {"rows": [], "is_submittable": False}
	meta = frappe.get_meta(doctype)
	fieldnames = {f.fieldname for f in meta.fields}
	fields = ["name"]
	for cand in ("status", "posting_date", "from_date", "work_from_date", "work_end_date",
				 "leave_type", "leave_period", "advance_amount", "amount", "purpose", "reason", "creation"):
		if cand in fieldnames:
			fields.append(cand)
	if meta.is_submittable:
		fields.append("docstatus")
	rows = frappe.get_all(doctype, filters={"employee": emp["name"]},
		fields=list(dict.fromkeys(fields)), order_by="creation desc", limit=50)
	return {"rows": rows, "is_submittable": bool(meta.is_submittable)}


@frappe.whitelist()
def get_leave_types():
	"""Leave types the current employee can apply for (with balance)."""
	emp = _current_employee()
	bal = {b["type"]: b for b in _leave_balance(emp)} if emp else {}
	return {"types": [{"value": lt.name, "label": lt.name, "balance": bal.get(lt.name, {}).get("balance")}
					  for lt in frappe.get_all("Leave Type", fields=["name"], order_by="name")]}


@frappe.whitelist()
def get_expense_types():
	return {"types": [{"value": t.name, "label": t.name}
					  for t in frappe.get_all("Expense Claim Type", fields=["name"], order_by="name")]}


@frappe.whitelist(methods=["POST"])
def toggle_checkin():
	"""Punch the employee in or out for the current day and return today's state."""
	employee = _current_employee()
	if not employee:
		frappe.throw("No employee record linked to this user.")

	today = getdate()
	logs = frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee["name"], "time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
		fields=["log_type"],
		order_by="time asc",
	)
	has_in = any(l.log_type == "IN" for l in logs)
	last_out = logs and logs[-1].log_type == "OUT"
	log_type = "IN" if (not has_in or last_out) else "OUT"

	frappe.get_doc({
		"doctype": "Employee Checkin",
		"employee": employee["name"],
		"time": now_datetime(),
		"log_type": log_type,
	}).insert(ignore_permissions=True)
	frappe.db.commit()

	shift_label, shift = _shift_label(employee)
	return _today_attendance(employee, shift)


@frappe.whitelist()
def get_employee_home():
	employee = _current_employee()
	if not employee:
		return {"employee": None}

	shift_label, shift = _shift_label(employee)
	employee["shift_label"] = shift_label
	employee["manager_name"] = _manager_name(employee)
	employee["location"] = employee.get("branch") or "—"

	return {
		"employee": employee,
		"today": _today_attendance(employee, shift),
		"week": _week(employee),
		"attendance_summary": _attendance_summary(employee),
		"leave_balance": _leave_balance(employee),
		"latest_payslip": _latest_payslip(employee),
		"who_is_out": _who_is_out(employee),
		"holidays": _holidays(employee),
		"celebrations": _celebrations(employee),
		"announcements": _announcements(),
		"tasks": _tasks(employee),
	}


@frappe.whitelist()
def get_tax_screen():
	emp = _current_employee()
	if not emp:
		return {"employee": None}
	# TDS paid this FY from salary slips
	slips = frappe.get_all("Salary Slip", filters={"employee": emp["name"], "docstatus": 1},
		fields=["name", "end_date"])
	tds = 0.0
	for s in slips:
		tds += frappe.db.get_value("Salary Detail",
			{"parent": s.name, "salary_component": "TDS", "parentfield": "deductions"}, "amount") or 0
	# declarations (India)
	decls = []
	declared_total = 0
	dec = frappe.get_all("Employee Tax Exemption Declaration",
		filters={"employee": emp["name"]}, fields=["name"], limit=1)
	if dec:
		for d in frappe.get_all("Employee Tax Exemption Declaration Category",
			filters={"parent": dec[0].name},
			fields=["exemption_category", "max_amount", "amount"]):
			decls.append({"sec": d.exemption_category, "limit": d.max_amount, "declared": d.amount})
			declared_total += d.amount or 0
	# flexible benefits from the latest salary slip's flexi components (real, not hardcoded)
	fbp = []
	if slips:
		flexi_comps = {c.name for c in frappe.get_all("Salary Component", filters={"is_flexible_benefit": 1}, fields=["name"])}
		if flexi_comps:
			latest = sorted(slips, key=lambda s: s.end_date)[-1]
			for e in frappe.get_all("Salary Detail",
				filters={"parent": latest.name, "parentfield": "earnings"},
				fields=["salary_component", "amount"]):
				if e.salary_component in flexi_comps:
					fbp.append([e.salary_component, e.amount])
	return {
		"employee": emp,
		"tds_paid": tds,
		"declarations": decls,
		"declared_total": declared_total,
		"fbp": fbp,
	}
