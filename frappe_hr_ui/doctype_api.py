"""Generic, permission-aware doctype engine.

The keystone for a *no-Desk* front-end: a metadata-driven CRUD layer the SPA uses to
list / view / create / edit / submit / delete any HR or Payroll doctype, with every
operation enforced by Frappe's own permission system (no `ignore_permissions`).

Scope is deliberately limited to the HR + Payroll modules plus a small set of HR-adjacent
masters — this is an HR admin surface, not a universal database editor.
"""

import frappe

# HR-adjacent masters that live outside the HR/Payroll modules but the UI must configure.
_CORE_MASTERS = {
	"Company", "Department", "Designation", "Branch", "Cost Center",
	"Holiday List", "Employment Type", "Employee Grade", "Currency",
}
_ALLOWED_MODULES = {"HR", "Payroll"}


def _allowed(doctype):
	"""Only HR/Payroll doctypes (+ core masters + child tables) are reachable here."""
	if doctype in _CORE_MASTERS:
		return
	try:
		meta = frappe.get_meta(doctype)
	except Exception:
		meta = None
	# child tables carry only field definitions (no standalone data) — allow for form rendering
	if meta and meta.istable:
		return
	if not meta or meta.module not in _ALLOWED_MODULES:
		frappe.throw(frappe._("This record type isn't available here."), frappe.PermissionError)


def _perms(doctype):
	return {
		"read": frappe.has_permission(doctype, "read"),
		"create": frappe.has_permission(doctype, "create"),
		"write": frappe.has_permission(doctype, "write"),
		"delete": frappe.has_permission(doctype, "delete"),
		"submit": frappe.has_permission(doctype, "submit"),
		"cancel": frappe.has_permission(doctype, "cancel"),
	}


@frappe.whitelist()
def get_meta(doctype):
	"""Field + permission metadata so the SPA can render a form/list for any doctype."""
	_allowed(doctype)
	meta = frappe.get_meta(doctype)
	if not meta.istable and not frappe.has_permission(doctype, "read"):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	SKIP = {"Section Break", "Column Break", "Tab Break", "HTML", "Button"}
	fields = []
	for f in meta.fields:
		if f.fieldtype in SKIP:
			continue
		fields.append({
			"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype,
			"options": f.options, "reqd": bool(f.reqd), "read_only": bool(f.read_only),
			"hidden": bool(f.hidden), "in_list_view": bool(f.in_list_view),
			"default": f.default, "description": f.description,
			"precision": f.precision,
		})
	return {
		"doctype": doctype,
		"title_field": meta.title_field or "name",
		"is_submittable": bool(meta.is_submittable),
		"is_single": bool(meta.issingle),
		"fields": fields,
		"perms": _perms(doctype),
	}


@frappe.whitelist()
def get_list(doctype, start=0, page_length=20, search=None, filters=None, order_by=None):
	"""Permission-filtered list (frappe.get_list enforces read perms + user filters)."""
	_allowed(doctype)
	meta = frappe.get_meta(doctype)
	fieldnames = {f.fieldname for f in meta.fields}
	title = meta.title_field if meta.title_field in fieldnames else None
	cols = ["name"]
	if title:
		cols.append(title)
	cols += [f.fieldname for f in meta.fields if f.in_list_view and f.fieldname in fieldnames][:5]
	if meta.is_submittable:
		cols.append("docstatus")
	cols = list(dict.fromkeys(cols))

	flt = frappe.parse_json(filters) if filters else {}
	or_filters = None
	if search:
		or_filters = [[doctype, "name", "like", f"%{search}%"]]
		if title:
			or_filters.append([doctype, title, "like", f"%{search}%"])

	# sanitise order_by against real fields
	ob = "modified desc"
	if order_by:
		fld = order_by.split()[0]
		if fld in fieldnames or fld in ("name", "modified", "creation"):
			ob = order_by

	rows = frappe.get_list(doctype, fields=cols, filters=flt, or_filters=or_filters,
		limit_start=int(start), limit_page_length=int(page_length) + 1, order_by=ob)
	has_more = len(rows) > int(page_length)
	return {"rows": rows[:int(page_length)], "has_more": has_more, "columns": cols,
			"title_field": title, "is_submittable": bool(meta.is_submittable)}


@frappe.whitelist()
def search_link(doctype, txt=None, page_length=20):
	"""Permission-aware option list for a Link field's target (any readable doctype)."""
	if not frappe.has_permission(doctype, "read"):
		return {"options": []}
	meta = frappe.get_meta(doctype)
	title = meta.title_field if (meta.title_field and meta.title_field != "name") else None
	fields = ["name"] + ([title] if title else [])
	or_filters = None
	if txt:
		or_filters = [[doctype, "name", "like", f"%{txt}%"]]
		if title:
			or_filters.append([doctype, title, "like", f"%{txt}%"])
	rows = frappe.get_list(doctype, fields=fields, or_filters=or_filters,
		limit_page_length=int(page_length), order_by="modified desc")

	def _label(r):
		t = r.get(title) if title else None
		return f"{t} ({r['name']})" if t and t != r["name"] else r["name"]

	return {"options": [{"label": _label(r), "value": r["name"]} for r in rows]}


@frappe.whitelist()
def get_doc(doctype, name):
	_allowed(doctype)
	if not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	return frappe.get_doc(doctype, name).as_dict()


@frappe.whitelist(methods=["POST"])
def save_doc(doctype, doc, name=None):
	"""Insert (name omitted) or update — Frappe enforces create/write perms + validations."""
	_allowed(doctype)
	values = frappe.parse_json(doc) or {}
	values.pop("doctype", None)
	if name:
		d = frappe.get_doc(doctype, name)
		d.update(values)
		d.save()  # respects write perm + controller validation
	else:
		d = frappe.get_doc({"doctype": doctype, **values})
		d.insert()  # respects create perm + validation
	frappe.db.commit()
	return {"name": d.name}


@frappe.whitelist(methods=["POST"])
def submit_doc(doctype, name):
	_allowed(doctype)
	d = frappe.get_doc(doctype, name)
	d.submit()
	frappe.db.commit()
	return {"name": d.name, "docstatus": d.docstatus}


@frappe.whitelist(methods=["POST"])
def cancel_doc(doctype, name):
	_allowed(doctype)
	d = frappe.get_doc(doctype, name)
	d.cancel()
	frappe.db.commit()
	return {"name": d.name, "docstatus": d.docstatus}


@frappe.whitelist(methods=["POST"])
def delete_doc(doctype, name):
	_allowed(doctype)
	if not frappe.has_permission(doctype, "delete", doc=name):
		frappe.throw(frappe._("Not permitted"), frappe.PermissionError)
	frappe.delete_doc(doctype, name)
	frappe.db.commit()
	return {"ok": True}
