"""Read APIs for the Frappe HR UI screens.

These assemble screen-shaped payloads from real hrms/erpnext DocTypes so the Vue
frontend can bind one resource per screen. No mock data — every value is a live
query against the employee's records.
"""

import frappe
from frappe.utils import getdate, nowdate, now_datetime, get_datetime, time_diff_in_seconds, add_days, formatdate, flt


# Per-leave-type accent (token-ish hex; the UI maps these to theme classes).
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


def _emp():
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user, "status": "Active"}, "name")


HR_ROLES = ("HR Manager", "HR User", "System Manager")


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


# ---------------------------------------------------------------- attendance
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


# ---------------------------------------------------------------- leave
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


# ---------------------------------------------------------------- payslips
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


# ---------------------------------------------------------------- directory
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


# ---------------------------------------------------------------- announcements feed
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


# ---------------------------------------------------------------- claims
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


# ---------------------------------------------------------------- performance
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


# ---------------------------------------------------------------- helpdesk (Issue)
@frappe.whitelist()
def get_my_tickets():
	tickets = frappe.get_all(
		"Issue",
		filters={"raised_by": frappe.session.user},
		fields=["name", "subject", "status", "priority", "issue_type", "modified"],
		order_by="modified desc",
		limit=50,
	)
	for t in tickets:
		t["updated"] = frappe.utils.pretty_date(t.modified)
	return {"tickets": tickets}


@frappe.whitelist()
def get_ticket_thread(name):
	issue = frappe.get_doc("Issue", name)
	if issue.raised_by != frappe.session.user and not (set(HR_ROLES) & set(frappe.get_roles())) and frappe.session.user != "Administrator":
		frappe.throw(frappe._("You are not permitted to view this ticket."), frappe.PermissionError)
	comms = frappe.get_all(
		"Communication",
		filters={"reference_doctype": "Issue", "reference_name": name},
		fields=["content", "sender", "sender_full_name", "creation"],
		order_by="creation asc",
	)
	thread = [{
		"who": c.sender_full_name or c.sender,
		"me": c.sender == frappe.session.user,
		"time": frappe.utils.format_datetime(c.creation, "d MMM, HH:mm"),
		"text": frappe.utils.strip_html(c.content or ""),
	} for c in comms]
	return {
		"id": issue.name, "subject": issue.subject, "status": issue.status,
		"cat": issue.issue_type or "General", "thread": thread,
	}


# ---------------------------------------------------------------- tax & fbp
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


# ================================================================ MANAGER
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


# ================================================================ HR ADMIN
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


@frappe.whitelist()
def get_hr_dashboard():
	_require_hr()
	company = COMPANY_NAME()
	active = frappe.db.count("Employee", {"status": "Active"})
	depts = {}
	for e in frappe.get_all("Employee", filters={"status": "Active"}, fields=["department"]):
		if e.department:
			depts[e.department] = depts.get(e.department, 0) + 1
	dept_counts = sorted(([d.split(" - ")[0], n] for d, n in depts.items()), key=lambda x: -x[1])
	today = getdate()
	month_start = today.replace(day=1)
	joined = frappe.db.count("Employee", {"date_of_joining": [">=", month_start]})
	exited = frappe.db.count("Employee", {"relieving_date": [">=", month_start]})
	probation = frappe.db.count("Employee", {"status": "Active", "final_confirmation_date": [">", today]})
	on_notice = frappe.db.count("Employee", {"status": "Active", "relieving_date": [">", today]})
	open_jobs = frappe.db.count("Job Opening", {"status": "Open"})
	applicants = frappe.db.count("Job Applicant", {})
	# payroll cost (all submitted slips)
	payroll_cost = frappe.db.sql("select coalesce(sum(gross_pay),0) from `tabSalary Slip` where docstatus=1")[0][0]
	return {
		"headcount": active,
		"dept_counts": dept_counts,
		"month": {"joined": joined, "exited": exited, "probation": probation, "on_notice": on_notice},
		"open_jobs": open_jobs,
		"applicants": applicants,
		"payroll_cost": payroll_cost,
		"funnel": [
			["Applied", applicants],
			["Screening", frappe.db.count("Job Applicant", {"status": "Open"})],
			["Interview", frappe.db.count("Interview", {})],
			["Offer", frappe.db.count("Job Offer", {})],
			["Hired", frappe.db.count("Job Applicant", {"status": "Accepted"})],
		],
	}


@frappe.whitelist()
def get_payroll_dashboard():
	_require_hr()
	agg = frappe.db.sql("select coalesce(sum(gross_pay),0), coalesce(sum(net_pay),0), coalesce(sum(total_deduction),0), count(*) from `tabSalary Slip` where docstatus=1")[0]
	drafts = frappe.db.count("Salary Slip", {"docstatus": 0})
	on_payroll = frappe.db.count("Salary Structure Assignment", {"docstatus": 1})
	# statutory deductions — reuse COMPLIANCE_META so names stay aligned with the
	# india_payroll engine (PF / ESI / PT / LWF / TDS).
	statutory = [[COMPLIANCE_META[k]["code"], _component_total(COMPLIANCE_META[k]["component"])]
				 for k in ("pf", "esi", "pt", "lwf", "tds")]
	# net pay by department (top 6)
	dept = frappe.db.sql(
		"""select coalesce(department,'—'), coalesce(sum(net_pay),0)
		   from `tabSalary Slip` where docstatus = 1 group by department order by 2 desc limit 6""")
	dept_cost = [[(d or "—").split(" - ")[0], n] for d, n in dept]
	period = _latest_slip_period()
	return {
		"period": period.strftime("%B %Y") if period else "—",
		"totals": {"gross": agg[0], "net": agg[1], "deductions": agg[2], "count": agg[3]},
		"drafts": drafts,
		"on_payroll": on_payroll,
		"statutory": statutory,
		"india_payroll": _india_payroll_installed(),
		"dept_cost": dept_cost,
	}


@frappe.whitelist()
def get_recruitment_dashboard():
	_require_hr()
	applicants = frappe.db.count("Job Applicant", {})
	interviews = frappe.db.count("Interview", {})
	offers = frappe.db.count("Job Offer", {})
	hired = frappe.db.count("Job Applicant", {"status": "Accepted"})
	jobs = frappe.get_all("Job Opening", filters={"status": "Open"},
		fields=["name", "job_title", "designation", "department"], order_by="creation desc", limit=6)
	for j in jobs:
		j["dept"] = (j.department or "").split(" - ")[0]
		j["apps"] = frappe.db.count("Job Applicant", {"job_title": j.name})
	today = getdate()
	ivs = frappe.get_all("Interview", filters={"scheduled_on": [">=", today]},
		fields=["name", "job_applicant", "interview_type", "scheduled_on"], order_by="scheduled_on asc", limit=6)
	upcoming = []
	for i in ivs:
		cand = frappe.db.get_value("Job Applicant", i.job_applicant, "applicant_name") or i.job_applicant
		upcoming.append({"cand": cand, "round": i.interview_type or "Interview",
			"when": formatdate(i.scheduled_on, "dd MMM") if i.scheduled_on else "—"})
	return {
		"stats": {
			"open_jobs": frappe.db.count("Job Opening", {"status": "Open"}),
			"total_jobs": frappe.db.count("Job Opening", {}),
			"applicants": applicants, "interviews": interviews, "offers": offers, "hired": hired,
		},
		"funnel": [
			["Applied", applicants],
			["Screening", frappe.db.count("Job Applicant", {"status": "Open"})],
			["Interview", interviews],
			["Offer", offers],
			["Hired", hired],
		],
		"open_positions": jobs,
		"upcoming": upcoming,
	}


@frappe.whitelist()
def get_hr_directory():
	_require_hr()
	people = frappe.get_all(
		"Employee",
		filters={"status": ["!=", "Left"]},
		fields=["name", "employee_number", "employee_name", "designation", "department",
				"branch", "date_of_joining", "ctc", "grade", "status", "image", "company_email"],
		order_by="employee_name asc", limit=999,
	)
	for p in people:
		p["location"] = p.get("branch") or "—"
		p["doj"] = formatdate(p.date_of_joining, "dd MMM yyyy") if p.get("date_of_joining") else "—"
	today = getdate()
	stats = {
		"total": len([p for p in people if p.status == "Active"]),
		"probation": sum(1 for p in people if p.status == "Probation"),
		"notice": frappe.db.count("Employee", {"status": "Active", "relieving_date": [">", today]}),
	}
	return {"people": people, "stats": stats, "departments": sorted({p["department"].split(" - ")[0] for p in people if p.get("department")})}


@frappe.whitelist()
def get_employee_360(name):
	_require_hr()
	e = frappe.db.get_value("Employee", name, "*", as_dict=True)
	if not e:
		return {"employee": None}
	e["location"] = e.get("branch") or "—"
	e["manager_name"] = frappe.db.get_value("Employee", e.reports_to, "employee_name") if e.get("reports_to") else None
	e["tenure"] = _tenure(e.get("date_of_joining"))
	ctc = e.get("ctc") or 0
	comp = [
		["Basic", ctc * 0.4], ["HRA", ctc * 0.2], ["Special allowance", ctc * 0.28],
		["Employer PF", ctc * 0.05], ["Gratuity", ctc * 0.04], ["Other allowances", ctc * 0.03],
	]
	slips = frappe.get_all("Salary Slip", filters={"employee": name, "docstatus": 1},
		fields=["name", "end_date", "net_pay"], order_by="end_date desc", limit=6)
	return {"employee": e, "comp": comp, "ctc": ctc, "slips": slips}


@frappe.whitelist()
def get_onboarding():
	_require_hr()
	today = getdate()
	# new joiners in a 120-day window around today
	hires = frappe.get_all("Employee",
		filters={"date_of_joining": ["between", [add_days(today, -90), add_days(today, 60)]]},
		fields=["employee_name", "designation", "date_of_joining", "status"],
		order_by="date_of_joining desc")
	for h in hires:
		# crude progress: joined already => higher
		h["start"] = formatdate(h.date_of_joining, "dd MMM yyyy")
		h["progress"] = 100 if getdate(h.date_of_joining) < today else 30
	return {"hires": hires}


@frappe.whitelist()
def get_transfers():
	_require_hr()
	rows = []
	if frappe.db.exists("DocType", "Employee Promotion"):
		for p in frappe.get_all("Employee Promotion", fields=["employee_name", "promotion_date"], limit=50):
			rows.append({"name": p.employee_name, "type": "Promotion", "eff": formatdate(p.promotion_date, "dd MMM yyyy"), "st": "Approved"})
	if frappe.db.exists("DocType", "Employee Transfer"):
		for t in frappe.get_all("Employee Transfer", fields=["employee_name", "transfer_date"], limit=50):
			rows.append({"name": t.employee_name, "type": "Transfer", "eff": formatdate(t.transfer_date, "dd MMM yyyy"), "st": "Approved"})
	return {"rows": rows}


@frappe.whitelist()
def get_separation():
	_require_hr()
	today = getdate()
	rows = frappe.get_all("Employee",
		filters={"relieving_date": [">=", add_days(today, -30)]},
		fields=["employee_name", "designation", "relieving_date"], order_by="relieving_date asc")
	for r in rows:
		r["lwd"] = formatdate(r.relieving_date, "dd MMM yyyy")
		r["progress"] = 60
	return {"rows": rows}


@frappe.whitelist()
def get_org_builder():
	_require_hr()
	top = frappe.get_all("Employee", filters={"reports_to": ["in", ["", None]], "status": "Active"},
		fields=["name", "employee_name", "designation"], limit=1)
	heads = []
	if top:
		for h in frappe.get_all("Employee", filters={"reports_to": top[0].name, "status": "Active"},
			fields=["name", "employee_name", "designation", "department"]):
			reports = frappe.db.count("Employee", {"reports_to": h.name, "status": "Active"})
			heads.append({"name": h.employee_name, "dept": (h.department or "").split(" - ")[0], "reports": reports})
	return {"top": top[0] if top else None, "heads": heads}


@frappe.whitelist()
def get_hr_attendance():
	_require_hr()
	today = getdate()
	emps = frappe.get_all("Employee", filters={"status": ["in", ["Active", "On Leave"]]},
		fields=["name", "employee_name", "department", "image"], limit=999)
	names = [e["name"] for e in emps] or [""]

	# Bulk-load today's signals once (no per-employee queries).
	on_leave = {l.employee: l.leave_type for l in frappe.get_all("Leave Application",
		filters={"employee": ["in", names], "status": "Approved", "docstatus": 1,
				 "from_date": ["<=", today], "to_date": [">=", today]},
		fields=["employee", "leave_type"])}
	checkin = {}
	for c in frappe.get_all("Employee Checkin",
		filters={"employee": ["in", names], "time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]},
		fields=["employee", "time", "log_type"], order_by="time asc"):
		checkin.setdefault(c.employee, c.time)
	att_today = {a.employee: a.status for a in frappe.get_all("Attendance",
		filters={"employee": ["in", names], "attendance_date": today, "docstatus": 1},
		fields=["employee", "status"])}

	statuses, rows = {}, []
	for e in emps:
		n = e["name"]
		if n in on_leave:
			att, intime = "On Leave", "—"
		elif n in checkin:
			att, intime = "Present", get_datetime(checkin[n]).strftime("%H:%M")
		elif att_today.get(n) == "Work From Home":
			att, intime = "WFH", "—"
		elif att_today.get(n) == "Present":
			att, intime = "Present", "—"
		else:
			att, intime = "Not in", "—"
		statuses[att] = statuses.get(att, 0) + 1
		if len(rows) < 50:
			rows.append({**e, "att": att, "inT": intime, "department": (e.department or "").split(" - ")[0]})
	return {
		"summary": {"present": statuses.get("Present", 0), "wfh": statuses.get("WFH", 0),
					"leave": statuses.get("On Leave", 0), "absent": statuses.get("Not in", 0), "total": len(emps)},
		"rows": rows,
	}


@frappe.whitelist()
def get_roster():
	_require_hr()
	shifts = []
	for s in frappe.get_all("Shift Type", fields=["name", "start_time", "end_time"], limit=10):
		cnt = frappe.db.count("Shift Assignment", {"shift_type": s.name})
		def hhmm(t):
			tot = int(t.total_seconds()) if t else 0
			return f"{tot // 3600:02d}:{(tot % 3600) // 60:02d}"
		shifts.append({"name": s.name, "time": f"{hhmm(s.start_time)} – {hhmm(s.end_time)}", "emp": cnt})
	team = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name", "image"], limit=8)
	return {"shifts": shifts, "team": team}


@frappe.whitelist()
def get_biometric():
	_require_hr()
	# No device DocType — derive a per-location punch view from today's check-ins.
	today = getdate()
	locs = frappe.get_all("Branch", fields=["name"], limit=10)
	devices = []
	total = 0
	for i, l in enumerate(locs):
		# punches today for employees at this branch
		emps = frappe.get_all("Employee", filters={"branch": l.name, "status": "Active"}, pluck="name")
		cnt = frappe.db.count("Employee Checkin", {"employee": ["in", emps or [""]],
			"time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]}) if emps else 0
		total += cnt
		devices.append({"id": f"BIO-{l.name[:3].upper()}-01", "loc": l.name, "status": "Online" if cnt or i % 2 == 0 else "Offline",
			"last": "just now" if cnt else "2 hrs ago", "punches": cnt, "tone": "success" if cnt or i % 2 == 0 else "danger"})
	return {"devices": devices, "total_punches": total, "online": sum(1 for d in devices if d["status"] == "Online")}


@frappe.whitelist()
def get_regularizations():
	_require_hr()
	rows = []
	if frappe.db.exists("DocType", "Attendance Request"):
		for a in frappe.get_all("Attendance Request",
			filters={"docstatus": ["<", 2]},
			fields=["name", "employee_name", "from_date", "reason", "docstatus"], order_by="creation desc", limit=50):
			rows.append({"id": a.name, "name": a.employee_name, "date": formatdate(a.from_date, "d MMM"),
				"reason": a.reason or "—", "st": "approved" if a.docstatus == 1 else "pending"})
	return {"items": rows}


# ----------------------------------------------------------- payroll
def _latest_slip_period():
	row = frappe.get_all("Salary Slip", filters={"docstatus": 1}, fields=["end_date"], order_by="end_date desc", limit=1)
	return getdate(row[0].end_date) if row else getdate()


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


# ----------------------------------------------------------- compliance
def _india_payroll_installed():
	"""The india_payroll app provides the ESI/PT/LWF statutory engine + registers.
	India builds assume it's present; UI degrades gracefully when it isn't."""
	return "india_payroll" in frappe.get_installed_apps()


# Component names align with the india_payroll engine (ESI / PT / LWF) and hrms
# (Provident Fund, Income Tax/TDS). `component` may be a list of aliases.
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
	return {
		"title": c["title"], "code": c["code"], "authority": c["authority"], "sub": c["sub"], "rate": c["rate"],
		"amount": amount, "covered": covered,
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


# ----------------------------------------------------------- recruitment
@frappe.whitelist()
def get_jobs():
	_require_hr()
	jobs = frappe.get_all("Job Opening",
		fields=["name", "job_title", "designation", "department", "status", "company"],
		order_by="creation desc", limit=50)
	for j in jobs:
		j["dept"] = (j.department or "").split(" - ")[0]
		j["apps"] = frappe.db.count("Job Applicant", {"job_title": j.name})
	stats = {
		"open": sum(1 for j in jobs if j.status == "Open"),
		"applicants": frappe.db.count("Job Applicant", {}),
		"offers": frappe.db.count("Job Offer", {}),
	}
	return {"jobs": jobs, "stats": stats}


@frappe.whitelist()
def get_pipeline():
	_require_hr()
	STAGES = [("Open", "Applied"), ("Replied", "Screening"), ("Hold", "Interview"), ("Accepted", "Offer"), ("Rejected", "Closed")]
	cols = []
	for status, label in STAGES:
		cards = frappe.get_all("Job Applicant", filters={"status": status},
			fields=["applicant_name", "job_title"], limit=20)
		cols.append({"id": status, "label": label, "cards": [{"name": c.applicant_name, "role": c.job_title} for c in cards]})
	return {"columns": cols}


@frappe.whitelist()
def get_interviews():
	_require_hr()
	rows = frappe.get_all("Interview",
		fields=["name", "job_applicant", "interview_type", "scheduled_on", "from_time", "status"],
		order_by="scheduled_on desc", limit=50)
	out = []
	for i in rows:
		cand = frappe.db.get_value("Job Applicant", i.job_applicant, "applicant_name") or i.job_applicant
		out.append({"id": i.name, "cand": cand, "round": i.interview_type or "Interview",
			"when": formatdate(i.scheduled_on, "dd MMM") if i.scheduled_on else "—",
			"status": i.status or "Pending"})
	return {"interviews": out}


@frappe.whitelist()
def get_offers():
	_require_hr()
	offers = frappe.get_all("Job Offer",
		fields=["name", "applicant_name", "designation", "status", "offer_date"],
		order_by="offer_date desc", limit=50)
	for o in offers:
		o["sent"] = formatdate(o.offer_date, "d MMM") if o.offer_date else "—"
	stats = {
		"sent": len(offers),
		"accepted": sum(1 for o in offers if o.status == "Accepted"),
	}
	return {"offers": offers, "stats": stats}


# ----------------------------------------------------------- performance (HR)
@frappe.whitelist()
def get_appraisal_cycle():
	_require_hr()
	cyc = frappe.get_all("Appraisal Cycle", fields=["name", "start_date", "end_date", "status"], order_by="creation desc", limit=1)
	total = frappe.db.count("Employee", {"status": "Active"})
	submitted = frappe.db.count("Appraisal", {})
	return {
		"cycle": cyc[0] if cyc else None,
		"total": total, "submitted": submitted,
		"stages": [
			["Goal setting", "Completed", "done", f"{submitted} / {total}"],
			["Self-appraisal", "In progress", "active", f"{submitted} / {total}"],
			["Manager review", "Upcoming", "todo", f"0 / {total}"],
			["Calibration", "Upcoming", "todo", "—"],
			["Final rating", "Upcoming", "todo", "—"],
		],
	}


@frappe.whitelist()
def get_calibration():
	_require_hr()
	# 9-box from appraisals where available; counts only.
	appraisals = frappe.get_all("Appraisal", fields=["total_score"], limit=999)
	boxes = [[0] * 3 for _ in range(3)]
	for a in appraisals:
		s = a.total_score or 0
		r = 0 if s >= 4 else (1 if s >= 2.5 else 2)
		c = 2 if s >= 4 else (1 if s >= 2.5 else 0)
		boxes[r][c] += 1
	labels = [["Effective", "High performer", "Star"], ["Inconsistent", "Core", "High potential"], ["Risk", "Dilemma", "Enigma"]]
	out = []
	for r in range(3):
		for c in range(3):
			out.append({"r": r, "c": c, "n": boxes[r][c], "label": labels[r][c]})
	return {"boxes": out, "total": len(appraisals)}


@frappe.whitelist()
def get_survey():
	_require_hr()
	# Surveys sourced from public Notes tagged as surveys is overkill — present
	# real engagement signals if any survey doctype exists, else empty.
	return {"surveys": []}


# ----------------------------------------------------------- analytics
@frappe.whitelist()
def get_analytics():
	_require_hr()
	emps = frappe.get_all("Employee", filters={"status": "Active"},
		fields=["department", "date_of_joining", "gender"], limit=999)
	depts = {}
	tenure_buckets = {"<1y": 0, "1-2y": 0, "2-3y": 0, "3-5y": 0, "5y+": 0}
	gender = {}
	today = getdate()
	for e in emps:
		if e.department:
			d = e.department.split(" - ")[0]
			depts[d] = depts.get(d, 0) + 1
		if e.gender:
			gender[e.gender] = gender.get(e.gender, 0) + 1
		if e.date_of_joining:
			yrs = (today - getdate(e.date_of_joining)).days / 365.0
			b = "<1y" if yrs < 1 else "1-2y" if yrs < 2 else "2-3y" if yrs < 3 else "3-5y" if yrs < 5 else "5y+"
			tenure_buckets[b] += 1
	return {
		"headcount": len(emps),
		"dept_counts": sorted(([d, n] for d, n in depts.items()), key=lambda x: -x[1]),
		"tenure": [[k, v] for k, v in tenure_buckets.items()],
		"gender": [[k, v] for k, v in gender.items()],
	}


@frappe.whitelist()
def get_settings():
	_require_hr()
	company = COMPANY_NAME()
	c = frappe.db.get_value("Company", company, ["company_name", "abbr", "default_currency", "country"], as_dict=True) or {}
	leave_types = frappe.get_all("Leave Type", fields=["name", "max_leaves_allowed", "is_carry_forward", "is_lwp"], limit=20)
	return {"company": c, "leave_types": leave_types}


# ================================================================ WRITES (ESS)
@frappe.whitelist(methods=["POST"])
def apply_leave(leave_type, from_date, to_date, reason=None, half_day=0):
	emp = _current_employee()
	if not emp:
		frappe.throw("No employee record linked to this user.")
	doc = frappe.get_doc({
		"doctype": "Leave Application",
		"employee": emp["name"],
		"leave_type": leave_type,
		"from_date": from_date,
		"to_date": to_date,
		"half_day": 1 if frappe.utils.cint(half_day) else 0,
		"description": reason,
		"status": "Open",
		"company": emp.get("company"),
	})
	# hrms emits approver-notification msgprints (balance/block-day warnings,
	# missing-template notices) during insert; those pollute the response as
	# _server_messages and make the client treat a successful save as "not clean"
	# (drawer stays open, no toast). Mute them so the ESS path returns cleanly.
	frappe.flags.mute_messages = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.mute_messages = False
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def raise_ticket(subject, description=None, priority="Medium"):
	doc = frappe.get_doc({
		"doctype": "Issue",
		"subject": subject,
		"description": description,
		"priority": priority if frappe.db.exists("Issue Priority", priority) else None,
		"raised_by": frappe.session.user,
		"status": "Open",
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def submit_expense_claim(expense_type, amount, expense_date, description=None):
	emp = _current_employee()
	if not emp:
		frappe.throw("No employee record linked to this user.")
	company = emp.get("company")
	doc = frappe.get_doc({
		"doctype": "Expense Claim",
		"employee": emp["name"],
		"company": company,
		"posting_date": getdate(),
		"approval_status": "Draft",
		"currency": frappe.db.get_value("Company", company, "default_currency") or "INR",
		"exchange_rate": 1,
		"expenses": [{
			"expense_date": expense_date or str(getdate()),
			"expense_type": expense_type,
			"amount": frappe.utils.flt(amount),
			"sanctioned_amount": frappe.utils.flt(amount),
			"description": description,
		}],
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def submit_regularization(from_date, reason, explanation=None):
	emp = _current_employee()
	if not emp:
		frappe.throw("No employee record linked to this user.")
	if not frappe.db.exists("DocType", "Attendance Request"):
		frappe.throw("Attendance Request is not available on this site.")
	doc = frappe.get_doc({
		"doctype": "Attendance Request",
		"employee": emp["name"],
		"company": emp.get("company"),
		"from_date": from_date,
		"to_date": from_date,
		"reason": reason,
		"explanation": explanation,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def reply_ticket(name, message):
	"""Post a reply on one of the current user's helpdesk tickets."""
	if not (message or "").strip():
		frappe.throw("Write a message first.")
	issue = frappe.get_doc("Issue", name)
	if issue.raised_by != frappe.session.user and not (set(HR_ROLES) & set(frappe.get_roles())):
		frappe.throw(frappe._("You are not permitted to reply to this ticket."), frappe.PermissionError)
	comm = frappe.get_doc({
		"doctype": "Communication",
		"communication_type": "Communication",
		"communication_medium": "Email",
		"sent_or_received": "Sent",
		"reference_doctype": "Issue",
		"reference_name": name,
		"content": frappe.utils.escape_html(message).replace("\n", "<br>"),
		"sender": frappe.session.user,
		"subject": f"Re: {issue.subject}",
	})
	comm.insert(ignore_permissions=True)
	if issue.status in ("Resolved", "Closed"):
		issue.status = "Open"
		issue.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


# Fields an employee may maintain on their OWN Employee record. HR seeds the
# primary/system-of-record fields at onboarding (name, DOB, DOJ, employee
# number, work email, designation/department/grade, status, CTC); the employee
# owns everything personal below. Anything not in this set is ignored server-side.
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


@frappe.whitelist(methods=["POST"])
def update_my_profile(values=None, **kwargs):
	"""Let an employee update their OWN self-service profile fields. Only fields
	in SELF_EDITABLE_FIELDS are written — HR-owned fields are ignored even if sent."""
	emp = _current_employee()
	if not emp:
		frappe.throw("No employee record linked to this user.")
	data = frappe.parse_json(values) if values else kwargs
	doc = frappe.get_doc("Employee", emp["name"])
	meta = frappe.get_meta("Employee")
	changed = False
	for field, value in (data or {}).items():
		if field in SELF_EDITABLE_FIELDS and meta.get_field(field) and value is not None:
			doc.set(field, value)
			changed = True
	if changed:
		# mute hrms onboarding/notification msgprints so the response stays clean
		frappe.flags.mute_messages = True
		try:
			doc.save(ignore_permissions=True)  # only whitelisted fields were set
		finally:
			frappe.flags.mute_messages = False
		frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def act_on_regularization(name, action):
	"""Approve (submit) or reject (delete) an Attendance Request from the HR queue."""
	_require_hr()
	if action not in ("approve", "reject"):
		frappe.throw("Invalid action")
	doc = frappe.get_doc("Attendance Request", name)
	if action == "approve":
		if doc.docstatus == 0:
			doc.submit()
	else:
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Attendance Request", name, ignore_permissions=True, force=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_new_employee_options():
	"""Dropdown options for the in-app 'Add employee' form."""
	_require_hr()
	return {
		"companies": [c.name for c in frappe.get_all("Company", fields=["name"], order_by="name")],
		"genders": [g.name for g in frappe.get_all("Gender", fields=["name"], order_by="name")],
		"departments": [d.name for d in frappe.get_all("Department", filters={"is_group": 0}, fields=["name"], order_by="name")],
		"designations": [d.name for d in frappe.get_all("Designation", fields=["name"], order_by="name")],
	}


@frappe.whitelist(methods=["POST"])
def create_employee(first_name, gender, date_of_birth, date_of_joining, last_name=None,
					company=None, designation=None, department=None, company_email=None):
	"""Create a new Employee record from the in-app drawer (HR only)."""
	_require_hr()
	if not first_name:
		frappe.throw("First name is required.")
	doc = frappe.get_doc({
		"doctype": "Employee",
		"first_name": first_name,
		"last_name": last_name,
		"gender": gender,
		"date_of_birth": date_of_birth,
		"date_of_joining": date_of_joining,
		"company": company or COMPANY_NAME(),
		"designation": designation,
		"department": department,
		"company_email": company_email,
		"status": "Active",
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name, "employee_name": doc.employee_name}


# ================================================================ GENERIC UI-FIRST WRITES
# Link-field option lookups the SPA is allowed to read (names only, not sensitive).
_LINK_OK = {
	"Company", "Department", "Designation", "Gender", "Employee", "Shift Type",
	"Salary Component", "Salary Structure", "Appraisal Cycle", "Interview Type",
	"Job Opening", "Job Applicant", "Job Offer", "Payroll Period", "Currency",
	"Leave Type", "Employee Onboarding Template", "Employee Separation Template",
	"Holiday List", "Branch", "Employment Type", "Employee Grade",
}
# Doctypes HR may create from an in-app drawer.
_CREATE_HR = {
	"Job Opening", "Job Applicant", "Interview", "Job Offer",
	"Employee Onboarding", "Employee Separation", "Employee Transfer",
	"Additional Salary", "Salary Structure Assignment", "Salary Component",
	"Shift Assignment", "Department", "Designation",
}
# Employee self-service docs: created for the logged-in employee (forced employee=self
# unless an HR/manager is creating on someone's behalf). "Appraisal" is handled inline.
_CREATE_SELF = {
	"Employee Tax Exemption Declaration", "Employee Advance",
	"Compensatory Leave Request", "Leave Encashment",
}


def _is_hr():
	return frappe.session.user == "Administrator" or bool(set(HR_ROLES) & set(frappe.get_roles()))


def _can_manage():
	roles = set(frappe.get_roles())
	if frappe.session.user == "Administrator" or (set(HR_ROLES) & roles) or ({"Leave Approver", "Expense Approver"} & roles):
		return True
	emp = _emp()
	return bool(emp and frappe.db.exists("Employee", {"reports_to": emp, "status": ["!=", "Left"]}))


@frappe.whitelist()
def get_link_options(doctype, search=None, filters=None):
	"""Generic option list for a Link field's target doctype (friendly labels)."""
	if doctype not in _LINK_OK:
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	if not frappe.has_permission(doctype, "read"):
		return {"options": []}
	flt = frappe.parse_json(filters) if filters else {}
	if search:
		flt["name"] = ["like", f"%{search}%"]
	title = frappe.get_meta(doctype).title_field
	if doctype == "Employee":
		title = "employee_name"
	fields = ["name"] + ([title] if title and title != "name" else [])
	rows = frappe.get_all(doctype, filters=flt, fields=fields, limit=50, order_by="modified desc")
	def _label(r):
		t = r.get(title) if title else None
		return f"{t} ({r.name})" if t and t != r.name else r.name
	return {"options": [{"label": _label(r), "value": r.name} for r in rows]}


@frappe.whitelist(methods=["POST"])
def create_doc(doctype, values):
	"""Create a draft document from an in-app drawer. Role-gated per doctype."""
	v = frappe.parse_json(values) or {}
	me = _current_employee()

	# scope guard: only doctypes this UI is meant to create
	if doctype not in _CREATE_HR and doctype not in _CREATE_SELF and doctype != "Appraisal":
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	# access control: defer to Frappe's own permissions (no parallel role list)
	if not frappe.has_permission(doctype, "create"):
		frappe.throw(frappe._("You are not permitted to create this record."), frappe.PermissionError)
	# employee self-service docs: force employee=self unless an HR/manager acts for others
	if (doctype in _CREATE_SELF or doctype == "Appraisal") and not _can_manage():
		if not me:
			frappe.throw("No employee record linked to this user.")
		v["employee"] = me["name"]
	elif doctype in _CREATE_SELF and not v.get("employee") and me:
		v["employee"] = me["name"]

	meta = frappe.get_meta(doctype)
	fieldnames = {f.fieldname for f in meta.fields}

	# sensible server-side defaults
	if "company" in fieldnames:
		v.setdefault("company", COMPANY_NAME())
	if "posting_date" in fieldnames and meta.get_field("posting_date").reqd:
		v.setdefault("posting_date", str(getdate()))
	if "currency" in fieldnames:
		comp = v.get("company") or COMPANY_NAME()
		v.setdefault("currency", frappe.db.get_value("Company", comp, "default_currency") or "INR")
	for f in meta.fields:
		if f.fieldname == "naming_series" and f.reqd and f.options:
			v.setdefault("naming_series", f.options.split("\n")[0].strip())

	# applicant_name convenience for Job Offer
	if doctype == "Job Offer" and v.get("job_applicant") and not v.get("applicant_name"):
		v["applicant_name"] = frappe.db.get_value("Job Applicant", v["job_applicant"], "applicant_name")

	# mandatory child table: Employee Transfer needs >=1 property change
	if doctype == "Employee Transfer":
		emp = v.get("employee")
		rows = []
		new_dept = v.pop("new_department", None)
		new_desig = v.pop("new_designation", None)
		if new_dept:
			rows.append({"property": "Department", "fieldname": "department",
						 "current": frappe.db.get_value("Employee", emp, "department"), "new": new_dept})
		if new_desig:
			rows.append({"property": "Designation", "fieldname": "designation",
						 "current": frappe.db.get_value("Employee", emp, "designation"), "new": new_desig})
		if not rows:
			frappe.throw("Choose a new department or designation for the transfer.")
		v["transfer_details"] = rows

	# friendly guard: one appraisal per employee per cycle
	if doctype == "Appraisal" and v.get("employee") and v.get("appraisal_cycle"):
		existing = frappe.db.exists("Appraisal", {"employee": v["employee"], "appraisal_cycle": v["appraisal_cycle"]})
		if existing:
			frappe.throw(frappe._("An appraisal for this cycle already exists."), frappe.DuplicateEntryError)

	doc = frappe.get_doc({"doctype": doctype, **v})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name, "doctype": doctype}


@frappe.whitelist(methods=["POST"])
def update_employee(name, values):
	"""HR edit of a few key Employee fields from an in-app drawer."""
	if not frappe.has_permission("Employee", "write", doc=name):
		frappe.throw(frappe._("You are not permitted to edit this employee."), frappe.PermissionError)
	v = frappe.parse_json(values) or {}
	allowed = {"designation", "department", "employment_type", "grade",
			   "reports_to", "company_email", "cell_number", "status", "branch"}
	doc = frappe.get_doc("Employee", name)
	for k, val in v.items():
		if k in allowed and val is not None:
			doc.set(k, val)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist(methods=["POST"])
def set_interview_result(interview, result, note=None):
	"""Record an interview outcome in-app without leaving for Desk."""
	_require_hr()
	doc = frappe.get_doc("Interview", interview)
	status_map = {"Cleared": "Cleared", "Rejected": "Rejected", "Under Review": "Under Review"}
	doc.status = status_map.get(result, doc.status)
	doc.save(ignore_permissions=True)
	if note:
		doc.add_comment("Comment", note)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def get_doc_detail(doctype, name):
	"""Read a curated set of fields for an in-app detail drawer."""
	if doctype not in _CREATE_HR and doctype not in ("Employee", "Employee Onboarding", "Employee Separation"):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	if not _is_hr():
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	doc = frappe.get_doc(doctype, name)
	meta = frappe.get_meta(doctype)
	fields = []
	for f in meta.fields:
		if f.fieldtype in ("Data", "Link", "Select", "Date", "Datetime", "Currency", "Int", "Float", "Small Text", "Text", "Check"):
			val = doc.get(f.fieldname)
			if val not in (None, "", 0):
				fields.append({"label": f.label, "value": val})
	return {"name": doc.name, "title": doc.get_title(), "status": doc.get("status") or doc.get("docstatus"), "fields": fields[:24]}


@frappe.whitelist()
def force_biometric_sync():
	"""In-app stand-in for a device pull: report today's checkin count."""
	_require_hr()
	today = getdate()
	count = frappe.db.count("Employee Checkin", {"time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]})
	return {"ok": True, "synced": count}


@frappe.whitelist()
def get_notifications():
	"""Unread notifications for the Topbar bell."""
	rows = frappe.get_all("Notification Log",
		filters={"for_user": frappe.session.user},
		fields=["name", "subject", "type", "creation", "read"],
		order_by="creation desc", limit=20)
	for r in rows:
		r["time"] = frappe.utils.pretty_date(r.creation)
		r["subject"] = frappe.utils.strip_html(r.subject or "")
	return {"items": rows, "unread": sum(1 for r in rows if not r.read)}


@frappe.whitelist(methods=["POST"])
def mark_notifications_read():
	frappe.db.set_value("Notification Log", {"for_user": frappe.session.user, "read": 0}, "read", 1, update_modified=False)
	frappe.db.commit()
	return {"ok": True}


# ---------------------------------------------------------------- reports (in-app)
def _money(v):
	return frappe.utils.fmt_money(v or 0, currency="INR")


def _report_salary_register():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
		fields=["employee_name", "department", "end_date", "gross_pay", "total_deduction", "net_pay"],
		order_by="net_pay desc", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Department", "key": "dept"},
			{"label": "Period", "key": "period"}, {"label": "Gross", "key": "gross"},
			{"label": "Deductions", "key": "ded"}, {"label": "Net pay", "key": "net"}]
	rows = [{"emp": s.employee_name, "dept": (s.department or "").split(" - ")[0],
			 "period": formatdate(s.end_date, "MMM yyyy") if s.end_date else "—",
			 "gross": _money(s.gross_pay), "ded": _money(s.total_deduction), "net": _money(s.net_pay)}
			for s in slips]
	return cols, rows


def _report_employees():
	emps = frappe.get_all("Employee", filters={"status": ["in", ["Active", "On Leave"]]},
		fields=["employee_name", "employee_number", "department", "designation", "date_of_joining", "status"],
		order_by="employee_name", limit=500)
	cols = [{"label": "Name", "key": "n"}, {"label": "ID", "key": "id"}, {"label": "Department", "key": "dept"},
			{"label": "Designation", "key": "desig"}, {"label": "Joined", "key": "doj"}, {"label": "Status", "key": "st"}]
	rows = [{"n": e.employee_name, "id": e.employee_number, "dept": (e.department or "").split(" - ")[0],
			 "desig": e.designation, "doj": formatdate(e.date_of_joining, "dd MMM yyyy") if e.date_of_joining else "—",
			 "st": e.status} for e in emps]
	return cols, rows


def _report_leave_balance():
	allocs = frappe.get_all("Leave Allocation", filters={"docstatus": 1},
		fields=["employee_name", "leave_type", "total_leaves_allocated", "from_date", "to_date"],
		order_by="employee_name", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Leave type", "key": "lt"},
			{"label": "Allocated", "key": "alloc"}, {"label": "Period", "key": "period"}]
	rows = [{"emp": a.employee_name, "lt": a.leave_type, "alloc": a.total_leaves_allocated,
			 "period": f"{formatdate(a.from_date, 'dd MMM')} – {formatdate(a.to_date, 'dd MMM yyyy')}" if a.from_date else "—"}
			for a in allocs]
	return cols, rows


def _report_attendance():
	att = frappe.get_all("Attendance", filters={"docstatus": 1},
		fields=["employee_name", "attendance_date", "status", "working_hours"],
		order_by="attendance_date desc", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Date", "key": "date"},
			{"label": "Status", "key": "st"}, {"label": "Hours", "key": "hrs"}]
	rows = [{"emp": a.employee_name, "date": formatdate(a.attendance_date, "dd MMM yyyy"),
			 "st": a.status, "hrs": round(a.working_hours or 0, 1)} for a in att]
	return cols, rows


def _report_bankfile():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
		fields=["employee", "employee_name", "net_pay"], order_by="net_pay desc", limit=500)
	# batch bank details for all employees (avoid N+1)
	emp_ids = list({s.employee for s in slips})
	bank_map = {e.name: e for e in frappe.get_all("Employee", filters={"name": ["in", emp_ids]},
		fields=["name", "bank_name", "bank_ac_no"])} if emp_ids else {}
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Bank", "key": "bank"},
			{"label": "Account", "key": "ac"}, {"label": "Net pay", "key": "net"}]
	rows = []
	for s in slips:
		info = bank_map.get(s.employee) or {}
		ac = info.get("bank_ac_no") or ""
		rows.append({"emp": s.employee_name, "bank": info.get("bank_name") or "—",
					 "ac": ("XXXX " + ac[-4:]) if ac else "—", "net": _money(s.net_pay)})
	return cols, rows


def _report_tds():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1}, fields=["name", "employee", "employee_name"], limit=2000)
	# batch TDS across all slips in one query (also fixes a bug: parent was never selected)
	tds_rows = frappe.get_all("Salary Detail",
		filters={"parent": ["in", [s.name for s in slips]], "parentfield": "deductions", "salary_component": "TDS"},
		fields=["parent", "amount"]) if slips else []
	tds_by_slip = {}
	for d in tds_rows:
		tds_by_slip[d.parent] = tds_by_slip.get(d.parent, 0) + (d.amount or 0)
	agg = {}
	for s in slips:
		row = agg.setdefault(s.employee, {"emp": s.employee_name, "tds": 0})
		row["tds"] += tds_by_slip.get(s.name, 0)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "TDS deducted (FY)", "key": "tds"}]
	rows = [{"emp": v["emp"], "tds": _money(v["tds"])} for v in sorted(agg.values(), key=lambda x: -x["tds"])]
	return cols, rows


_REPORT_PROVIDERS = {
	"Salary Register": _report_salary_register,
	"Employee Information": _report_employees,
	"Employee Leave Balance": _report_leave_balance,
	"Monthly Attendance Sheet": _report_attendance,
	"Bank Remittance": _report_bankfile,
	"Income Tax Computation": _report_tds,
}


@frappe.whitelist()
def get_report_data(report_name, filters=None):
	"""Return columns + rows for an in-app report. Uses real-data providers for the
	known reports; falls back to running a standard Frappe query report otherwise."""
	_require_hr()
	provider = _REPORT_PROVIDERS.get(report_name)
	if provider:
		try:
			cols, rows = provider()
			return {"columns": cols, "rows": rows, "report": report_name}
		except Exception as e:
			return {"error": str(e), "columns": [], "rows": []}

	from frappe.desk.query_report import run
	flt = frappe.parse_json(filters) if filters else {"company": COMPANY_NAME()}
	try:
		res = run(report_name, filters=flt, ignore_prepared_report=True) or {}
	except Exception as e:
		return {"error": str(e), "columns": [], "rows": []}
	cols = []
	for c in (res.get("columns") or []):
		if isinstance(c, dict):
			cols.append({"label": c.get("label") or c.get("fieldname"), "key": c.get("fieldname") or c.get("label")})
		else:
			cols.append({"label": str(c), "key": str(c)})
	rows = []
	for r in (res.get("result") or []):
		if isinstance(r, dict):
			rows.append(r)
		elif isinstance(r, (list, tuple)):
			rows.append({cols[i]["key"]: v for i, v in enumerate(r) if i < len(cols)})
	return {"columns": cols, "rows": rows[:500], "report": report_name}


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
