"""Golden self-test for the Frappe HR UI backend.

Exercises every screen aggregator (reads), every action endpoint (writes —
create → assert → cleanup), RBAC, and the generic doctype engine, as the three
demo personas. Run after any change:

    bench --site <site> execute frappe_hr_ui.selftest.run

Prints a PASS/FAIL report and returns a summary dict. Creates throwaway records
and deletes them; safe to run repeatedly. Requires the demo personas + seed data.
"""

import frappe
from frappe_hr_ui import api
from frappe_hr_ui import doctype_api as dx
from frappe_hr_ui import access_api as ax
from frappe_hr_ui import india_defaults as idf
from frappe_hr_ui import employee_import as ei

EMP = "aarav.mehta@frappe.io"
MGR = "devika.rao@frappe.io"
HR = "fatima.sheikh@frappe.io"


def run():
    R = {"read": [0, 0], "write": [0, 0], "rbac": [0, 0], "engine": [0, 0], "input": [0, 0], "fails": [], "skips": []}
    trash = []

    def ok(bucket): R[bucket][0] += 1
    def bad(bucket, msg): R[bucket][1] += 1; R["fails"].append(msg)
    def skip(name, why): R["skips"].append(f"{name}: {why}")

    def read(user, name, fn):
        frappe.set_user(user)
        try:
            fn(); ok("read")
        except Exception as e:
            bad("read", f"READ {name}: {type(e).__name__}: {str(e)[:80]}")

    def write(user, name, make, doctype=None):
        frappe.set_user(user)
        try:
            res = make(); ok("write")
            if doctype:
                nm = res.get("name") if isinstance(res, dict) else res
                if isinstance(nm, str):
                    trash.append((doctype, nm))
            return res
        except Exception as e:
            bad("write", f"WRITE {name}: {type(e).__name__}: {str(e)[:90]}")

    def rbac(name, fn, expect_block=True):
        try:
            fn(); blocked = False
        except Exception:
            blocked = True
        if blocked == expect_block:
            ok("rbac")
        else:
            bad("rbac", f"RBAC {name}: expected {'block' if expect_block else 'allow'}")

    def as_user(u, fn):
        frappe.set_user(u)
        try:
            return fn()
        finally:
            frappe.set_user("Administrator")

    def validates(user, name, make, doctype=None):
        """A write that SHOULD be rejected. Pass = it raised; fail = it slipped through."""
        frappe.set_user(user)
        try:
            res = make()
        except Exception:
            ok("input"); return
        bad("input", f"INPUT {name}: invalid input was accepted")
        if doctype:
            nm = res.get("name") if isinstance(res, dict) else res
            if isinstance(nm, str):
                trash.append((doctype, nm))

    # Preconditions: a green report is meaningless if the personas or seed data
    # are absent, because the checks would just not run. Fail hard and early.
    frappe.set_user("Administrator")
    missing_users = [u for u in (EMP, MGR, HR) if not frappe.db.exists("User", u)]
    emp_obj = frappe.db.get_value("Employee", {"status": "Active"}, "name")
    if missing_users or not emp_obj:
        problems = []
        if missing_users:
            problems.append(f"demo personas not found: {missing_users}")
        if not emp_obj:
            problems.append("no Active Employee")
        raise SystemExit("Self-test preconditions missing — " + "; ".join(problems) + ". Seed demo data first.")

    # ---------------- READS ----------------
    for n, f in [("home", api.get_employee_home), ("profile", api.get_employee_profile),
                 ("attendance", api.get_employee_attendance), ("leave", api.get_employee_leave),
                 ("payslips", api.get_payslips), ("tax", api.get_tax_screen),
                 ("claims", api.get_expense_claims_screen), ("perf", api.get_employee_performance),
                 ("tickets", api.get_my_tickets), ("directory", api.get_directory),
                 ("announcements", api.get_announcements_feed)]:
        read(EMP, n, f)
    for n, f in [("team_overview", api.get_team_overview), ("team_approvals", api.get_team_approvals),
                 ("team_attendance", api.get_team_attendance), ("team_leave", api.get_team_leave),
                 ("team_performance", api.get_team_performance), ("org_chart", api.get_org_chart)]:
        read(MGR, n, f)
    for n, f in [("hr_dashboard", api.get_hr_dashboard), ("hr_directory", api.get_hr_directory),
                 ("onboarding", api.get_onboarding), ("transfers", api.get_transfers),
                 ("separation", api.get_separation), ("payroll_run", api.get_payroll_run),
                 ("bankfile", api.get_bankfile), ("jobs", api.get_jobs), ("offers", api.get_offers),
                 ("analytics", api.get_analytics), ("settings", api.get_settings)]:
        read(HR, n, f)
    for rep in ("Salary Register", "Employee Information", "Income Tax Computation"):
        read(HR, f"report:{rep}", lambda r=rep: api.get_report_data(r))
    read(HR, "defaults_status", lambda: idf.defaults_status())
    read(HR, "import_template", lambda: ei.import_template())

    # ---------------- WRITES (create -> cleanup) ----------------
    write(EMP, "toggle_checkin", lambda: {"name": _last_checkin(emp_obj)})
    leave_types = api.get_leave_types().get("types") or []
    if leave_types:
        lt = leave_types[0]["value"]
        write(EMP, "apply_leave", lambda: api.apply_leave(lt, "2026-07-20", "2026-07-20", "selftest"), "Leave Application")
    else:
        skip("apply_leave", "no leave types seeded")
    write(EMP, "submit_regularization", lambda: api.submit_regularization("2026-06-09", "Work From Home", "selftest"), "Attendance Request")
    et = (api.get_expense_types().get("types") or [{}])[0].get("value")
    if et:
        write(EMP, "submit_expense_claim", lambda: api.submit_expense_claim(et, 50, "2026-06-09", "selftest"), "Expense Claim")
    else:
        skip("submit_expense_claim", "no expense claim types seeded")
    tkt = write(EMP, "raise_ticket", lambda: api.raise_ticket("selftest", "b", "Low"), "Issue")
    if tkt:
        write(EMP, "reply_ticket", lambda: api.reply_ticket(tkt["name"], "r"))
    cell = frappe.db.get_value("Employee", {"user_id": EMP}, "cell_number")
    write(EMP, "update_my_profile", lambda: api.update_my_profile(cell_number="9000000009"))
    frappe.set_user(EMP); api.update_my_profile(cell_number=cell or "")
    write(EMP, "ess create:Employee Advance",
          lambda: api.create_doc("Employee Advance", frappe.as_json({"purpose": "selftest", "advance_amount": 100})), "Employee Advance")
    read(EMP, "get_my_docs:Employee Advance", lambda: api.get_my_docs("Employee Advance"))
    write(HR, "create_employee", lambda: api.create_employee(first_name="Self", last_name="Test",
        gender=frappe.db.get_value("Gender", {}, "name"), date_of_birth="1995-01-01", date_of_joining="2026-06-01"), "Employee")
    write(HR, "create_doc:Department", lambda: api.create_doc("Department", frappe.as_json({"department_name": "Selftest Dept"})), "Department")
    # employee bulk import (one valid row -> cleanup)
    frappe.set_user(HR)
    try:
        gender = frappe.db.get_value("Gender", {}, "name")
        res = ei.import_employees(frappe.as_json([{"first_name": "Selftest", "last_name": "Import",
            "gender": gender, "date_of_birth": "1995-01-01", "date_of_joining": "2026-06-01"}]))
        if res["created"] == 1:
            ok("write"); trash.append(("Employee", res["names"][0]["name"]))
        else:
            bad("write", f"import_employees created={res['created']} errors={res['errors']}")
    except Exception as e:
        bad("write", f"import_employees: {type(e).__name__}: {str(e)[:80]}")

    # ---------------- GENERIC ENGINE ----------------
    frappe.set_user(HR)
    try:
        dx.get_meta("Leave Type"); ok("engine")
    except Exception as e:
        bad("engine", f"engine.get_meta: {e}")
    try:
        dx.get_list("Salary Component", page_length=5); ok("engine")
    except Exception as e:
        bad("engine", f"engine.get_list: {e}")
    try:
        r = dx.save_doc("Designation", frappe.as_json({"designation_name": "Selftest Role"}))
        dx.delete_doc("Designation", r["name"]); ok("engine")
    except Exception as e:
        bad("engine", f"engine.save/delete: {e}")
        try:
            frappe.set_user("Administrator"); frappe.delete_doc("Designation", "Selftest Role", force=True, ignore_permissions=True)
        except Exception:
            pass

    # ---------------- ACCESS MANAGEMENT ----------------
    frappe.set_user("Administrator")
    email = "selftest.user@example.com"
    def _drop_user():
        try:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True, ignore_permissions=True, delete_permanently=True)
                frappe.db.commit()
        except Exception:
            frappe.db.rollback()
    _drop_user()
    try:
        ax.create_user(email, "Self", "Test", frappe.as_json(["HR User"]))
        ax.set_user_access(email, frappe.as_json(["Leave Approver"]))
        roles = ax.get_user_access(email)["roles"]
        ok("engine") if roles == ["Leave Approver"] else bad("engine", f"access roles {roles}")
    except Exception as e:
        bad("engine", f"access mgmt: {type(e).__name__}: {str(e)[:80]}")
    _drop_user()

    # ---------------- RBAC ----------------
    frappe.set_user("Administrator")
    rbac("employee blocked from user admin", lambda: as_user(EMP, lambda: ax.list_users()), True)
    iss = frappe.get_doc({"doctype": "Issue", "subject": "rbac", "raised_by": HR, "status": "Open"}).insert(ignore_permissions=True)
    frappe.db.commit(); trash.append(("Issue", iss.name))
    rbac("employee reads other's ticket", lambda: as_user(EMP, lambda: api.get_ticket_thread(iss.name)), True)
    rbac("employee replies to other's ticket", lambda: as_user(EMP, lambda: api.reply_ticket(iss.name, "intrusion")), True)
    rbac("employee calls HR dashboard", lambda: as_user(EMP, lambda: api.get_hr_dashboard()), True)
    rbac("employee opens HR employee-360", lambda: as_user(EMP, lambda: api.get_employee_360(emp_obj)), True)
    rbac("employee opens HR doc detail", lambda: as_user(EMP, lambda: api.get_doc_detail("Employee", emp_obj)), True)
    rbac("employee creates via engine", lambda: as_user(EMP, lambda: dx.save_doc("Designation", frappe.as_json({"designation_name": "X"}))), True)
    rbac("engine blocks non-HR doctype", lambda: as_user(HR, lambda: dx.get_list("User")), True)
    # Salary IDOR: an employee must not read another employee's payslip.
    frappe.set_user("Administrator")
    _emp_of_emp = frappe.db.get_value("Employee", {"user_id": EMP}, "name")
    _other_slip = frappe.db.get_value("Salary Slip", {"employee": ["!=", _emp_of_emp or "__none__"], "docstatus": 1}, "name")
    if _other_slip:
        rbac("employee reads other's payslip", lambda: as_user(EMP, lambda: api.get_payslip_detail(_other_slip)), True)
    else:
        skip("employee reads other's payslip", "no other employee's submitted Salary Slip found")
    frappe.set_user(EMP)
    people = api.get_directory().get("people") or []
    if not people:
        skip("directory hides PII", "directory returned no people")
    else:
        person = people[0]
        def assert_no_pii():
            if "user_id" in person or "cell_number" in person:
                raise Exception("PII leaked in directory payload")
        rbac("directory hides PII", assert_no_pii, False)

    # ---------------- NEGATIVE INPUTS (each call must be rejected) ----------------
    frappe.set_user("Administrator")
    gender = frappe.db.get_value("Gender", {}, "name")
    if leave_types:
        good_lt = leave_types[0]["value"]
        validates(EMP, "apply_leave reversed dates",
                  lambda: api.apply_leave(good_lt, "2026-07-22", "2026-07-20", "selftest"), "Leave Application")
    else:
        skip("apply_leave reversed dates", "no leave types seeded")
    validates(EMP, "apply_leave unknown leave type",
              lambda: api.apply_leave("__no_such_leave_type__", "2026-07-20", "2026-07-20", "selftest"), "Leave Application")
    validates(HR, "create_employee empty first name",
              lambda: api.create_employee(first_name="", gender=gender, date_of_birth="1995-01-01", date_of_joining="2026-06-01"), "Employee")
    validates(HR, "create_employee birth after joining",
              lambda: api.create_employee(first_name="Bad", last_name="Dates", gender=gender, date_of_birth="2030-01-01", date_of_joining="2026-06-01"), "Employee")

    # ---------------- cleanup ----------------
    frappe.set_user("Administrator")
    orphans = []
    for dt, nm in trash:
        try:
            d = frappe.get_doc(dt, nm)
            if getattr(d, "docstatus", 0) == 1:
                d.cancel()
            frappe.delete_doc(dt, nm, force=True, ignore_permissions=True)
        except Exception as e:
            orphans.append(f"{dt} {nm}: {type(e).__name__}")
    frappe.db.commit()
    if orphans:
        bad("write", f"cleanup left {len(orphans)} orphan record(s): {'; '.join(orphans)}")

    buckets = ("read", "write", "engine", "rbac", "input")
    total_fail = sum(R[k][1] for k in buckets)
    print("\n===== FRAPPE HR UI SELF-TEST =====")
    for k in buckets:
        print(f"{k.upper():8} {R[k][0]} pass / {R[k][1]} fail")
    print(f"SKIPPED  {len(R['skips'])}")
    for f in R["fails"]:
        print("  ✗", f)
    for s in R["skips"]:
        print("  ⊘", s)
    if total_fail:
        verdict = f"{total_fail} FAILURE(S) ⚠"
    elif R["skips"]:
        verdict = f"PASS but {len(R['skips'])} check(s) SKIPPED — coverage incomplete ⚠"
    else:
        verdict = "ALL PASS ✅"
    print("VERDICT:", verdict)
    return R


def ci():
    """CI entrypoint — exits non-zero on any failure OR skipped check.

    A skip means a check could not run (missing seed/data), so coverage is
    incomplete and the run cannot certify the backend. Treat it as not-green.
    """
    R = run()
    fails = sum(R[k][1] for k in ("read", "write", "engine", "rbac", "input"))
    problems = []
    if fails:
        problems.append(f"{fails} failure(s):\n" + "\n".join(R["fails"]))
    if R["skips"]:
        problems.append(f"{len(R['skips'])} skipped check(s) — coverage incomplete:\n" + "\n".join(R["skips"]))
    if problems:
        raise SystemExit("Self-test NOT production-ready —\n" + "\n\n".join(problems))
    print("Self-test passed — all checks ran, 0 skipped.")


def _last_checkin(_=None):
    api.toggle_checkin()
    emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    rows = frappe.get_all("Employee Checkin", filters={"employee": emp}, order_by="creation desc", limit=1)
    return rows[0].name if rows else None
