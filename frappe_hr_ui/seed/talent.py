"""Seed recruitment, announcements, issues, appraisal and lifecycle."""

import frappe
from frappe.utils import nowdate

from .data import (
	ABBR,
	ANNOUNCEMENTS,
	COMPANY,
)


def ensure_recruitment():
    openings = [
        ("Senior Frontend Engineer", "Frontend Engineer", "Engineering"),
        ("Product Designer", "Product Designer", "Design"),
        ("Account Executive", "Account Executive", "Sales"),
        ("DevOps Engineer", "DevOps Engineer", "Engineering"),
    ]
    title_to_name = {}
    for title, desig, dept in openings:
        existing = frappe.db.get_value("Job Opening", {"job_title": title}, "name")
        if existing:
            title_to_name[title] = existing
            continue
        try:
            jo = frappe.get_doc({
                "doctype": "Job Opening", "job_title": title, "designation": desig,
                "company": COMPANY, "status": "Open", "department": f"{dept} - {ABBR}",
            })
            jo.insert(ignore_permissions=True)
            title_to_name[title] = jo.name
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! job opening {title}: {e}")
    frappe.db.commit()  # persist openings before risky child inserts

    # applicant -> (name, email, opening title, applicant status)
    applicants = [
        ("Aisha Khan", "aisha.khan@example.com", "Senior Frontend Engineer", "Open"),
        ("Karan Patel", "karan.patel@example.com", "Senior Frontend Engineer", "Replied"),
        ("Vivek Nair", "vivek.nair@example.com", "Senior Frontend Engineer", "Hold"),
        ("Pooja Reddy", "pooja.reddy@example.com", "Product Designer", "Accepted"),
        ("Arnav Bose", "arnav.bose@example.com", "DevOps Engineer", "Hold"),
        ("Imran Ali", "imran.ali@example.com", "Account Executive", "Open"),
    ]
    for name, email, title, status in applicants:
        if frappe.db.exists("Job Applicant", {"email_id": email}):
            continue
        try:
            frappe.get_doc({
                "doctype": "Job Applicant", "applicant_name": name, "email_id": email,
                "job_title": title_to_name.get(title), "status": status,
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! applicant {name}: {e}")
    frappe.db.commit()

    # interviews
    if not frappe.db.exists("Interview Type", "Technical Round"):
        try:
            frappe.get_doc({"doctype": "Interview Type", "__newname": "Technical Round", "name": "Technical Round"}).insert(ignore_permissions=True)
        except Exception:
            frappe.db.rollback()
    for cand in ["Vivek Nair", "Arnav Bose"]:
        ja = frappe.db.get_value("Job Applicant", {"applicant_name": cand}, "name")
        if ja and not frappe.db.exists("Interview", {"job_applicant": ja}):
            try:
                frappe.get_doc({
                    "doctype": "Interview", "job_applicant": ja, "interview_type": "Technical Round",
                    "scheduled_on": nowdate(), "from_time": "10:00:00", "to_time": "10:45:00",
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! interview {cand}: {e}")

    for name, desig in [("Pooja Reddy", "Product Designer"), ("Arnav Bose", "DevOps Engineer")]:
        ja = frappe.db.get_value("Job Applicant", {"applicant_name": name}, "name")
        if ja and not frappe.db.exists("Job Offer", {"job_applicant": ja}):
            try:
                frappe.get_doc({
                    "doctype": "Job Offer", "job_applicant": ja,
                    "status": "Accepted" if name == "Pooja Reddy" else "Awaiting Response",
                    "offer_date": "2026-05-29", "designation": desig, "company": COMPANY,
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! offer {name}: {e}")
    frappe.db.commit()
    print("  + Recruitment (openings, applicants, interviews, offers) ensured")


def ensure_announcements():
    for title, body in ANNOUNCEMENTS:
        if frappe.db.exists("Note", {"title": title}):
            continue
        try:
            frappe.get_doc({
                "doctype": "Note", "title": title, "public": 1,
                "content": f"<div>{body}</div>",
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! note {title}: {e}")
    frappe.db.commit()
    print(f"  + Announcements (Notes): {len(ANNOUNCEMENTS)} ensured")


def ensure_issues(id_to_name):
    """Helpdesk tickets as Issues raised by Aarav."""
    tickets = [
        ("Discrepancy in May payslip PF deduction", "Open", "Medium"),
        ("Request experience letter for visa", "Closed", "Low"),
        ("Unable to access learning portal", "Open", "High"),
    ]
    for subj, status, prio in tickets:
        if frappe.db.exists("Issue", {"subject": subj}):
            continue
        try:
            frappe.get_doc({
                "doctype": "Issue", "subject": subj, "raised_by": "aarav.mehta@frappe.io",
                "status": status, "priority": prio,
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.db.rollback()
            print(f"    ! issue {subj}: {e}")
    frappe.db.commit()
    print("  + Helpdesk Issues ensured")


def ensure_appraisal(id_to_name):
    """Best-effort: a cycle + appraisal with KRAs for Aarav so Performance has data."""
    a = id_to_name.get("HR-1042")
    if not a or not frappe.db.exists("DocType", "Appraisal Cycle"):
        return
    cycle = "H1 2026"
    try:
        if not frappe.db.exists("Appraisal Cycle", cycle):
            frappe.get_doc({
                "doctype": "Appraisal Cycle", "cycle_name": cycle, "company": COMPANY,
                "start_date": "2026-01-01", "end_date": "2026-06-30",
            }).insert(ignore_permissions=True)
        if not frappe.db.exists("Appraisal", {"employee": a, "appraisal_cycle": cycle}):
            ap = frappe.get_doc({
                "doctype": "Appraisal", "employee": a, "appraisal_cycle": cycle, "company": COMPANY,
                "goals": [
                    {"kra": "Ship attendance regularization v2", "per_weightage": 30, "score": 3.75},
                    {"kra": "Reduce payroll page load to < 1.5s", "per_weightage": 25, "score": 3.0},
                    {"kra": "Mentor 2 junior engineers", "per_weightage": 20, "score": 4.5},
                    {"kra": "Improve test coverage to 80%", "per_weightage": 15, "score": 2.0},
                    {"kra": "Contribute 3 design-system components", "per_weightage": 10, "score": 1.65},
                ],
            })
            ap.insert(ignore_permissions=True)
        frappe.db.commit()
        print("  + Appraisal (Aarav, H1 2026) ensured")
    except Exception as e:
        frappe.db.rollback()
        print(f"    ! appraisal: {e}")


def ensure_lifecycle(id_to_name):
    manish = id_to_name.get("HR-1301")
    kavya = id_to_name.get("HR-1356")
    if manish:
        try:
            frappe.db.set_value("Employee", manish, "final_confirmation_date", "2026-09-02")
        except Exception:
            pass
    if kavya:
        try:
            frappe.db.set_value("Employee", kavya, "relieving_date", "2026-06-28")
        except Exception:
            pass
    frappe.db.commit()
    print("  + Lifecycle flags (probation / notice) set")
