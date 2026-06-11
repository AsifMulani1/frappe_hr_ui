"""Read APIs for the Frappe HR UI screens.

These assemble screen-shaped payloads from real hrms/erpnext DocTypes so the Vue
frontend can bind one resource per screen. No mock data — every value is a live
query against the employee's records.
"""

import frappe
from frappe.utils import getdate, nowdate, now_datetime, get_datetime, time_diff_in_seconds, add_days, formatdate, flt, get_last_day


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


_STATUTORY_FIELDS = ["pf_registration_number", "esic_registration_number", "pt_registration_number", "tan_number"]


# ----------------------------------------------------------- recruitment


# ----------------------------------------------------------- performance (HR)


# ----------------------------------------------------------- analytics


# ================================================================ WRITES (ESS)


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


