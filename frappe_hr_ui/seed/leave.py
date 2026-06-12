"""Seed leave allocations, applications and attendance."""

import frappe
from frappe.utils import getdate, add_days, nowdate

from .data import (
	COMPANY,
	LEAVE_TYPES,
)


def ensure_leave_allocations(id_to_name):
    fy_from, fy_to = "2026-04-01", "2027-03-31"
    for eid, docname in id_to_name.items():
        for lt, qty in LEAVE_TYPES:
            if frappe.db.exists("Leave Allocation",
                                {"employee": docname, "leave_type": lt, "from_date": fy_from}):
                continue
            try:
                la = frappe.get_doc({
                    "doctype": "Leave Allocation", "employee": docname, "leave_type": lt,
                    "from_date": fy_from, "to_date": fy_to, "new_leaves_allocated": qty,
                })
                la.insert(ignore_permissions=True)
                la.submit()
            except Exception as e:
                frappe.db.rollback()
                print(f"    ! leave alloc {eid}/{lt}: {e}")
    frappe.db.commit()
    print("  + Leave Allocations ensured")


def _leave_app(docname, lt, frm, to, status, reason):
    if frappe.db.exists("Leave Application",
                        {"employee": docname, "leave_type": lt, "from_date": frm}):
        return
    try:
        la = frappe.get_doc({
            "doctype": "Leave Application", "employee": docname, "leave_type": lt,
            "from_date": frm, "to_date": to, "status": status,
            "description": reason,
        })
        la.insert(ignore_permissions=True)
        if status == "Approved":
            la.submit()
    except Exception as e:
        frappe.db.rollback()
        print(f"    ! leave app {docname}/{lt}: {e}")


def ensure_leave_applications(id_to_name):
    A = id_to_name.get("HR-1042")
    if A:
        _leave_app(A, "Earned Leave", "2026-05-12", "2026-05-16", "Approved", "Family vacation - Goa")
        _leave_app(A, "Casual Leave", "2026-06-18", "2026-06-18", "Open", "Personal work")
    pairs = [
        ("HR-1067", "Sick Leave",   "2026-06-02", "2026-06-03", "Approved", "Fever"),
        ("HR-1102", "Casual Leave", "2026-06-02", "2026-06-04", "Approved", "Out of station"),
        ("HR-1190", "Earned Leave", "2026-06-23", "2026-06-27", "Open",     "Family function"),
        ("HR-1221", "Sick Leave",   "2026-05-30", "2026-05-30", "Approved", "Medical"),
    ]
    for eid, lt, frm, to, st, rsn in pairs:
        dn = id_to_name.get(eid)
        if dn:
            _leave_app(dn, lt, frm, to, st, rsn)

    # A few approved leaves spanning the actual current day so the "who's out"
    # card always reflects real, present-day absences.
    today = getdate()
    near = [
        ("HR-1067", "Sick Leave",   add_days(today, -1), add_days(today, 1)),
        ("HR-1102", "Casual Leave", today,               add_days(today, 2)),
        ("HR-1334", "Earned Leave", add_days(today, -2), today),
    ]
    for eid, lt, frm, to in near:
        dn = id_to_name.get(eid)
        if dn:
            _leave_app(dn, lt, str(frm), str(to), "Approved", "Planned time off")
    frappe.db.commit()
    print("  + Leave Applications ensured")


def ensure_attendance(id_to_name):
    from datetime import timedelta
    # Fill attendance from mid-May through the actual current day so team and
    # company attendance screens always have present-day data.
    start, end = getdate("2026-05-18"), getdate(nowdate())
    for eid, docname in id_to_name.items():
        d = start
        while d <= end:
            if d.weekday() < 5:
                if not frappe.db.exists("Attendance", {"employee": docname, "attendance_date": d}):
                    try:
                        att = frappe.get_doc({
                            "doctype": "Attendance", "employee": docname,
                            "attendance_date": d, "status": "Present", "company": COMPANY,
                        })
                        att.insert(ignore_permissions=True)
                        att.submit()
                    except Exception:
                        frappe.db.rollback()
            d += timedelta(days=1)
    A = id_to_name.get("HR-1042")
    if A:
        checkins = [("2026-06-01 10:04:00", "IN"), ("2026-06-01 19:12:00", "OUT"),
                    ("2026-06-02 09:58:00", "IN")]
        # An open check-in for the actual current day so the home "today's
        # attendance" hero reflects a live, checked-in state on any run date.
        today = nowdate()
        checkins.append((f"{today} 09:58:00", "IN"))
        for dt, log in checkins:
            if not frappe.db.exists("Employee Checkin", {"employee": A, "time": dt}):
                try:
                    frappe.get_doc({"doctype": "Employee Checkin", "employee": A,
                                    "time": dt, "log_type": log}).insert(ignore_permissions=True)
                except Exception:
                    frappe.db.rollback()
    frappe.db.commit()
    print("  + Attendance + check-ins ensured")
