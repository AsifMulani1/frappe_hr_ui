"""Bulk employee import for the in-UI setup wizard.

The SPA parses an uploaded CSV client-side and posts rows here; we validate and
create Employee records one by one, returning a per-row result so the user sees
exactly what succeeded and what failed. Permission-gated (Employee create).
"""

import frappe

COLUMNS = [
	{"key": "first_name", "label": "First name", "reqd": True},
	{"key": "last_name", "label": "Last name", "reqd": False},
	{"key": "gender", "label": "Gender", "reqd": True, "hint": "Male / Female / Other"},
	{"key": "date_of_birth", "label": "Date of birth", "reqd": True, "hint": "YYYY-MM-DD"},
	{"key": "date_of_joining", "label": "Date of joining", "reqd": True, "hint": "YYYY-MM-DD"},
	{"key": "designation", "label": "Designation", "reqd": False},
	{"key": "department", "label": "Department", "reqd": False},
	{"key": "company_email", "label": "Work email", "reqd": False},
]


@frappe.whitelist()
def import_template():
	"""Columns + a sample CSV header row for the importer UI."""
	return {"columns": COLUMNS, "header": ",".join(c["key"] for c in COLUMNS)}


def _company(company=None):
	return company or frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")


def _ensure_designation(name):
	"""Find or create a Designation so a CSV with new titles doesn't error."""
	name = (name or "").strip()
	if not name:
		return None
	if frappe.db.exists("Designation", name):
		return name
	existing = frappe.db.get_value("Designation", {"designation_name": name})
	if existing:
		return existing
	return frappe.get_doc({"doctype": "Designation", "designation_name": name}).insert(ignore_permissions=True).name


def _ensure_department(name, company):
	"""Find or create a Department (Departments are company-scoped & abbr-suffixed)."""
	name = (name or "").strip()
	if not name:
		return None
	if frappe.db.exists("Department", name):
		return name
	existing = frappe.db.get_value("Department", {"department_name": name, "company": company}) \
		or frappe.db.get_value("Department", {"department_name": name})
	if existing:
		return existing
	return frappe.get_doc({"doctype": "Department", "department_name": name, "company": company}).insert(ignore_permissions=True).name


@frappe.whitelist(methods=["POST"])
def import_employees(rows, company=None):
	if not frappe.has_permission("Employee", "create"):
		frappe.throw(frappe._("You are not permitted to import employees."), frappe.PermissionError)
	rows = frappe.parse_json(rows) or []
	company = _company(company)
	if not company:
		frappe.throw(frappe._("No company found. Create your company first (Setup wizard → Company)."))
	created, errors = [], []
	reqd = [c["key"] for c in COLUMNS if c["reqd"]]
	for i, row in enumerate(rows):
		rownum = i + 1
		try:
			missing = [k for k in reqd if not (row.get(k) or "").strip()]
			if missing:
				raise frappe.ValidationError(f"missing {', '.join(missing)}")
			doc = frappe.get_doc({
				"doctype": "Employee",
				"first_name": (row.get("first_name") or "").strip(),
				"last_name": (row.get("last_name") or "").strip() or None,
				"gender": (row.get("gender") or "").strip(),
				"date_of_birth": (row.get("date_of_birth") or "").strip(),
				"date_of_joining": (row.get("date_of_joining") or "").strip(),
				"designation": _ensure_designation(row.get("designation")),
				"department": _ensure_department(row.get("department"), company),
				"company_email": (row.get("company_email") or "").strip() or None,
				"company": company,
				"status": "Active",
			})
			doc.insert(ignore_permissions=True)  # access already gated above
			frappe.db.commit()  # keep successes even if a later row fails
			created.append({"row": rownum, "name": doc.name, "employee_name": doc.employee_name})
		except Exception as e:
			frappe.db.rollback()
			errors.append({"row": rownum, "value": row.get("first_name") or "—", "error": str(e)[:140]})
	return {"created": len(created), "names": created, "errors": errors, "total": len(rows)}
