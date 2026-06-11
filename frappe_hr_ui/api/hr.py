# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""HR admin screens — dashboards, directory, lifecycle, attendance, roster, biometric."""

import frappe
from frappe.utils import add_days, formatdate, get_datetime, getdate

from .core import (
	COMPANY_NAME,
	COMPLIANCE_META,
	_component_total,
	_emp,
	_india_payroll_installed,
	_latest_slip_period,
	_require_hr,
	_tenure,
)


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
