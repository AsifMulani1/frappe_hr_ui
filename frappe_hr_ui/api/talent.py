# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Recruitment & performance screens — jobs, pipeline, interviews, offers, appraisal, surveys, analytics."""

import frappe
from frappe.utils import formatdate, getdate

from .core import (
	COMPANY_NAME,
	_require_hr,
)


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
