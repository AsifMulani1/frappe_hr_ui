"""Seed employees, their profile details and persona users."""

import frappe

from .data import (
	ABBR,
	COMPANY,
	PEOPLE,
	PERSONA_USERS,
	_exists,
)


def ensure_employees():
    """Two passes: create everyone first, then wire reports_to (manager ID)."""
    ensure_genders()
    id_to_name = {}

    for (eid, name, desig, dept, loc, status, mgr, etype, ctc, doj) in PEOPLE:
        if _exists("Employee", {"employee_number": eid}):
            existing = frappe.db.get_value("Employee", {"employee_number": eid}, "name")
            id_to_name[eid] = existing
            continue
        first, *rest = name.split(" ")
        last = " ".join(rest) or first
        emp = frappe.get_doc({
            "doctype": "Employee",
            "employee_number": eid,
            "first_name": first,
            "last_name": last,
            "employee_name": name,
            "company": COMPANY,
            "status": "Active",
            "date_of_joining": doj,
            "date_of_birth": "1994-01-01",
            "gender": "Prefer not to say",
            "department": f"{dept} - {ABBR}",
            "designation": desig,
            "branch": loc if loc != "Remote" else None,
            "employment_type": etype,
            "company_email": name.lower().replace(" ", ".") + "@frappe.io",
            "holiday_list": "Frappe Holidays 2026",
            "bio": f"Mockup status: {status}",
        })
        emp.insert(ignore_permissions=True)
        id_to_name[eid] = emp.name

    for (eid, name, desig, dept, loc, status, mgr, etype, ctc, doj) in PEOPLE:
        if mgr and mgr in id_to_name:
            frappe.db.set_value("Employee", id_to_name[eid], "reports_to", id_to_name[mgr])

    print(f"  + Employees: {len(PEOPLE)} ensured")
    return id_to_name


def ensure_profile_details(id_to_name):
    """Rich profile for the ESS persona (Aarav) so the profile screen is complete."""
    a = id_to_name.get("HR-1042")
    if not a:
        return
    vals = {
        "date_of_birth": "1996-08-14",
        "gender": "Male",
        "blood_group": "O+",
        "marital_status": "Married",
        "cell_number": "+91 98200 41042",
        "personal_email": "aarav.m@gmail.com",
        "emergency_phone_number": "+91 98201 22119",
        "person_to_be_contacted": "Riya Mehta",
        "relation": "Spouse",
        "current_address": "A-1204, Lodha Amara, Thane (W), Mumbai 400607",
        "permanent_address": "A-1204, Lodha Amara, Thane (W), Mumbai 400607",
        "bank_name": "HDFC Bank",
        "bank_ac_no": "50100247701841",
        "ifsc_code": "HDFC0000234",
        "pan_number": "ABCPM4521K",
        "provident_fund_account": "100874512369",
        "salary_mode": "Bank",
    }
    for k, v in list(vals.items()):
        if not frappe.get_meta("Employee").get_field(k):
            vals.pop(k, None)
    try:
        frappe.db.set_value("Employee", a, vals)
        frappe.db.commit()
        print("  + Profile details for Aarav set")
    except Exception as e:
        frappe.db.rollback()
        print(f"    ! profile details: {e}")


def ensure_users(id_to_name):
    for eid, email, pwd, roles in PERSONA_USERS:
        docname = id_to_name.get(eid)
        if not docname:
            continue
        first = frappe.db.get_value("Employee", docname, "first_name")
        valid_roles = [r for r in roles if frappe.db.exists("Role", r)]
        if not frappe.db.exists("User", email):
            try:
                u = frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": first or email.split("@")[0],
                    "send_welcome_email": 0,
                    "new_password": pwd,
                })
                u.flags.no_welcome_mail = True
                u.insert(ignore_permissions=True)
                # add_roles persists reliably; assigning the child table on insert
                # does not always stick for a brand-new user.
                u.add_roles(*valid_roles)
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! user {email}: {e}")
                continue
        else:
            try:
                from frappe.utils.password import update_password
                update_password(email, pwd)
                frappe.get_doc("User", email).add_roles(*valid_roles)
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! user sync {email}: {e}")
        # link employee <-> user
        if frappe.db.get_value("Employee", docname, "user_id") != email:
            frappe.db.set_value("Employee", docname, "user_id", email)
    frappe.db.commit()
    print(f"  + Persona users: {len(PERSONA_USERS)} ensured (password: Frappe@123)")
