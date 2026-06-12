# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Employee self-service screens — attendance, leave, payslips, directory, performance, tickets, tax."""

import frappe
from frappe.utils import add_days, formatdate, get_datetime, getdate

from .core import (
	HR_ROLES,
	_announcements,
	_attendance_summary,
	_current_employee,
	_emp,
	_leave_balance,
	_who_is_out,
)


@frappe.whitelist()
def get_employee_attendance():
	emp = _current_employee()
	if not emp:
		return {"employee": None}
	today = getdate()
	start = add_days(today, -45)
	att = frappe.get_all(
		"Attendance",
		filters={"employee": emp["name"], "attendance_date": [">=", start], "docstatus": 1},
		fields=["attendance_date", "status", "in_time", "out_time", "working_hours"],
		order_by="attendance_date desc",
	)
	checkins = frappe.get_all(
		"Employee Checkin",
		filters={"employee": emp["name"], "time": [">=", f"{start} 00:00:00"]},
		fields=["time", "log_type"],
		order_by="time asc",
	)
	# group check-ins by day -> first IN / last OUT
	by_day = {}
	for c in checkins:
		d = get_datetime(c.time).date()
		by_day.setdefault(d, []).append(c)
	logs = []
	for a in att:
		d = getdate(a.attendance_date)
		day_logs = by_day.get(d, [])
		first_in = next((get_datetime(l.time) for l in day_logs if l.log_type == "IN"), get_datetime(a.in_time) if a.in_time else None)
		last_out = next((get_datetime(l.time) for l in reversed(day_logs) if l.log_type == "OUT"), get_datetime(a.out_time) if a.out_time else None)
		hrs = a.working_hours
		logs.append({
			"date": d.strftime("%d %b, %a"),
			"in": first_in.strftime("%H:%M") if first_in else "—",
			"out": last_out.strftime("%H:%M") if last_out else "—",
			"hrs": f"{int(hrs)}h {int((hrs % 1) * 60):02d}m" if hrs else "—",
			"status": a.status,
			"mode": "Remote" if a.status == "Work From Home" else ("—" if a.status == "On Leave" else "Office"),
			"note": "",
		})
	# calendar map for current month
	cal_start = today.replace(day=1)
	cal = {
		getdate(a.attendance_date).day: a.status
		for a in frappe.get_all(
			"Attendance",
			filters={"employee": emp["name"], "attendance_date": [">=", cal_start], "docstatus": 1},
			fields=["attendance_date", "status"],
		)
	}
	summary = _attendance_summary(emp)
	return {
		"employee": emp,
		"logs": logs,
		"calendar": cal,
		"month": today.strftime("%B %Y"),
		"summary": summary,
		"today": today.day,
	}


@frappe.whitelist()
def get_employee_leave():
	emp = _current_employee()
	if not emp:
		return {"employee": None}
	apps = frappe.get_all(
		"Leave Application",
		filters={"employee": emp["name"]},
		fields=["name", "leave_type", "from_date", "to_date", "total_leave_days",
				"status", "leave_approver", "posting_date", "description"],
		order_by="from_date desc",
		limit=50,
	)
	rows = []
	for a in apps:
		rows.append({
			"id": a.name,
			"type": a.leave_type,
			"from": formatdate(a.from_date, "d MMM"),
			"to": formatdate(a.to_date, "d MMM"),
			"days": a.total_leave_days,
			"status": a.status,
			"applied": formatdate(a.posting_date, "d MMM") if a.posting_date else "—",
			"reason": a.description or "—",
		})
	return {
		"employee": emp,
		"requests": rows,
		"balance": _leave_balance(emp),
		"who_is_out": _who_is_out(emp),
	}


@frappe.whitelist()
def get_payslips():
	emp = _current_employee()
	if not emp:
		return {"employee": None, "slips": []}
	slips = frappe.get_all(
		"Salary Slip",
		filters={"employee": emp["name"], "docstatus": 1},
		fields=["name", "start_date", "end_date", "gross_pay", "net_pay", "total_deduction", "status"],
		order_by="end_date desc",
	)
	for s in slips:
		s["month"] = getdate(s.end_date).strftime("%b %Y")
	return {"employee": emp, "slips": slips}


@frappe.whitelist()
def get_payslip_detail(name):
	emp = _current_employee()
	slip = frappe.get_doc("Salary Slip", name)
	if not emp or slip.employee != emp["name"]:
		frappe.throw("Not permitted")
	return {
		"name": slip.name,
		"company": slip.company,
		"month": getdate(slip.end_date).strftime("%B %Y"),
		"posting_date": formatdate(slip.end_date, "dd MMM yyyy"),
		"employee_name": slip.employee_name,
		"designation": frappe.db.get_value("Employee", slip.employee, "designation"),
		"emp_number": frappe.db.get_value("Employee", slip.employee, "employee_number"),
		"payment_days": slip.payment_days,
		"total_working_days": slip.total_working_days,
		"earnings": [{"label": e.salary_component, "amount": e.amount} for e in slip.earnings],
		"deductions": [{"label": e.salary_component, "amount": e.amount} for e in slip.deductions],
		"gross": slip.gross_pay,
		"total_deduction": slip.total_deduction,
		"net": slip.net_pay,
		"net_words": slip.total_in_words,
		"status": "Paid" if slip.docstatus == 1 else "Draft",
	}


@frappe.whitelist()
def get_directory():
	people = frappe.get_all(
		"Employee",
		filters={"status": ["in", ["Active", "On Leave", "Suspended"]]},
		fields=["name", "employee_number", "employee_name", "designation", "department",
				"branch", "reports_to", "company_email", "status", "image"],
		order_by="employee_name asc",
		limit=999,
	)
	name_map = {e.name: e.employee_name for e in frappe.get_all("Employee", fields=["name", "employee_name"], limit=0)}
	for p in people:
		p["location"] = p.get("branch") or "—"
		p["manager_name"] = name_map.get(p.reports_to, "—") if p.get("reports_to") else "—"
	depts = sorted({p["department"] for p in people if p.get("department")})
	return {"people": people, "departments": depts}


@frappe.whitelist()
def get_announcements_feed():
	notes = frappe.get_all(
		"Note", filters={"public": 1},
		fields=["name", "title", "content", "modified", "owner"],
		order_by="modified desc", limit=20,
	)
	out = []
	for n in notes:
		out.append({
			"id": n.name,
			"title": n.title,
			"body": frappe.utils.strip_html(n.content or "").strip(),
			"by": frappe.db.get_value("User", n.owner, "full_name") or n.owner,
			"time": frappe.utils.pretty_date(n.modified),
		})
	return {"posts": out}


@frappe.whitelist()
def get_expense_claims_screen():
	emp = _current_employee()
	if not emp:
		return {"employee": None, "claims": []}
	claims = frappe.get_all(
		"Expense Claim",
		filters={"employee": emp["name"]},
		fields=["name", "posting_date", "total_claimed_amount", "total_sanctioned_amount",
				"approval_status", "status", "docstatus"],
		order_by="posting_date desc",
		limit=50,
	)
	rows = []
	for c in claims:
		first = frappe.db.get_value("Expense Claim Detail", {"parent": c.name}, ["expense_type", "description"], as_dict=True) or {}
		paid = frappe.db.get_value("Expense Claim", c.name, "clearance_date")
		status = "Paid" if paid else (c.approval_status or "Draft")
		rows.append({
			"id": c.name,
			"category": first.get("expense_type") or "—",
			"desc": first.get("description") or "—",
			"date": formatdate(c.posting_date, "dd MMM yyyy"),
			"amount": c.total_claimed_amount,
			"status": status,
		})
	total = sum(c.total_claimed_amount or 0 for c in claims)
	approved = sum(c.total_sanctioned_amount or 0 for c in claims if c.approval_status == "Approved")
	pending = sum(c.total_claimed_amount or 0 for c in claims if (c.approval_status or "Draft") == "Draft")
	return {
		"employee": emp,
		"claims": rows,
		"summary": {"total": total, "approved": approved, "pending": pending,
					"count": len(rows), "pending_count": sum(1 for r in rows if r["status"] == "Draft")},
	}


@frappe.whitelist()
def get_employee_performance():
	emp = _current_employee()
	if not emp:
		return {"employee": None, "goals": []}
	goals, overall, cycle = [], 0, None
	try:
		appr = frappe.get_all(
			"Appraisal",
			filters={"employee": emp["name"]},
			fields=["name", "appraisal_cycle"],
			order_by="creation desc",
			limit=1,
		)
		if appr:
			cycle = appr[0].appraisal_cycle
			rows = frappe.get_all(
				"Appraisal Goal",
				filters={"parent": appr[0].name},
				fields=["kra", "per_weightage", "score"],
			)
			for g in rows:
				# score is 0-5; surface as a 0-100 progress reading
				progress = int(round((g.score or 0) * 20))
				goals.append({"title": g.kra, "weight": g.per_weightage or 0, "progress": progress})
			if goals:
				overall = int(round(sum(x["progress"] * (x["weight"] or 0) for x in goals) / (sum(x["weight"] or 0 for x in goals) or 1)))
	except Exception:
		frappe.clear_last_message()
	return {"employee": emp, "cycle": cycle, "goals": goals, "overall": overall, "feedback": []}


