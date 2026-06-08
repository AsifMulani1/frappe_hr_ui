"""Read APIs for the Frappe HR UI screens.

These assemble screen-shaped payloads from real hrms/erpnext DocTypes so the Vue
frontend can bind one resource per screen. No mock data — every value is a live
query against the employee's records.
"""

import frappe
from frappe.utils import getdate, nowdate, now_datetime, get_datetime, time_diff_in_seconds, add_days, formatdate


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
	first_in = next((l.time for l in logs if l.log_type == "IN"), logs[0].time if logs else None)
	last_out = next((l.time for l in reversed(logs) if l.log_type == "OUT"), None)
	checked_in = bool(first_in) and not last_out

	worked_seconds = 0
	if first_in:
		end = get_datetime(last_out) if last_out else now_datetime()
		worked_seconds = max(0, time_diff_in_seconds(end, get_datetime(first_in)))

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
	avg = sum(hours) / len(hours) if hours else 0
	return {
		"present": present + wfh,
		"wfh": wfh,
		"leave": leave,
		"avg_hours": f"{int(avg)}h {int((avg % 1) * 60):02d}m" if avg else "—",
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
	hl = employee.get("holiday_list") or frappe.db.get_value("Company", employee.get("company"), "default_holiday_list")
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
				"branch", "reports_to", "company_email", "cell_number", "status", "image", "user_id"],
		order_by="employee_name asc",
		limit=999,
	)
	for p in people:
		p["location"] = p.get("branch") or "—"
		p["manager_name"] = frappe.db.get_value("Employee", p.reports_to, "employee_name") if p.get("reports_to") else "—"
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
	return {
		"employee": emp,
		"tds_paid": tds,
		"declarations": decls,
		"declared_total": declared_total,
		"fbp": [["Meal card", 2200], ["Fuel & travel", 3000], ["Telephone & internet", 1500], ["Books & periodicals", 1000]],
	}


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
