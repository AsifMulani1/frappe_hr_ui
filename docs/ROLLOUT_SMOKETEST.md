# Internal-rollout smoke test

A tight, sequenced click-through to run **before** putting Frappe HR UI in front of
your own employees. Target: ~15 min on desktop + ~5 min on a phone. Mark each
checkpoint ✅/❌. Anything ❌ is a rollout blocker — note the screen + what you saw.

> Prereqs: a site with a few real employees, at least one with a **Salary Slip**,
> one **Leave Application**, and one reporting manager. Run `bench --site <site>
> execute frappe_hr_ui.selftest.run` first — it must end in `VERDICT: ALL PASS`.

Open `/people` (hard-refresh: ⌘/Ctrl-Shift-R) so you get the latest build.

---

## Part 1 — Employee daily loops (sign in as an ordinary employee)

These are the screens 95% of your staff touch. They must be flawless.

### 1. Clock in / out  *(the most-used action in the app)*
- [ ] Home shows **Today's attendance** with a Check in button.
- [ ] Click **Check in** → button shows a spinner, then a green **"Checked in"** toast.
- [ ] The ring / worked-time updates; button now reads **Check out**.
- [ ] Click **Check out** → **"Checked out"** toast; state flips back.
- [ ] Refresh the page → the check-in state **persists** (it was really saved).

### 2. Apply for leave
- [ ] Left rail **Me → Time off & attendance → Leave**.
- [ ] Leave balances render (not "—"/blank).
- [ ] **Apply** → drawer opens; pick a leave type, from/to dates, reason.
- [ ] The day-count updates as you change dates.
- [ ] Submit → success toast; the new request appears in the list as **Open/Pending**.
- [ ] (Optional) Confirm in Desk that a **Leave Application** doc was created.

### 3. Payslips
- [ ] **Me → Pay & expenses → Payslips** lists real slips (or a clean empty state).
- [ ] Open one → earnings/deductions/net render; **Download PDF** works.

### 4. Self-service breadth (quick scan — each should load, not error)
- [ ] My profile · Attendance · Tax & FBP · Reimbursements · Helpdesk · Directory.
- [ ] None show a stack trace, infinite spinner, or "—" where a number belongs.

---

## Part 2 — Manager loop (sign in as a reporting manager)

- [ ] Workspace switcher (top-left) now offers **Team**.
- [ ] **Team → Approvals** lists the team's pending requests.
- [ ] **Approve** one → green **"Request approved"** toast; row clears.
- [ ] **Reject** one → confirm dialog → **"Request rejected"** toast; row clears.
- [ ] Team attendance / Team leave / Org chart each load.

---

## Part 3 — The new navigation (sign in as HR / admin)

### 5. Workspaces are calm, not overwhelming
- [ ] Switcher shows **Me · Team · People · Recruitment · Payroll** (per your roles).
- [ ] Each workspace's rail is **scannable** — grouped, no 40-item wall.
- [ ] **People → Dashboard**, **Payroll → Dashboard**, **Recruitment → Dashboard**
      each render with **real numbers** (headcount, net payout, open jobs).

### 6. Settings hub (the gear, bottom-left)
- [ ] Gear appears only in admin workspaces; opens **Settings**.
- [ ] Categories on the left (Organization / Time & leave / Payroll / Performance /
      System); cards on the right with descriptions.
- [ ] Click a card (e.g. **Leave types**) → opens that config list.
- [ ] ⌘K → search "leave type" → it's findable from search too.

### 7. Inline create  *(create a master without leaving)*
- [ ] Open any form with a link field — e.g. **Settings → Salary components → New**,
      or a config doctype with a child table.
- [ ] On a **Link** field, click the **＋** beside the picker.
- [ ] A **second drawer** opens *on top* to create that linked record.
- [ ] Fill + Create → the new record is **auto-selected** in the original field;
      you land back exactly where you were.
- [ ] Cancel on the nested drawer returns cleanly to the first drawer.

---

## Part 4 — Phone (≈5 min, real device or DevTools device mode)

Employees live in self-service on their phones. Open `/people` on a phone.
- [ ] Home + **Check in/out** is reachable and tappable (button not cut off).
- [ ] The sidebar collapses / is reachable; you can navigate to Leave & Payslips.
- [ ] Apply-leave drawer is usable (fields not overflowing the viewport).
- [ ] Tables scroll horizontally instead of breaking the layout.
- [ ] No element is clipped behind another; tap targets are finger-sized.

> Mobile is the area I could **not** verify from code — give this part real attention.

---

## Pass criteria
Rollout-ready when **Parts 1–2 are 100% ✅** (the daily loops) and Part 3 has no
❌ (the new IA). Part 4 ❌s are fixable polish, not necessarily blockers — judge by
how many of your staff are phone-first.

Log ❌s with: screen, what you did, what you expected, what happened.
