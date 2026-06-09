# Seeds the EXACT sample company + people from the HRMS mockup into Frappe HR (hrms).
# Idempotent: safe to re-run. It only creates what's missing.
#
# Run with:
#   bench --site hrms.localhost execute frappe_hr_ui.seed.run
#
# Requires: hrms app installed on the site. Frappe v16.

import frappe
from frappe.utils import getdate, add_days, nowdate

COMPANY = "Frappe Technologies Pvt. Ltd."
ABBR = "FT"
CURRENCY = "INR"
COUNTRY = "India"

DEPARTMENTS = [
    "Engineering", "Design", "Sales", "Marketing",
    "People", "Finance", "Customer Success", "Leadership",
]

LOCATIONS = ["Mumbai", "Bengaluru", "Pune", "Delhi", "Hyderabad", "Remote"]

DESIGNATIONS = [
    "VP Engineering", "Engineering Manager", "Senior Engineer", "Product Engineer",
    "Frontend Engineer", "Backend Engineer", "DevOps Engineer", "QA Engineer",
    "Data Analyst", "Design Lead", "Product Designer", "UX Researcher",
    "Sales Director", "Account Executive", "Sales Executive",
    "Marketing Manager", "Content Strategist", "HR Business Partner", "Recruiter",
    "Finance Controller", "Finance Analyst", "Support Engineer",
    "Customer Success Lead", "Intern - Engineering",
]

EMPLOYMENT_TYPES = ["Full-time", "Intern"]

# Indian leave types -> (annual quota, is LWP)
LEAVE_TYPES = [
    ("Casual Leave", 12),
    ("Sick Leave", 8),
    ("Earned Leave", 18),
    ("Comp Off", 3),
]

# Holiday list (FY 2026-27 sample, dates in 2026)
HOLIDAYS = [
    ("2026-08-15", "Independence Day"),
    ("2026-08-26", "Ganesh Chaturthi"),
    ("2026-10-02", "Gandhi Jayanti"),
    ("2026-10-20", "Diwali (Lakshmi Pujan)"),
    ("2026-10-21", "Diwali (Balipratipada)"),
    ("2026-12-25", "Christmas"),
]

# id, name, designation, department, location(branch), status, manager_id, type, annual_ctc, doj
PEOPLE = [
    ("HR-1320", "Nikhil Shah",     "VP Engineering",       "Leadership",       "Mumbai",    "Active", None,      "Full-time", 6000000, "2015-06-01"),
    ("HR-1001", "Devika Rao",      "Engineering Manager",  "Engineering",      "Mumbai",    "Active", "HR-1320", "Full-time", 3600000, "2019-01-05"),
    ("HR-1119", "Meera Nair",      "Design Lead",          "Design",           "Mumbai",    "Active", "HR-1320", "Full-time", 3000000, "2018-11-11"),
    ("HR-1178", "Priya Menon",     "Sales Director",       "Sales",            "Delhi",     "Active", "HR-1320", "Full-time", 4200000, "2017-02-08"),
    ("HR-1289", "Rahul Khanna",    "Finance Controller",   "Finance",          "Mumbai",    "Active", "HR-1320", "Full-time", 3900000, "2016-04-12"),
    ("HR-1203", "Fatima Sheikh",   "HR Business Partner",  "People",           "Mumbai",    "Active", "HR-1320", "Full-time", 1860000, "2021-01-14"),
    ("HR-1345", "Amit Trivedi",    "Customer Success Lead","Customer Success", "Bengaluru", "Active", "HR-1320", "Full-time", 2520000, "2020-09-07"),
    ("HR-1042", "Aarav Mehta",     "Product Engineer",     "Engineering",      "Mumbai",    "Active", "HR-1001", "Full-time", 1704000, "2022-04-12"),
    ("HR-1067", "Karthik Iyer",    "Senior Engineer",      "Engineering",      "Bengaluru", "Active", "HR-1001", "Full-time", 2400000, "2020-08-22"),
    ("HR-1102", "Rohan Gupta",     "QA Engineer",          "Engineering",      "Pune",      "Active", "HR-1001", "Full-time", 1380000, "2022-07-15"),
    ("HR-1156", "Ananya Desai",    "Frontend Engineer",    "Engineering",      "Bengaluru", "Active", "HR-1001", "Full-time", 1560000, "2023-09-19"),
    ("HR-1190", "Arjun Reddy",     "DevOps Engineer",      "Engineering",      "Hyderabad", "Active", "HR-1001", "Full-time", 2160000, "2021-10-27"),
    ("HR-1221", "Aditya Joshi",    "Backend Engineer",     "Engineering",      "Pune",      "Active", "HR-1001", "Full-time", 1920000, "2022-05-05"),
    ("HR-1334", "Sneha Reddy",     "Data Analyst",         "Engineering",      "Hyderabad", "Active", "HR-1001", "Full-time", 1440000, "2024-02-14"),
    ("HR-1088", "Sana Kapoor",     "Product Designer",     "Design",           "Mumbai",    "Active", "HR-1119", "Full-time", 1980000, "2021-03-03"),
    ("HR-1356", "Kavya Pillai",    "UX Researcher",        "Design",           "Mumbai",    "Active", "HR-1119", "Full-time", 1740000, "2022-04-19"),
    ("HR-1134", "Vikram Singh",    "Account Executive",    "Sales",            "Delhi",     "Active", "HR-1178", "Full-time", 1620000, "2022-06-02"),
    ("HR-1301", "Manish Agarwal",  "Sales Executive",      "Sales",            "Delhi",     "Active", "HR-1178", "Full-time",  960000, "2026-03-02"),
    ("HR-1245", "Neha Verma",      "Marketing Manager",    "Marketing",        "Mumbai",    "Active", "HR-1178", "Full-time", 2280000, "2020-07-30"),
    ("HR-1312", "Divya Krishnan",  "Content Strategist",   "Marketing",        "Bengaluru", "Active", "HR-1245", "Full-time", 1320000, "2022-11-25"),
    ("HR-1277", "Ishita Banerjee", "Finance Analyst",      "Finance",          "Mumbai",    "Active", "HR-1289", "Full-time", 1500000, "2021-08-09"),
    ("HR-1294", "Pooja Patil",     "Recruiter",            "People",           "Pune",      "Active", "HR-1203", "Full-time", 1080000, "2023-06-18"),
    ("HR-1260", "Sandeep Kumar",   "Support Engineer",     "Customer Success", "Bengaluru", "Active", "HR-1001", "Full-time", 1140000, "2023-03-21"),
    ("HR-1361", "Rishi Malhotra",  "Intern - Engineering", "Engineering",      "Remote",    "Active", "HR-1221", "Intern",     480000, "2026-01-06"),
]


def _exists(doctype, name):
    return frappe.db.exists(doctype, name)


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


GRADES = ["L1", "L2", "L3", "L4", "L5"]


def _grade_for_ctc(ctc):
    if ctc >= 3500000:
        return "L5"
    if ctc >= 2200000:
        return "L4"
    if ctc >= 1500000:
        return "L3"
    if ctc >= 1000000:
        return "L2"
    return "L1"


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


# Persona logins: (employee_id, email, password, [roles]). Lets you sign in as
# the ESS persona (Aarav), a manager (Devika), and an HR admin to see each
# role's workspace against real data.
PERSONA_USERS = [
    ("HR-1042", "aarav.mehta@frappe.io", "Frappe@123", ["Employee"]),
    ("HR-1001", "devika.rao@frappe.io", "Frappe@123", ["Employee", "Leave Approver", "Expense Approver"]),
    ("HR-1203", "fatima.sheikh@frappe.io", "Frappe@123", ["Employee", "HR Manager", "HR User"]),
]


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


ANNOUNCEMENTS = [
    ("Updated work-from-home policy effective 1 July",
     "We're moving to a 3-days-in-office model for all Mumbai and Bengaluru teams starting 1 July 2026. Tuesdays and Thursdays are anchor days; the third day is flexible. Remote-first roles are unaffected."),
    ("May payslips released - investment proofs open",
     "Your May 2026 payslip is now available under Payslips. The window to submit investment proofs for FY 2025-26 is open until 31 December. Submitting early helps spread your TDS evenly."),
    ("Quarterly town hall - Saturday 6 June, 4:00 PM",
     "Join us for the Q1 review and product roadmap. In-person at the Mumbai office auditorium, or on the livestream for remote teammates. We'll close with an open AMA."),
    ("New mental wellness benefit - 6 free therapy sessions",
     "We've partnered with a wellness provider to offer every employee 6 confidential counselling sessions per year, fully covered. Book directly through the benefits portal."),
]


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


def run():
    print("Seeding Frappe HR sample data ...")
    ensure_company()
    ensure_simple("Department", DEPARTMENTS)
    ensure_simple("Designation", DESIGNATIONS)
    ensure_simple("Branch", [l for l in LOCATIONS if l != "Remote"])
    ensure_simple("Employment Type", EMPLOYMENT_TYPES)
    hl = ensure_holiday_list()
    # Make it the company default so leave + salary-slip working-day lookups resolve.
    if frappe.db.exists("Company", COMPANY):
        frappe.db.set_value("Company", COMPANY, "default_holiday_list", hl)
        frappe.db.commit()
    ensure_holiday_assignment(hl)
    ensure_leave_types()
    id_to_name = ensure_employees()
    ensure_grades(id_to_name)
    ensure_profile_details(id_to_name)
    ensure_salary_structure(id_to_name)
    ensure_leave_allocations(id_to_name)
    ensure_leave_applications(id_to_name)
    ensure_attendance(id_to_name)
    ensure_salary_slips(id_to_name)
    ensure_expense_claims(id_to_name)
    ensure_recruitment()
    ensure_announcements()
    ensure_issues(id_to_name)
    ensure_appraisal(id_to_name)
    ensure_lifecycle(id_to_name)
    ensure_users(id_to_name)
    frappe.db.commit()
    print("Done. Sign in as aarav.mehta@frappe.io / Frappe@123 and open /people")
