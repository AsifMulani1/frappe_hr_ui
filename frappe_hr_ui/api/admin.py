# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Employee administration — create/update employee, generic doc create, links, notifications."""

import frappe
from frappe.utils import flt, getdate

from .core import (
	COMPANY_NAME,
	HR_ROLES,
	_CREATE_HR,
	_CREATE_SELF,
	_LINK_OK,
	_current_employee,
	_emp,
	_require_hr,
)


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
