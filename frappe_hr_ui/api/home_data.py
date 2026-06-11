# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Employee-home data builders — assemble the self-service dashboard payloads."""

import frappe
from frappe.utils import add_days, formatdate, get_datetime, getdate, now_datetime, time_diff_in_seconds

from .base import LEAVE_CODE, LEAVE_COLORS

__all__ = [
	"_today_attendance",
	"_week",
	"_daily_hours_from_checkins",
	"_attendance_summary",
	"_leave_balance",
	"_latest_payslip",
	"_who_is_out",
	"_holidays",
	"_celebrations",
	"_announcements",
	"_tasks",
]


def _today_attendance(employee, shift):
	"""Check-in state for the actual current day."""
	today = getdate()
	logs = frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee["name"], "time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
		fields=["time", "log_type"],
		order_by="time asc",
	)
	# Current state is whatever the LAST punch was — not "any OUT exists today".
	# (The old logic broke on multiple in/out sessions: a morning OUT made the
	# screen read "checked out" even after you punched back IN.)
	checked_in = bool(logs) and logs[-1].log_type == "IN"
	first_in = next((l.time for l in logs if l.log_type == "IN"), None)
	last_out = logs[-1].time if (logs and logs[-1].log_type == "OUT") else None

	# Worked time = sum of each IN→OUT session, plus the open IN→now if on the clock.
	worked_seconds = 0
	open_in = None
	for l in logs:
		if l.log_type == "IN":
			if open_in is None:
				open_in = get_datetime(l.time)
		elif open_in is not None:  # OUT closes the open session
			worked_seconds += max(0, time_diff_in_seconds(get_datetime(l.time), open_in))
			open_in = None
	if open_in is not None:
		worked_seconds += max(0, time_diff_in_seconds(now_datetime(), open_in))

	# shift target minutes (default 9h)
	target_minutes = 540
	if shift.get("start_time") and shift.get("end_time"):
		target_minutes = max(0, int((shift["end_time"] - shift["start_time"]).total_seconds() // 60))

	return {
		"checked_in": checked_in,
		"first_in": get_datetime(first_in).strftime("%H:%M") if first_in else None,
		"last_out": get_datetime(last_out).strftime("%H:%M") if last_out else None,
		"worked_minutes": int(worked_seconds // 60),
		"target_minutes": target_minutes,
	}


def _week(employee):
	"""Mon–Sun strip for the current week."""
	today = getdate()
	monday = add_days(today, -today.weekday())
	att = {
		a.attendance_date: a.status
		for a in frappe.get_all(
			"Attendance",
			filters={
				"employee": employee["name"],
				"attendance_date": ["between", [monday, add_days(monday, 6)]],
				"docstatus": 1,
			},
			fields=["attendance_date", "status"],
		)
	}
	days = []
	for i in range(7):
		d = add_days(monday, i)
		dow = d.weekday()
		if dow >= 5:
			status = "weekoff"
		elif d > today:
			status = "upcoming"
		elif d == today:
			status = "active"
		else:
			st = att.get(d)
			status = "present" if st in ("Present", "Work From Home", "Half Day") else (
				"leave" if st == "On Leave" else ("present" if st else "upcoming")
			)
		days.append({
			"d": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dow],
			"date": d.strftime("%d"),
			"status": status,
		})
	return days


def _daily_hours_from_checkins(employee, start, end):
	"""Average daily worked hours derived from Employee Checkin (first IN -> last OUT)."""
	logs = frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee["name"], "time": ["between", [f"{start} 00:00:00", f"{end} 23:59:59"]]},
		fields=["time", "log_type"], order_by="time asc",
	)
	by_day = {}
	for l in logs:
		by_day.setdefault(get_datetime(l.time).date(), []).append(l)
	hrs = []
	for day in by_day.values():
		ins = [get_datetime(x.time) for x in day if x.log_type == "IN"]
		outs = [get_datetime(x.time) for x in day if x.log_type == "OUT"]
		if ins and outs:
			delta = (max(outs) - min(ins)).total_seconds() / 3600
			if delta > 0:
				hrs.append(delta)
	return hrs


def _attendance_summary(employee):
	today = getdate()
	start = add_days(today, -30)
	rows = frappe.get_all(
		"Attendance",
		filters={"employee": employee["name"], "attendance_date": ["between", [start, today]], "docstatus": 1},
		fields=["status", "working_hours"],
	)
	present = sum(1 for r in rows if r.status in ("Present", "Half Day"))
	wfh = sum(1 for r in rows if r.status == "Work From Home")
	leave = sum(1 for r in rows if r.status == "On Leave")
	hours = [r.working_hours for r in rows if r.working_hours]
	if not hours:
		hours = _daily_hours_from_checkins(employee, start, today)
	avg = sum(hours) / len(hours) if hours else 0
	return {
		"present": present + wfh,
		"wfh": wfh,
		"leave": leave,
		"avg_hours": f"{int(avg)}h {int((avg % 1) * 60):02d}m" if avg else None,
	}


def _leave_balance(employee):
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	details = get_leave_details(employee["name"], getdate())
	alloc = details.get("leave_allocation", {})
	out = []
	for lt, d in alloc.items():
		total = d.get("total_leaves") or 0
		taken = d.get("leaves_taken") or 0
		pending = d.get("leaves_pending_approval") or 0
		out.append({
			"type": lt,
			"code": LEAVE_CODE.get(lt, "".join(w[0] for w in lt.split())[:2].upper()),
			"total": total,
			"used": taken,
			"pending": pending,
			"balance": d.get("remaining_leaves") or 0,
			"color": LEAVE_COLORS.get(lt, "blue"),
		})
	return out


def _latest_payslip(employee):
	slip = frappe.get_all(
		"Salary Slip",
		filters={"employee": employee["name"], "docstatus": 1},
		fields=["name", "start_date", "end_date", "gross_pay", "net_pay", "total_deduction", "status"],
		order_by="end_date desc",
		limit=1,
	)
	if not slip:
		return None
	s = slip[0]
	return {
		"name": s.name,
		"month": getdate(s.end_date).strftime("%b %Y"),
		"net": s.net_pay,
		"gross": s.gross_pay,
		"deductions": s.total_deduction,
		"credited": formatdate(s.end_date, "dd MMM yyyy"),
		"status": "Paid" if s.status == "Submitted" else s.status,
	}


def _who_is_out(employee):
	today = getdate()
	apps = frappe.get_all(
		"Leave Application",
		filters={
			"company": employee.get("company"),
			"status": "Approved",
			"from_date": ["<=", add_days(today, 7)],
			"to_date": [">=", today],
			"docstatus": 1,
		},
		fields=["employee_name", "leave_type", "from_date", "to_date"],
		order_by="from_date asc",
		limit=6,
	)
	out = []
	for a in apps:
		if a.to_date == today:
			until = "Today"
		else:
			until = f"Until {formatdate(a.to_date, 'd MMM')}"
		out.append({"name": a.employee_name, "note": a.leave_type, "until": until})
	return out


def _holidays(employee):
	# resolve via hrms/erpnext's authoritative resolver (employee -> grade -> company)
	from hrms.utils.holiday_list import get_holiday_list_for_employee
	hl = get_holiday_list_for_employee(employee["name"], raise_exception=False) \
		or frappe.db.get_value("Company", employee.get("company"), "default_holiday_list")
	if not hl:
		return []
	today = getdate()
	rows = frappe.get_all(
		"Holiday",
		filters={"parent": hl, "holiday_date": [">=", today], "weekly_off": 0},
		fields=["holiday_date", "description"],
		order_by="holiday_date asc",
		limit=4,
	)
	out = []
	for r in rows:
		d = getdate(r.holiday_date)
		out.append({
			"date": d.strftime("%d"),
			"mon": d.strftime("%b"),
			"day": d.strftime("%A"),
			"name": r.description,
		})
	return out


def _celebrations(employee):
	"""Upcoming work anniversaries among colleagues (real joining dates)."""
	today = getdate()
	rows = frappe.get_all(
		"Employee",
		filters={"status": "Active", "company": employee.get("company")},
		fields=["employee_name", "designation", "department", "date_of_joining"],
		limit=500,
	)
	out = []
	for r in rows:
		if not r.date_of_joining:
			continue
		doj = getdate(r.date_of_joining)
		# next anniversary
		try:
			anniv = doj.replace(year=today.year)
		except ValueError:
			continue
		if anniv < today:
			anniv = anniv.replace(year=today.year + 1)
		delta = (anniv - today).days
		if 0 <= delta <= 14 and anniv.year > doj.year:
			years = anniv.year - doj.year
			label = "Work anniversary today" if delta == 0 else f"{years} years on {formatdate(anniv, 'd MMM')}"
			out.append({"name": r.employee_name, "label": label, "sub": r.department, "_d": delta})
	out.sort(key=lambda x: x["_d"])
	for o in out:
		o.pop("_d", None)
	return out[:4]


def _announcements():
	"""Company announcements sourced from public Notes."""
	notes = frappe.get_all(
		"Note",
		filters={"public": 1},
		fields=["name", "title", "content", "modified", "owner"],
		order_by="modified desc",
		limit=4,
	)
	out = []
	for n in notes:
		content = frappe.utils.strip_html(n.content or "").strip()
		out.append({
			"id": n.name,
			"title": n.title,
			"excerpt": (content[:160] + "…") if len(content) > 160 else content,
			"by": frappe.db.get_value("User", n.owner, "full_name") or n.owner,
			"time": frappe.utils.pretty_date(n.modified),
		})
	return out


def _tasks(employee):
	"""Actionable items derived from real records."""
	out = []
	pending_leaves = frappe.db.count(
		"Leave Application", {"employee": employee["name"], "status": "Open", "docstatus": 0}
	)
	if pending_leaves:
		out.append({
			"title": f"{pending_leaves} leave request{'s' if pending_leaves > 1 else ''} awaiting approval",
			"due": "Submitted", "kind": "calendar", "priority": "medium",
		})
	draft_claims = frappe.db.count(
		"Expense Claim", {"employee": employee["name"], "approval_status": "Draft"}
	)
	if draft_claims:
		out.append({
			"title": f"{draft_claims} expense claim{'s' if draft_claims > 1 else ''} in draft",
			"due": "Not submitted", "kind": "wallet", "priority": "low",
		})
	return out
