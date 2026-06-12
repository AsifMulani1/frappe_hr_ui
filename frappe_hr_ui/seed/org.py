"""Seed the company, masters, holidays, leave types and grades."""

import frappe

from .data import (
	ABBR,
	COMPANY,
	COUNTRY,
	CURRENCY,
	GRADES,
	HOLIDAYS,
	LEAVE_TYPES,
	PEOPLE,
	_exists,
	_grade_for_ctc,
)


def ensure_company():
    if not _exists("Company", COMPANY):
        frappe.get_doc({
            "doctype": "Company", "company_name": COMPANY, "abbr": ABBR,
            "default_currency": CURRENCY, "country": COUNTRY,
        }).insert(ignore_permissions=True)
        print(f"  + Company {COMPANY}")


def ensure_simple(doctype, names, extra=None):
    """Create single-field master records by name (Department, Designation, etc.)."""
    name_field = {
        "Department": "department_name",
        "Designation": "designation_name",
        "Branch": "branch",
        "Employment Type": "employee_type_name",
    }[doctype]
    for n in names:
        scoped = f"{n} - {ABBR}" if doctype == "Department" else n
        if doctype == "Department" and _exists("Department", scoped):
            continue
        if doctype != "Department" and _exists(doctype, n):
            continue
        doc = {"doctype": doctype, name_field: n}
        if doctype == "Department":
            doc["company"] = COMPANY
        if extra:
            doc.update(extra)
        frappe.get_doc(doc).insert(ignore_permissions=True)
    print(f"  + {doctype}: {len(names)} ensured")


def ensure_holiday_list():
    hl_name = "Frappe Holidays 2026"
    if _exists("Holiday List", hl_name):
        return hl_name
    doc = frappe.get_doc({
        "doctype": "Holiday List", "holiday_list_name": hl_name,
        "from_date": "2026-01-01", "to_date": "2026-12-31",
        "holidays": [{"holiday_date": d, "description": desc} for d, desc in HOLIDAYS],
    })
    doc.insert(ignore_permissions=True)
    print(f"  + Holiday List {hl_name}")
    return hl_name


def ensure_holiday_assignment(hl):
    # HRMS v16 resolves an employee's holidays via submitted "Holiday List
    # Assignment" records, not the Employee.holiday_list field. One company-wide
    # assignment covers everyone for leave + salary-slip working-day lookups.
    if frappe.db.exists(
        "Holiday List Assignment",
        {"applicable_for": "Company", "assigned_to": COMPANY, "docstatus": 1},
    ):
        return
    try:
        hla = frappe.get_doc({
            "doctype": "Holiday List Assignment",
            "applicable_for": "Company",
            "assigned_to": COMPANY,
            "employee_company": COMPANY,
            "holiday_list": hl,
            "holiday_list_start": "2026-01-01",
            "holiday_list_end": "2026-12-31",
            "from_date": "2026-01-01",
        })
        hla.insert(ignore_permissions=True)
        hla.submit()
        frappe.db.commit()
        print("  + Holiday List Assignment (company-wide) created")
    except Exception as e:
        frappe.db.rollback()
        print(f"    ! holiday list assignment: {e}")


def ensure_leave_types():
    for lt, _q in LEAVE_TYPES:
        if not _exists("Leave Type", lt):
            frappe.get_doc({
                "doctype": "Leave Type", "leave_type_name": lt,
                "max_leaves_allowed": _q, "is_carry_forward": 1 if lt == "Earned Leave" else 0,
            }).insert(ignore_permissions=True)
    print(f"  + Leave Types: {len(LEAVE_TYPES)} ensured")


def ensure_genders():
    # Fresh sites may not have every Gender record the seed references.
    for g in ["Prefer not to say", "Male", "Female", "Other"]:
        if not _exists("Gender", g):
            frappe.get_doc({"doctype": "Gender", "gender": g}).insert(ignore_permissions=True)


def ensure_grades(id_to_name):
    for g in GRADES:
        if not _exists("Employee Grade", g):
            try:
                frappe.get_doc({"doctype": "Employee Grade", "__newname": g, "name": g}).insert(ignore_permissions=True)
            except Exception:
                frappe.db.rollback()
    # assign a grade to everyone by CTC tier (helps directory / 360 screens)
    for (eid, name, desig, dept, loc, status, mgr, etype, ctc, doj) in PEOPLE:
        dn = id_to_name.get(eid)
        if dn and _exists("Employee Grade", _grade_for_ctc(ctc)):
            frappe.db.set_value("Employee", dn, {"grade": _grade_for_ctc(ctc), "ctc": ctc})
    frappe.db.commit()
    print("  + Employee Grades ensured + assigned")
