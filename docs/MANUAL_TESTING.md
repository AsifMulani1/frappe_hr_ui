# Manual Test Guide — Frappe HR UI

Covers everything built across the platform work (config console, onboarding wizard,
access management, ESS requests, HR cases, in-app reports, search, branding). For the
employee self-service screens specifically, see `EMPLOYEE_WORKSPACE_TESTING.md`.

## 0. Setup

- **App URL:** http://hrms.localhost:8002/people  (hard-refresh once: Cmd/Ctrl-Shift-R)
- **Logins** (password `Frappe@123`):
  - `fatima.sheikh@frappe.io` — HR & Payroll
  - `aarav.mehta@frappe.io` — Employee
  - `devika.rao@frappe.io` — Manager
  - **Administrator** — needed for **Users & access** (System Manager). Log in at `/login`
    then open `/people`.
- After any rebuild: `bench --site hrms.localhost clear-cache` and hard-refresh.

## 1. Fastest confidence — run the self-test (30 seconds, no clicking)

```bash
bench --site hrms.localhost execute frappe_hr_ui.selftest.run
```
Expect **`VERDICT: ALL PASS ✅`** (~55 checks: every screen aggregator, every write
action create→assert→cleanup, the generic engine, RBAC, and access management). This
verifies the entire data/permission layer in one shot. Everything below is the *visual /
interaction* layer that a script can't check.

---

## 2. Configuration console (HR, no Desk)

Log in as **fatima**. Sidebar workspace = **HR & Payroll**. Scroll to the
**Configuration** group.

For each master below: open it → the list loads → **New …** opens a form → fill required
fields (marked `*`) → **Create** → the row appears → click the row → edit a field → **Save**
→ click a row → **Delete** (a confirm dialog appears) → confirm.

- [ ] **Departments**, **Designations**, **Employee grades**, **Employment types** — simple masters, create/edit/delete cleanly.
- [ ] **Leave types** — create one (name + allocation); edit; the `Apply for leave` drawer should then offer it.
- [ ] **Salary components** — create an earning/deduction.
- [ ] **Expense types** — create one; it should appear in the employee `New reimbursement` category dropdown.
- [ ] **Shift types** — create one (start/end time).

### Child-table editing (the key one)
- [ ] **Holiday lists** → New → name + from/to dates → in the **holidays** sub-grid click **Add row**, set a date + description, add a couple → **Create**. Reopen it → the rows are there.
- [ ] **Leave policies** → New → add **leave policy details** rows (leave type + allocation). (Note: complex masters that need extra hrms fields will show a clear validation toast — that's hrms enforcing its rules, not a bug.)
- [ ] **Income tax slabs** → New → add slab rows.

### Settings singles
- [ ] **HR settings** → form loads with current values → change a non-critical field → **Save** → "Settings saved" → reopen, value persisted.
- [ ] **Payroll settings** → same.

**Expected throughout:** lists paginate (Previous/Next), search filters, the **New** button only shows if you have create permission, deletes always confirm.

---

## 3. Users & access (Administrator only)

Log in as **Administrator** → `/people` → HR & Payroll → **Configuration → Users & access**.
- [ ] The list shows existing login users with their roles + linked employee + Active status.
- [ ] **Add user** → first/last name + email + tick roles (HR Manager / HR User / Leave Approver / Expense Approver) → **Create user** → it appears.
- [ ] Click a user → toggle roles / disable → **Save access** → reopen, changes persisted.
- [ ] **Security check:** log in as **aarav** and try to open `/config/access` directly — it should show an error state ("Couldn't load…"), because user-admin requires System Manager. (Employees can't manage access.)

---

## 4. Setup wizard + onboarding (HR/Administrator)

Open `/people` → HR & Payroll → **Configuration → Setup wizard** (or go to `/setup`).
- [ ] **Step 1 Overview** — shows your company + counts (components / leave types / employees). **Get started**.
- [ ] **Step 2 Defaults** — checklist of what exists → **Apply India defaults** → toast "Defaults applied", checklist updates (it's idempotent — safe to click again, nothing duplicates). **Next**.
- [ ] **Step 3 Employees** — **Download CSV template** → open it (header row of columns) → add 1–2 rows (first_name, gender = Male/Female/Other, date_of_birth + date_of_joining as YYYY-MM-DD) → upload the file → a **preview table** appears → **Import** → "N of M imported"; any bad rows show a red per-row reason (e.g. invalid gender). **Finish**.
- [ ] **Step 4 Done** — links to Directory / Dashboard. Open the Directory and confirm the imported people are there.

---

## 5. Employee self-service requests (login as aarav)

Sidebar workspace = **Employee**.
- [ ] **Advances** → **New advance** → purpose + amount → **Submit** → it appears in *your* list (only your own).
- [ ] **Comp-off** → **Request comp-off** → pick a date that **is a holiday** + reason → submit. (A non-holiday date is rejected by hrms with a clear toast — expected.)
- [ ] **Leave encashment** → **Request encashment** → pick period + leave type. (Needs an eligible allocation; otherwise hrms explains why — expected.)

**Expected:** each screen lists only the logged-in employee's own requests; `employee` is set automatically (you never pick yourself).

---

## 6. HR cases & offboarding (login as fatima)

HR & Payroll → **Cases & offboarding**.
- [ ] **Promotions / Grievances / Exit interviews / Full & final** — each lists records; **New** opens a generic form (incl. child tables for Full & Final). Create a simple Grievance or Exit Interview to confirm the flow; complex docs that need more required fields will toast hrms's validation.

---

## 7. In-app reports (HR, no Desk)

- [ ] **Analytics → Report builder** → click any report (e.g. *Salary register*, *Headcount & demographics*) → an in-app drawer opens with a real data table + **Download CSV**.
- [ ] **Compliance → PF dashboard → Generate challan** and **Challan & returns → Generate challan** → report drawer with rows.
- [ ] Confirm **Salary register** shows ~24 rows and **Income Tax Computation** shows non-zero TDS (we fixed a bug there).

---

## 8. Cross-cutting UX

- [ ] **⌘K search** — press Cmd/Ctrl-K anywhere → type "leave", "salary", "directory" → ↑/↓ + Enter jumps to the screen (switching workspace if needed). The search box has **no green focus ring**. Esc closes.
- [ ] **Branding** — sidebar shows the **Frappe HR logo**; primary buttons + accents are **teal-green**; browser tab favicon is the logo.
- [ ] **Confirm dialogs** — Manager → Approvals → **Reject** prompts before acting; HR → Regularization → **Reject** / **Approve all** prompt.
- [ ] **States** — throttle your network (DevTools → Slow/Offline) and reload a screen: you get a centered **loading** then a proper **error with Retry**, not a flash of empty/fake data. Log in as Administrator (no Employee record) and open an employee screen → "No employee record linked".
- [ ] **PWA install (mobile/Chrome)** — open `/people` on a phone → browser menu → **Add to Home screen** → it installs as "Frappe HR" with the green logo, opens standalone. (Full offline isn't enabled yet — that's the pending service-worker work.)

---

## What a script can't tell you (focus your manual time here)
Pixel rendering, animations/transitions, drawer feel, responsive layout on small screens,
and the PWA install — these need your eyes. The data, wiring, permissions and reports are
already covered by `selftest.run`.
