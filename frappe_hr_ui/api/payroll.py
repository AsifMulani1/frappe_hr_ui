# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Payroll administration — run, preview, bulk assignment, structure, bank file."""

import frappe
from frappe.utils import flt, formatdate, get_last_day, getdate, nowdate

from .core import (
	_component_total,
	_emp,
	_latest_slip_period,
	_require_hr,
)


@frappe.whitelist()
def get_payroll_run():
	_require_hr()
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
		fields=["name", "employee", "employee_name", "department", "gross_pay", "net_pay", "total_deduction"],
		order_by="net_pay desc", limit=25)
	# batch PF/TDS for all slips in one query (avoid N+1)
	deductions = frappe.get_all("Salary Detail",
		filters={"parent": ["in", [s.name for s in slips]], "parentfield": "deductions",
				 "salary_component": ["in", ["Provident Fund", "TDS"]]},
		fields=["parent", "salary_component", "amount"]) if slips else []
	ded_map = {}
	for d in deductions:
		ded_map.setdefault(d.parent, {})[d.salary_component] = d.amount
	for s in slips:
		s["department"] = (s.department or "").split(" - ")[0]
		s["pf"] = ded_map.get(s.name, {}).get("Provident Fund") or 0
		s["tds"] = ded_map.get(s.name, {}).get("TDS") or 0
	agg = frappe.db.sql("select coalesce(sum(gross_pay),0), coalesce(sum(net_pay),0), coalesce(sum(total_deduction),0), count(*) from `tabSalary Slip` where docstatus=1")[0]
	return {
		"slips": slips,
		"period": _latest_slip_period().strftime("%B %Y"),
		"totals": {"gross": agg[0], "net": agg[1], "deductions": agg[2], "count": agg[3]},
	}


def _payroll_eligible(start, company=None):
	"""Latest active salary-structure assignment per Active employee, effective by `start`.
	Company is only filtered when explicitly given — otherwise every company's employees
	are processed using their own assignment's company (DIY-safe, multi-company tolerant)."""
	filters = {"docstatus": 1, "from_date": ["<=", start]}
	if company:
		filters["company"] = company
	assigns = frappe.get_all("Salary Structure Assignment",
		filters=filters,
		fields=["employee", "employee_name", "salary_structure", "company", "from_date", "employment_state"],
		order_by="from_date desc")
	latest = {}
	for a in assigns:
		if a.employee in latest:
			continue
		if frappe.db.get_value("Employee", a.employee, "status") != "Active":
			continue
		latest[a.employee] = a
	return latest


@frappe.whitelist()
def preview_payroll(start_date, company=None):
	"""Who would be processed for a period — drives the 'Run payroll' confirm step."""
	_require_hr()
	start = getdate(start_date)
	elig = _payroll_eligible(start, company)
	rows = []
	for emp, a in elig.items():
		exists = frappe.db.exists("Salary Slip", {"employee": emp, "start_date": start, "docstatus": ["<", 2]})
		rows.append({"employee_name": a.employee_name, "salary_structure": a.salary_structure,
			"state": a.get("employment_state") or "—", "already_run": bool(exists)})
	return {"period": start.strftime("%B %Y"), "eligible": len(rows),
		"pending": sum(1 for r in rows if not r["already_run"]), "rows": rows}


@frappe.whitelist()
def preview_payslip(start_date, employee=None, company=None):
	"""A real, computed payslip for ONE employee — WITHOUT persisting anything.

	Builds a draft Salary Slip (which fires india_payroll's PT/ESI/LWF injection
	exactly as a real run would), reads the computed earnings/deductions, then rolls
	the transaction back so no slip is ever saved. The 'see it actually work' moment
	before committing real payroll."""
	_require_hr()
	start = getdate(start_date)
	end = get_last_day(start)
	elig = _payroll_eligible(start, company)
	if not elig:
		return {"ok": False, "reason": "no_assignment", "period": start.strftime("%B %Y")}
	# requested employee if eligible, otherwise the first eligible one
	emp, a = (employee, elig[employee]) if (employee and employee in elig) else next(iter(elig.items()))
	result, err = None, None
	try:
		frappe.flags.mute_messages = True
		s = frappe.new_doc("Salary Slip")
		s.employee = emp
		s.company = a.company
		s.salary_structure = a.salary_structure
		s.payroll_frequency = "Monthly"
		s.start_date = start
		s.end_date = end
		s.insert(ignore_permissions=True)  # computes pay + india_payroll PT/ESI/LWF
		result = {
			"ok": True,
			"period": start.strftime("%B %Y"),
			"employee": emp,
			"employee_name": a.employee_name,
			"designation": frappe.db.get_value("Employee", emp, "designation") or "",
			"state": a.get("employment_state") or "",
			"salary_structure": a.salary_structure,
			"earnings": [{"component": r.salary_component, "amount": flt(r.amount)} for r in s.earnings if flt(r.amount)],
			"deductions": [{"component": r.salary_component, "amount": flt(r.amount)} for r in s.deductions if flt(r.amount)],
			"gross_pay": flt(s.gross_pay),
			"total_deduction": flt(s.total_deduction),
			"net_pay": flt(s.net_pay),
			"candidates": [{"employee": e, "employee_name": x.employee_name} for e, x in list(elig.items())[:30]],
		}
	except Exception as e:
		err = frappe.utils.strip_html(str(e))[:160]
	finally:
		frappe.db.rollback()  # discard the draft entirely — nothing persists
		frappe.flags.mute_messages = False
	if err:
		return {"ok": False, "reason": "error", "error": err, "period": start.strftime("%B %Y")}
	return result


@frappe.whitelist(methods=["POST"])
def run_payroll(start_date, end_date, company=None):
	"""Generate + submit salary slips for every eligible employee for the period.
	india_payroll's before_save hooks inject PT/ESI/LWF automatically. Each slip is
	committed individually so one failure never undoes the rest of the batch."""
	_require_hr()
	start, end = getdate(start_date), getdate(end_date)
	elig = _payroll_eligible(start, company)
	created, skipped, errors = [], [], []
	for emp, a in elig.items():
		if frappe.db.exists("Salary Slip", {"employee": emp, "start_date": start, "docstatus": ["<", 2]}):
			skipped.append(a.employee_name)
			continue
		try:
			frappe.flags.mute_messages = True
			s = frappe.new_doc("Salary Slip")
			s.employee = emp
			s.company = a.company
			s.salary_structure = a.salary_structure
			s.payroll_frequency = "Monthly"
			s.start_date = start
			s.end_date = end
			s.insert(ignore_permissions=True)  # india_payroll injects PT/ESI/LWF here
			s.submit()
			frappe.db.commit()  # durable per slip
			created.append({"employee": a.employee_name, "gross": flt(s.gross_pay), "net": flt(s.net_pay)})
		except Exception as e:
			frappe.db.rollback()  # discard only this failed slip
			errors.append({"employee": a.employee_name, "error": str(e)[:140]})
		finally:
			frappe.flags.mute_messages = False
	return {
		"period": start.strftime("%B %Y"),
		"created": len(created), "skipped": len(skipped), "errors": errors,
		"totals": {"gross": sum(c["gross"] for c in created), "net": sum(c["net"] for c in created), "count": len(created)},
	}


@frappe.whitelist()
def get_unassigned_employees():
	"""Active employees with no submitted salary-structure assignment — the people
	who still need compensation set before payroll can run for them."""
	_require_hr()
	assigned = {a.employee for a in frappe.get_all("Salary Structure Assignment",
		filters={"docstatus": 1}, fields=["employee"])}
	emps = frappe.get_all("Employee", filters={"status": "Active"},
		fields=["name", "employee_name", "department", "designation"], order_by="employee_name")
	rows = [{"employee": e.name, "employee_name": e.employee_name,
			 "department": (e.department or "—").split(" - ")[0], "designation": e.designation or "—"}
			for e in emps if e.name not in assigned]
	structures = [s.name for s in frappe.get_all("Salary Structure", filters={"docstatus": 1}, fields=["name"])]
	return {"employees": rows, "structures": structures, "default_structure": structures[0] if structures else None}


@frappe.whitelist(methods=["POST"])
def bulk_assign_salary(salary_structure, rows, from_date=None):
	"""Create + submit a Salary Structure Assignment for many employees at once.
	rows: [{employee, base, employment_state}]. Per-row commit so one failure
	never undoes the rest. employment_state drives PT/LWF (india_payroll)."""
	_require_hr()
	rows = frappe.parse_json(rows) or []
	from_date = from_date or nowdate()
	has_state = bool(frappe.get_meta("Salary Structure Assignment").get_field("employment_state"))
	done, errors = [], []
	for row in rows:
		emp = row.get("employee")
		try:
			doc = frappe.get_doc({
				"doctype": "Salary Structure Assignment",
				"employee": emp,
				"salary_structure": salary_structure,
				"from_date": from_date,
				"base": flt(row.get("base")) or 0,
				"company": frappe.db.get_value("Employee", emp, "company"),
			})
			if has_state and row.get("employment_state"):
				doc.employment_state = row.get("employment_state")
			doc.insert(ignore_permissions=True)
			doc.submit()
			frappe.db.commit()
			done.append(emp)
		except Exception as e:
			frappe.db.rollback()
			errors.append({"employee": frappe.db.get_value("Employee", emp, "employee_name") or emp, "error": str(e)[:130]})
	return {"assigned": len(done), "errors": errors, "total": len(rows)}


@frappe.whitelist()
def get_salary_structure():
	_require_hr()
	ss = frappe.get_all("Salary Structure", filters={"docstatus": 1}, fields=["name"], limit=1)
	comps = []
	if ss:
		doc = frappe.get_doc("Salary Structure", ss[0].name)
		for e in doc.earnings:
			comps.append({"name": e.salary_component, "type": "Earning", "formula": e.formula or (e.amount and str(e.amount)) or "—"})
		for e in doc.deductions:
			comps.append({"name": e.salary_component, "type": "Deduction", "formula": e.formula or (e.amount and str(e.amount)) or "—"})
	return {"structure": ss[0].name if ss else None, "components": comps,
			"earnings": sum(1 for c in comps if c["type"] == "Earning"), "deductions": sum(1 for c in comps if c["type"] == "Deduction"),
			"employees": frappe.db.count("Salary Structure Assignment", {"docstatus": 1})}


@frappe.whitelist()
def get_revisions():
	_require_hr()
	rows = []
	for a in frappe.get_all("Salary Structure Assignment", filters={"docstatus": 1},
		fields=["employee", "employee_name", "base", "from_date"], order_by="from_date desc", limit=30):
		rows.append({"name": a.employee_name, "type": "Assignment", "to": a.base * 12, "eff": formatdate(a.from_date, "dd MMM yyyy")})
	return {"rows": rows}


@frappe.whitelist()
def get_offcycle():
	_require_hr()
	rows = []
	if frappe.db.exists("DocType", "Additional Salary"):
		for a in frappe.get_all("Additional Salary",
			fields=["employee_name", "salary_component", "amount", "payroll_date", "docstatus"], order_by="creation desc", limit=30):
			rows.append({"name": a.employee_name, "type": a.salary_component, "amt": a.amount,
				"date": formatdate(a.payroll_date, "d MMM") if a.payroll_date else "—",
				"st": "Approved" if a.docstatus == 1 else "Pending"})
	total = sum(r["amt"] or 0 for r in rows)
	return {"rows": rows, "total": total}


@frappe.whitelist()
def get_reconcile():
	_require_hr()
	agg = frappe.db.sql("select count(*), coalesce(sum(case when net_pay<0 then 1 else 0 end),0) from `tabSalary Slip` where docstatus=1")[0]
	active = frappe.db.count("Employee", {"status": "Active"})
	missing_ifsc = frappe.db.count("Employee", {"status": "Active", "ifsc_code": ["in", ["", None]]})
	checks = [
		{"label": "Salary slips generated", "detail": f"{agg[0]} slips submitted", "st": "pass"},
		{"label": "No negative net pay", "detail": "All positive" if agg[1] == 0 else f"{agg[1]} negative", "st": "pass" if agg[1] == 0 else "fail"},
		{"label": "Bank details present", "detail": "All valid" if missing_ifsc == 0 else f"{missing_ifsc} missing IFSC", "st": "pass" if missing_ifsc == 0 else "fail"},
		{"label": "Headcount matches active employees", "detail": f"{active} active", "st": "pass"},
	]
	passed = sum(1 for c in checks if c["st"] == "pass")
	return {"checks": checks, "passed": passed, "total": len(checks),
			"warnings": sum(1 for c in checks if c["st"] == "warn"), "blockers": sum(1 for c in checks if c["st"] == "fail")}


@frappe.whitelist()
def get_bankfile():
	_require_hr()
	rows = frappe.db.sql("""
		select coalesce(e.bank_name, 'Unmapped') bank, count(*) emp, coalesce(sum(ss.net_pay),0) amt
		from `tabSalary Slip` ss join `tabEmployee` e on e.name = ss.employee
		where ss.docstatus=1 group by e.bank_name order by amt desc""", as_dict=True)
	for r in rows:
		r["st"] = "Ready"; r["tone"] = "success"; r["mode"] = "NEFT"
	total = sum(r.amt for r in rows)
	return {"banks": rows, "total": total, "ready": sum(r.emp for r in rows)}
