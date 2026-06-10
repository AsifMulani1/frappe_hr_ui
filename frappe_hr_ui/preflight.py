"""
Rollout smoke-test pre-flight.

Inspects the live site and prints a data-backed walkthrough for Parts 1-3 of
docs/ROLLOUT_SMOKETEST.md: who to log in as, the concrete values each checkpoint
should show, and a ❌ on any checkpoint that can't be tested yet because the data
isn't there (so you can tell "missing data" apart from "broken feature").

    bench --site <site> execute frappe_hr_ui.preflight.run
"""

import frappe
from frappe_hr_ui import api


def _as(user, fn):
    frappe.set_user(user)
    try:
        return fn()
    except Exception as e:
        return {"__error__": f"{type(e).__name__}: {str(e)[:120]}"}
    finally:
        frappe.set_user("Administrator")


def _line(ok, text):
    print(f"  [{'OK ' if ok else 'XX '}] {text}")


def run():
    print("\n" + "=" * 72)
    print("ROLLOUT PRE-FLIGHT — data-backed walkthrough for Parts 1-3")
    print("=" * 72)

    # ---------------------------------------------------------------- Part 1
    print("\n── PART 1 · Employee daily loops ──────────────────────────────")
    # an active employee linked to a login, ideally with a payslip
    slip_emps = {s.employee for s in frappe.get_all("Salary Slip", {"docstatus": 1}, ["employee"])}
    cand = frappe.get_all(
        "Employee",
        filters={"status": "Active", "user_id": ["is", "set"]},
        fields=["name", "employee_name", "user_id"],
        limit=50,
    )
    emp = next((e for e in cand if e.name in slip_emps), cand[0] if cand else None)
    if not emp:
        _line(False, "No Active employee is linked to a User login — create one (Employee.user_id) to test ESS.")
    else:
        u = emp.user_id
        print(f"  → Log in as:  {u}   ({emp.employee_name})")
        home = _as(u, api.get_employee_home)
        if "__error__" in home:
            _line(False, f"Home failed to load: {home['__error__']}")
        else:
            today = home.get("today") or {}
            _line(True, f"1. Clock in/out: currently {'CHECKED IN' if today.get('checked_in') else 'checked out'} — toggle it, expect a toast + state flip")
        lv = _as(u, api.get_employee_leave)
        if "__error__" in lv:
            _line(False, f"2. Leave screen errors: {lv['__error__']}")
        else:
            bals = lv.get("balances") or lv.get("balance") or []
            n = len(bals) if isinstance(bals, list) else "—"
            _line(bool(bals), f"2. Leave: {n} leave-type balance(s) shown — Apply should open a drawer & submit")
        ps = _as(u, api.get_payslips)
        slips = (ps or {}).get("slips") or []
        if slips:
            latest = slips[0]
            _line(True, f"3. Payslips: {len(slips)} slip(s); latest {latest.get('month')} net ₹{latest.get('net_pay'):,.0f} — open it, Download PDF")
        else:
            _line(False, "3. Payslips: this employee has none — pick one with a submitted Salary Slip, or this checkpoint shows the empty state")

    # ---------------------------------------------------------------- Part 2
    print("\n── PART 2 · Manager loop ──────────────────────────────────────")
    # someone who manages people or approves
    approver_roles = {"Leave Approver", "Expense Approver", "HR Manager", "HR User"}
    mgr = None
    for e in cand:
        roles = set(frappe.get_roles(e.user_id))
        if approver_roles & roles:
            mgr = e
            break
    has_reports = None
    if not mgr:
        # anyone with direct reports
        rep = frappe.get_all("Employee", {"reports_to": ["is", "set"], "status": "Active"}, ["reports_to"], limit=1)
        if rep:
            has_reports = rep[0].reports_to
            mgr = frappe.db.get_value("Employee", has_reports, ["name", "employee_name", "user_id"], as_dict=True)
    if not mgr or not mgr.get("user_id"):
        _line(False, "No login-linked manager/approver found — assign a Leave Approver role or set reports_to to test approvals.")
    else:
        print(f"  → Log in as:  {mgr['user_id']}   ({mgr['employee_name']})")
        appr = _as(mgr["user_id"], api.get_team_approvals)
        items = (appr or {}).get("items") or []
        if "__error__" in (appr or {}):
            _line(False, f"Approvals failed: {appr['__error__']}")
        elif items:
            _line(True, f"Approvals: {len(items)} pending — Approve/Reject one, expect a toast + the row clearing")
        else:
            _line(False, "Approvals: queue is empty — have an employee apply for leave first, then re-check (not a bug, just no data)")

    # ---------------------------------------------------------------- Part 3
    print("\n── PART 3 · HR / admin (new IA) ───────────────────────────────")
    hr_user = next((e.user_id for e in cand if {"HR Manager", "HR User"} & set(frappe.get_roles(e.user_id))), None)
    print(f"  → Log in as:  {hr_user or 'an HR Manager / HR User (none linked — Administrator works in a pinch)'}")
    hr = _as(hr_user or "Administrator", api.get_hr_dashboard)
    pay = _as(hr_user or "Administrator", api.get_payroll_dashboard)
    rec = _as(hr_user or "Administrator", api.get_recruitment_dashboard)
    _line("__error__" not in hr, f"People dashboard: {hr.get('headcount', '—')} headcount, {hr.get('open_jobs', '—')} open jobs")
    _line("__error__" not in pay, f"Payroll dashboard: {pay.get('period', '—')}, net ₹{(pay.get('totals') or {}).get('net', 0):,.0f}, {pay.get('on_payroll', '—')} on payroll")
    _line("__error__" not in rec, f"Recruitment dashboard: {(rec.get('stats') or {}).get('open_jobs', '—')} open positions, {(rec.get('stats') or {}).get('applicants', '—')} applicants")
    _line(True, "Settings hub: open the gear (bottom-left) — expect categories Organization/Time & leave/Payroll/Performance/System")
    _line(True, "Inline create: on a Link field click ＋, a 2nd drawer opens, create → auto-selected back in the field")

    print("\n" + "=" * 72)
    print("Anything marked XX above is a data gap, not necessarily a bug — seed it,")
    print("or note the checkpoint as N/A. Everything else: click through and confirm.")
    print("=" * 72 + "\n")


def seed_pending_approval():
    """Seed ONE pending leave request for a manager's report so Part 2
    (approve/reject) is testable in the UI. Safe to approve OR reject."""
    frappe.set_user("Administrator")
    pooja = frappe.db.get_value("Employee", {"employee_name": "Pooja Patil"}, "name")
    fatima = "fatima.sheikh@frappe.io"
    if not pooja:
        print("Couldn't find Pooja Patil — adjust this seeder to a real report of your manager.")
        return
    existing = frappe.get_all("Leave Application", {"employee": pooja, "status": "Open", "docstatus": 0}, ["name"])
    if existing:
        print(f"Already pending: {existing[0].name} — log in as {fatima} → Team → Approvals.")
        return

    def _make(with_approver):
        d = {
            "doctype": "Leave Application", "employee": pooja, "leave_type": "Casual Leave",
            "from_date": "2026-09-15", "to_date": "2026-09-15", "status": "Open",
            "description": "Rollout smoke-test — safe to approve or reject.",
        }
        if with_approver:
            d["leave_approver"] = fatima
        doc = frappe.get_doc(d)
        doc.insert(ignore_permissions=True)
        return doc

    try:
        doc = _make(True)
    except Exception:
        frappe.db.rollback()
        doc = _make(False)
    frappe.db.commit()

    frappe.set_user(fatima)
    n = len((api.get_team_approvals() or {}).get("items", []))
    frappe.set_user("Administrator")
    print(f"✅ Seeded {doc.name} (Pooja Patil, 1-day Casual Leave).")
    print(f"   Fatima's approval queue now shows {n} item(s).")
    print(f"→ Log in as {fatima} → Team → Approvals → Approve or Reject it (either clears it).")
