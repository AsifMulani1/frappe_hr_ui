"""Seed salary structures, slips and expense claims."""

import frappe
from frappe.utils import getdate

from .data import (
	COMPANY,
	CURRENCY,
	PEOPLE,
	_exists,
)


def ensure_salary_structure(id_to_name):
    earnings = [
        ("Basic", "Earning", "base * 0.40"),
        ("House Rent Allowance", "Earning", "base * 0.20"),
        ("Special Allowance", "Earning", "base * 0.28"),
        ("Conveyance Allowance", "Earning", "1600"),
        ("LTA", "Earning", "base * 0.05"),
    ]
    deductions = [
        ("Provident Fund", "Deduction", "base * 0.048"),
        ("Professional Tax", "Deduction", "200"),
        ("TDS", "Deduction", "base * 0.10"),
    ]
    for cname, ctype, _f in earnings + deductions:
        if not _exists("Salary Component", cname):
            frappe.get_doc({
                "doctype": "Salary Component", "salary_component": cname,
                "type": ctype, "company": COMPANY,
            }).insert(ignore_permissions=True)

    ss_name = "Frappe Standard Structure"
    if not _exists("Salary Structure", ss_name):
        ss = frappe.get_doc({
            "doctype": "Salary Structure", "name": ss_name, "company": COMPANY,
            "payroll_frequency": "Monthly", "currency": CURRENCY,
            "earnings": [{"salary_component": c, "amount_based_on_formula": 1, "formula": f}
                         for c, t, f in earnings],
            "deductions": [{"salary_component": c, "amount_based_on_formula": 1, "formula": f}
                           for c, t, f in deductions],
        })
        ss.insert(ignore_permissions=True)
        ss.submit()
        print(f"  + Salary Structure {ss_name}")

    for (eid, name, desig, dept, loc, status, mgr, etype, ctc, doj) in PEOPLE:
        docname = id_to_name.get(eid)
        if not docname:
            continue
        if _exists("Salary Structure Assignment", {"employee": docname}):
            continue
        monthly = round(ctc / 12)
        ssa = frappe.get_doc({
            "doctype": "Salary Structure Assignment",
            "employee": docname, "salary_structure": ss_name,
            "company": COMPANY, "from_date": doj if getdate(doj) > getdate("2026-01-01") else "2026-01-01",
            "base": monthly,
        })
        ssa.insert(ignore_permissions=True)
        ssa.submit()
    print("  + Salary Structure Assignments ensured")


def _expense_account():
    return frappe.db.get_value(
        "Account",
        {"company": COMPANY, "account_type": "Expense Account", "is_group": 0},
        "name",
    ) or frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Expense", "is_group": 0}, "name")


def ensure_expense_claims(id_to_name):
    acct = _expense_account()
    for t in ["Travel", "Internet", "Food", "Conveyance", "Wellness", "Learning"]:
        if not frappe.db.exists("Expense Claim Type", t):
            try:
                doc = {"doctype": "Expense Claim Type", "expense_type": t}
                if acct:
                    doc["accounts"] = [{"company": COMPANY, "default_account": acct}]
                frappe.get_doc(doc).insert(ignore_permissions=True)
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! expense type {t}: {e}")
        elif acct and not frappe.db.exists("Expense Claim Account", {"parent": t, "company": COMPANY}):
            try:
                ect = frappe.get_doc("Expense Claim Type", t)
                ect.append("accounts", {"company": COMPANY, "default_account": acct})
                ect.save(ignore_permissions=True)
            except Exception:
                frappe.db.rollback()
    frappe.db.commit()  # persist types before risky claim inserts
    rows = [
        ("HR-1042", "Internet", "2026-05-31", 1499, "Home broadband - May"),
        ("HR-1042", "Conveyance", "2026-05-28", 640, "Client visit - Andheri"),
        ("HR-1156", "Travel", "2026-05-20", 9800, "Hotel - Bengaluru, 2 nights"),
    ]
    for eid, etype, edate, amt, desc in rows:
        dn = id_to_name.get(eid)
        if not dn or frappe.db.exists("Expense Claim",
                                      {"employee": dn, "posting_date": edate}):
            continue
        try:
            ec = frappe.get_doc({
                "doctype": "Expense Claim", "employee": dn, "company": COMPANY,
                "posting_date": edate, "approval_status": "Draft",
                "currency": CURRENCY, "exchange_rate": 1,
                "expenses": [{"expense_date": edate, "expense_type": etype,
                              "amount": amt, "sanctioned_amount": amt, "description": desc}],
            })
            ec.insert(ignore_permissions=True)
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! expense {eid}: {e}")
    frappe.db.commit()
    print("  + Expense Claims ensured")


def ensure_salary_slips(id_to_name):
    start, end = "2026-05-01", "2026-05-31"
    made = 0
    for eid, docname in id_to_name.items():
        if frappe.db.exists("Salary Slip",
                            {"employee": docname, "start_date": start, "end_date": end}):
            continue
        try:
            ss = frappe.get_doc({
                "doctype": "Salary Slip", "employee": docname,
                "start_date": start, "end_date": end,
                "payroll_frequency": "Monthly", "company": COMPANY,
            })
            ss.insert(ignore_permissions=True)
            ss.submit()
            made += 1
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! salary slip {eid}: {e}")
    frappe.db.commit()
    print(f"  + Salary Slips (May 2026): {made} created")
