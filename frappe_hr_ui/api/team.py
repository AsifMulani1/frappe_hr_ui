# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Manager (team) screens — overview, approvals, attendance, leave, performance, org chart."""

import frappe
from frappe.utils import add_days, formatdate, get_datetime, getdate

from .core import (
	_current_employee,
	_emp,
	_require_manager,
)


def _team(manager):
	return frappe.get_all(
		"Employee",
		filters={"reports_to": manager, "status": ["in", ["Active", "On Leave"]]},
		fields=["name", "employee_number", "employee_name", "designation", "department",
				"branch", "image"],
		order_by="employee_name asc",
	)


def _today_status(emp_name):
	today = getdate()
	on_leave = frappe.db.exists(
		"Leave Application",
		{"employee": emp_name, "status": "Approved", "docstatus": 1,
		 "from_date": ["<=", today], "to_date": [">=", today]},
	)
	if on_leave:
		lt = frappe.db.get_value("Leave Application",
			{"employee": emp_name, "status": "Approved", "from_date": ["<=", today], "to_date": [">=", today]},
			"leave_type")
		return {"att": "On Leave", "in": "—", "note": lt}
	logs = frappe.get_all("Employee Checkin",
		filters={"employee": emp_name, "time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
		fields=["time", "log_type"], order_by="time asc")
	if logs:
		first_in = next((get_datetime(l.time) for l in logs if l.log_type == "IN"), None)
		return {"att": "Present", "in": first_in.strftime("%H:%M") if first_in else "—", "note": None}
	att = frappe.db.get_value("Attendance", {"employee": emp_name, "attendance_date": today, "docstatus": 1}, "status")
	if att == "Work From Home":
		return {"att": "WFH", "in": "—", "note": None}
	if att == "Present":
		return {"att": "Present", "in": "—", "note": None}
	return {"att": "Not in", "in": "—", "note": None}


def _pending_approvals(manager, manager_emp):
	out = []
	leaves = frappe.get_all("Leave Application",
		filters={"status": "Open", "docstatus": 0,
				 "employee": ["in", [t.name for t in _team(manager_emp)] or [""]]},
		fields=["name", "employee_name", "employee", "leave_type", "from_date", "to_date", "total_leave_days", "description"])
	for l in leaves:
		out.append({"id": l.name, "kind": "Leave", "person": l.employee_name, "pid": l.employee,
			"detail": f"{l.leave_type} · {formatdate(l.from_date, 'd MMM')}", "amount": f"{l.total_leave_days} day(s)",
			"sub": l.description or "—", "tone": "info", "icon": "calendar"})
	claims = frappe.get_all("Expense Claim",
		filters={"approval_status": "Draft", "docstatus": 0,
				 "employee": ["in", [t.name for t in _team(manager_emp)] or [""]]},
		fields=["name", "employee_name", "employee", "total_claimed_amount"])
	for c in claims:
		out.append({"id": c.name, "kind": "Expense", "person": c.employee_name, "pid": c.employee,
			"detail": "Expense claim", "amount": frappe.utils.fmt_money(c.total_claimed_amount, currency="INR"),
			"sub": "—", "tone": "accent", "icon": "wallet"})
	return out


@frappe.whitelist()
def get_team_overview():
	_require_manager()
	mgr = _current_employee()
	if not mgr:
		return {"manager": None}
	team = _team(mgr["name"])
	for t in team:
		t["today"] = _today_status(t["name"])
	present = sum(1 for t in team if t["today"]["att"] in ("Present", "WFH"))
	on_leave = sum(1 for t in team if t["today"]["att"] == "On Leave")
	approvals = _pending_approvals(frappe.session.user, mgr["name"])
	# upcoming team leave (next 14 days)
	today = getdate()
	upcoming = frappe.get_all("Leave Application",
		filters={"employee": ["in", [t["name"] for t in team] or [""]], "status": "Approved",
				 "to_date": [">=", today], "from_date": ["<=", add_days(today, 14)], "docstatus": 1},
		fields=["employee_name", "leave_type", "from_date", "to_date"], order_by="from_date asc", limit=6)
	for u in upcoming:
		u["when"] = "Today" if u.to_date == today else f"{formatdate(u.from_date, 'd MMM')}–{formatdate(u.to_date, 'd MMM')}"
	return {
		"manager": mgr,
		"team": team,
		"summary": {"present": present, "total": len(team), "on_leave": on_leave,
					"approvals": len(approvals)},
		"approvals": approvals[:4],
		"upcoming_leave": upcoming,
	}


@frappe.whitelist()
def get_team_approvals():
	_require_manager()
	mgr = _current_employee()
	if not mgr:
		return {"items": []}
	return {"items": _pending_approvals(frappe.session.user, mgr["name"])}


@frappe.whitelist(methods=["POST"])
def act_on_approval(kind, name, action):
	_require_manager()
	if action not in ("approve", "reject"):
		frappe.throw("Invalid action")
	doc = frappe.get_doc("Leave Application" if kind == "Leave" else "Expense Claim", name)
	if kind == "Leave":
		doc.status = "Approved" if action == "approve" else "Rejected"
		doc.save(ignore_permissions=True)
		if action == "approve":
			doc.submit()
	else:
		doc.approval_status = "Approved" if action == "approve" else "Rejected"
		doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_team_attendance():
	_require_manager()
	mgr = _current_employee()
	if not mgr:
		return {"team": []}
	team = _team(mgr["name"])
	today = getdate()
	for i, t in enumerate(team):
		t["today"] = _today_status(t["name"])
		# month present %
		start = today.replace(day=1)
		total = frappe.db.count("Attendance", {"employee": t["name"], "attendance_date": [">=", start], "docstatus": 1})
		present = frappe.db.count("Attendance", {"employee": t["name"], "attendance_date": [">=", start], "status": ["in", ["Present", "Work From Home", "Half Day"]], "docstatus": 1})
		t["rate"] = round(present / total * 100) if total else 100
	present_now = sum(1 for t in team if t["today"]["att"] in ("Present", "WFH"))
	return {"team": team, "summary": {"present": present_now, "total": len(team)}}


@frappe.whitelist()
def get_team_leave():
	_require_manager()
	mgr = _current_employee()
	if not mgr:
		return {"team": [], "leave_map": {}}
	team = _team(mgr["name"])
	today = getdate()
	month_start = today.replace(day=1)
	import calendar as _cal
	ndays = _cal.monthrange(today.year, today.month)[1]
	month_end = today.replace(day=ndays)
	leave_map = {}
	CODE = {"Casual Leave": "CL", "Sick Leave": "SL", "Earned Leave": "EL", "Comp Off": "CO"}
	COLOR = {"CL": "#0289F7", "SL": "#0B9E92", "EL": "#8642C2", "CO": "#DB7706"}
	for t in team:
		apps = frappe.get_all("Leave Application",
			filters={"employee": t["name"], "status": "Approved", "docstatus": 1,
					 "from_date": ["<=", month_end], "to_date": [">=", month_start]},
			fields=["leave_type", "from_date", "to_date"])
		days = []
		code = None
		for a in apps:
			code = CODE.get(a.leave_type, "L")
			s = max(getdate(a.from_date), month_start)
			e = min(getdate(a.to_date), month_end)
			d = s
			while d <= e:
				days.append(d.day)
				d = add_days(d, 1)
		if days:
			leave_map[t["name"]] = {"days": days, "type": code, "color": COLOR.get(code, "#0289F7")}
	return {"team": team, "leave_map": leave_map, "days_in_month": ndays, "today": today.day, "month": today.strftime("%B %Y")}


@frappe.whitelist()
def get_team_performance():
	_require_manager()
	mgr = _current_employee()
	if not mgr:
		return {"team": []}
	team = _team(mgr["name"])
	out = []
	for t in team:
		appr = frappe.get_all("Appraisal", filters={"employee": t["name"]},
			fields=["name", "total_score"], order_by="creation desc", limit=1)
		prog = 0
		rating = None
		if appr:
			rows = frappe.get_all("Appraisal Goal", filters={"parent": appr[0].name}, fields=["per_weightage", "score"])
			tw = sum(r.per_weightage or 0 for r in rows) or 1
			prog = int(round(sum((r.score or 0) * 20 * (r.per_weightage or 0) for r in rows) / tw))
			rating = round(appr[0].total_score, 1) if appr[0].total_score else None
		out.append({"name": t["employee_name"], "designation": t["designation"], "progress": prog, "rating": rating})
	return {"team": out}


@frappe.whitelist()
def get_org_chart():
	mgr = _current_employee()
	if not mgr:
		return {"manager": None, "reports": []}
	return {
		"manager": {"name": mgr["employee_name"], "designation": mgr["designation"]},
		"reports": [{"name": t["employee_name"], "designation": t["designation"]} for t in _team(mgr["name"])],
	}
