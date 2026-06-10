# Employee Workspace — Functional Test Guide

How to functionally test the Employee Self-Service (ESS) workspace of Frappe HR UI and
confirm it's working. Covers the 11 employee screens served at **`/people`**.

## 0. Setup

1. Make sure the bench is running: `bench start` (web on `:8002`).
2. Rebuild the SPA if you changed frontend code:
   ```bash
   cd apps/frappe_hr_ui/frontend && yarn build
   bench --site hrms.localhost clear-cache
   ```
3. Open **http://hrms.localhost:8002/people** and log in as the **employee persona**:
   - `aarav.mehta@frappe.io` / `Frappe@123`  (Employee workspace)
   - For RBAC checks also have: `devika.rao@frappe.io` (Manager), `fatima.sheikh@frappe.io` (HR).

> Tip: open DevTools → Network, filter to `/api/method/frappe_hr_ui`. Every screen should
> fire its aggregator and return HTTP 200 with a JSON `message`. A 403/417/500 is a bug.

---

## 1. Manual test — per screen

For **every** screen, first confirm the 3 universal states (now standardized via `AsyncShell`):
- **Loading**: a brief "Loading…" centered message (not a flash of empty tables).
- **Error**: kill the network (DevTools → offline) and reload → a red "Couldn't load this page" with a **Retry** that re-fetches.
- **No employee linked**: log in as a user with no Employee (e.g. Administrator) → "No employee record linked" message (not fabricated zeros).

### Home (`/`)
- [ ] Greeting + date line show your name/location/shift.
- [ ] **Check in / Check out** toggles and the ring/worked-minutes update (creates an Employee Checkin).
- [ ] Quick Actions tiles navigate (Leave, Payslip, Reimbursement, Expense, Ticket, Regularize).
- [ ] "Apply for leave" → goes to Leave; "View history"/"Break"/"Regularize" → Attendance.
- [ ] Leave balance "Apply", Announcements "All", payslip "View"/"Download", Celebrations "Congrats" all act.

### My Profile (`/profile`)
- [ ] Personal / Job / Bank & tax / Documents tabs render real data.
- [ ] **Edit details** → drawer pre-fills; bad email is rejected; Save persists and the card refreshes.
- [ ] **Documents** button switches to the Documents tab; **Upload** attaches a file and it appears in the list.
- [ ] Reporting line + peers + tenure show.

### Attendance (`/attendance`)
- [ ] Stat tiles + daily log table populate; **calendar grid aligns to weekdays** and shows the correct number of days for the month.
- [ ] **Export** downloads a CSV of the daily log.
- [ ] **Regularize** → drawer; a **future date is rejected**; a valid request submits and the list refreshes.

### Leave (`/leave`)
- [ ] Balance total + per-type bars; requests table with status badges; "Team on leave".
- [ ] **Apply for leave** → drawer; **end-date-before-start is rejected**; submit creates a Leave Application (Open) and refreshes.

### Payslips (`/payslips`)
- [ ] Slip list on the left; selecting one shows earnings/deductions/net.
- [ ] Header shows the **real company name** (not a hardcoded one); status badge is green only when Paid.
- [ ] **Download PDF** (disabled until a slip is selected) opens the server-rendered PDF.

### Tax & benefits (`/tax`)
- [ ] All four tiles are real (TDS paid, total declared, flexible-benefits total, declarations count) — no hardcoded "New regime" / "31 Dec".
- [ ] Declarations table + FBP list (shows "No flexible benefits configured" when none).
- [ ] **Update declaration** → drawer (pick payroll period) creates a Tax Exemption Declaration **for yourself**.

### Reimbursements (`/reimbursements`) & Expenses (`/expenses`)
- [ ] Summary tiles + claims table.
- [ ] **New** → drawer; **zero/negative amount and empty date are rejected**; valid claim submits and refreshes.

### Performance (`/performance`)
- [ ] Tiles (overall %, goals, cycle, feedback) + goals with progress bars.
- [ ] **Start self-appraisal** → drawer (pick cycle) creates an Appraisal **for yourself**.

### Helpdesk (`/helpdesk`)
- [ ] Ticket list + thread; **Raise a ticket** creates an Issue.
- [ ] Type a reply + Enter (or Send) → reply appears in the thread; input disabled when no ticket selected.

### Directory (`/directory`)
- [ ] Grid/List toggle; department chips filter; search filters by name/role/dept.
- [ ] Click a person → drawer with details; **Copy email** / **Send email** work.

### Announcements (`/announcements`)
- [ ] Company posts render; Acknowledge / Share / Quick links act (lightweight, client-side).

---

## 2. Security checks (RBAC — must pass)

- [ ] As `aarav`, every screen shows **only Aarav's** data (his payslips, leave, claims, tickets).
- [ ] **Ticket isolation**: aarav cannot open another user's ticket thread (returns *Not permitted*). Verified server-side in `get_ticket_thread`.
- [ ] **Directory** payload does not include other employees' login id (`user_id`) or personal `cell_number`.
- [ ] `get_payslip_detail` throws if you pass a slip that isn't yours.

---

## 3. API smoke test (no browser needed)

Run every ESS endpoint as the employee and confirm none error. Save as a temp file and run with `bench execute`:

```python
# apps/frappe_hr_ui/frappe_hr_ui/_smoke.py
import frappe
from frappe_hr_ui import api

def run():
    frappe.set_user("aarav.mehta@frappe.io")
    for name, fn in [
        ("home", api.get_employee_home), ("profile", api.get_employee_profile),
        ("attendance", api.get_employee_attendance), ("leave", api.get_employee_leave),
        ("payslips", api.get_payslips), ("tax", api.get_tax_screen),
        ("claims", api.get_expense_claims_screen), ("performance", api.get_employee_performance),
        ("tickets", api.get_my_tickets), ("directory", api.get_directory),
        ("announcements", api.get_announcements_feed),
    ]:
        try:
            fn(); print("OK", name)
        except Exception as e:
            print("ERR", name, type(e).__name__, e)
```
```bash
bench --site hrms.localhost execute frappe_hr_ui._smoke.run
rm apps/frappe_hr_ui/frappe_hr_ui/_smoke.py
```

Write flows can be tested the same way (each creates a real record — delete it after):
`api.apply_leave(...)`, `api.submit_expense_claim(...)`, `api.raise_ticket(...)` + `api.reply_ticket(...)`,
`api.submit_regularization(...)`, `api.update_my_profile(...)`, `api.toggle_checkin()`,
`api.create_doc("Appraisal", ...)`, `api.create_doc("Employee Tax Exemption Declaration", ...)`.

### HTTP-level (curl) smoke
```bash
curl -s -c /tmp/cj -b /tmp/cj -X POST http://hrms.localhost:8002/api/method/login \
  -H 'Content-Type: application/json' \
  -d '{"usr":"aarav.mehta@frappe.io","pwd":"Frappe@123"}'
curl -s -b /tmp/cj http://hrms.localhost:8002/api/method/frappe_hr_ui.api.get_employee_home | head -c 300
```

---

## 4. What was hardened for production (this pass)

- **Security:** `get_ticket_thread` now enforces ticket ownership (was a cross-user leak); `get_directory` no longer returns `user_id`/`cell_number`.
- **No fabricated data:** payslip uses the real company; tax tiles are all data-driven; tax FBP is derived from the salary slip's flexible-benefit components (empty if none).
- **Consistent states:** new shared `AsyncShell` gives every screen real loading / error (with Retry) / no-employee states instead of fake empty data.
- **Validation:** leave end≥start, no future-dated regularization, expense amount > 0 with a required date, profile email format.
- **Robustness:** guarded array bindings (payslip earnings/deductions), numeric coercion (leave/FBP totals), correct attendance calendar (weekday-aligned, real day count).
- **A11y/UX:** drawer closes on Escape, close button is `type=button` + aria-label, table rows only show a pointer when actually clickable.
- **Bug fix:** `EssPerformance` crashed (`reactive` not imported) — fixed.

## 5. Known limitations (not blockers)
- Announcements "Acknowledge" and "Quick links" are client-side only (no persistence/doc store).
- Performance "Request feedback" and Tax "Form 16" are acknowledgement stubs (no year-end Form-16 doc exists mid-year).
- Directory department chips show the first 6 only.
