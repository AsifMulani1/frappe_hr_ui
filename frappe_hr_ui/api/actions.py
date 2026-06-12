# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""Write actions — apply leave, raise/reply ticket, submit expense, regularisation, profile."""

import frappe
from frappe.utils import flt, getdate

from .core import (
	HR_ROLES,
	SELF_EDITABLE_FIELDS,
	_current_employee,
	_require_hr,
)


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
