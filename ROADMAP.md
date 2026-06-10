# Frappe HR UI — Execution Roadmap

**Vision.** A modern, consumer-grade, **open-source front-end for Frappe HR (`hrms`)**. The
hrms engine stays the system of record (payroll, statutory PF/ESI/PT/TDS, leave, attendance);
this app replaces the *interface only*. **Users never see Frappe Desk** — every flow, including
configuration and setup, happens in this UI. Self-serviceable: install next to hrms, go live in
a day, own your data.

**Non-goals.** We do not re-implement payroll/compliance logic, the ERP, or Frappe platform
internals (workflow builder, print designer, custom-field editor) — those stay in hrms/Desk for
system admins, who are not "the user".

**Guiding principles.**
1. **Bind to hrms, don't re-roll** — reuse hrms's whitelisted APIs + doctype controllers so
   business rules and upgrades live in hrms.
2. **Defer to Frappe permissions** — gate on `frappe.has_permission`, not a parallel role list.
3. **Metadata-driven by default, curated where it matters** — a generic doctype engine covers
   the long tail; bespoke screens for high-frequency/complex flows.
4. **Upgrade-safe** — pinned to hrms v16; prefer its APIs/meta over custom queries.
5. **Verified every step** — golden self-test (`selftest`) run on every change.

---

## Phase 0 — Foundation & engine fidelity  *(keystone)*
Goal: the architecture that makes "no-Desk, full coverage, upgrade-safe" possible.

- **0.1 Generic meta-driven doctype engine**
  - Backend: permission-aware CRUD over HR/Payroll doctypes — `meta`, `list`, `get`, `save`,
    `submit`, `cancel`, `delete` — all enforced by `frappe.has_permission` (no `ignore_permissions`).
  - Frontend: one reusable **list view** + **form view** that render any doctype from its meta
    (fields, links, child tables, sections, submit states).
- **0.2 Re-point transactional reads/writes to hrms native getters** (leave, expense, attendance,
  holidays, directory, notifications) — delete our parallel queries.
- **0.3 Permissions → `frappe.has_permission`**; sidebar/screens reflect real perms.
- **0.4 Golden self-test** — `frappe_hr_ui.selftest.run`: all reads + writes + RBAC, fixtures
  create→assert→cleanup. Wire into CI.

**Done when:** any HR/Payroll doctype is viewable/editable in-UI (permission-checked); the
self-test is one command and green; no `/app` redirects anywhere.

## Phase 1 — No-Desk completeness (configuration & coverage)
Goal: an admin can run the whole product without touching Desk.

- **1.1 Settings console** on the generic engine: HR Settings, Payroll Settings, and masters
  (leave types/policies/periods, salary components, shift types, holiday lists,
  departments/designations/grades, expense types, tax slabs/exemption categories).
- **1.2 Curated builders** where generic forms aren't enough: **Salary Structure**, **Leave
  Policy & assignment**, **Payroll run** wizard.
- **1.3 Access management** — create users + assign Employee/Manager/HR roles from the UI.
- **1.4 Long-tail masters** auto-exposed via the generic engine (no bespoke work).

**Done when:** a fresh company can be fully configured in-UI; zero Desk needed for HR ops.

## Phase 2 — Onboarding & self-serviceability
Goal: zero-to-first-payslip in an afternoon, no Desk, no manual.

- **2.1 Setup wizard:** company → statutory IDs → salary structures → leave policies →
  holiday list → **employee Excel/CSV import (validated)** → first payroll dry-run.
- **2.2 India defaults pack:** standard salary components, PT slabs per state, Indian leave
  types, holiday templates — versioned & updatable.
- **2.3 Health checks** in-UI ("PF missing for 3 employees", "PT not set for Karnataka").
- **2.4 One-command install** (Docker Compose) + Frappe Cloud one-click + docs/demo mode.

**Done when:** a new user installs, runs the wizard, imports staff, and previews payroll
without help or Desk.

## Phase 3 — Transactional depth (close hrms feature gaps)
Curated screens (on the established drawer pattern) for hrms doctypes we don't yet expose.

- **High:** Travel Request, Employee Advance, Leave Encashment, Compensatory Leave, FBP
  (Benefit Application/Claim), Tax Proof Submission, Shift Request/Swap, Full & Final.
- **Medium:** Goals/KRA cascade, Performance Feedback, Employee Grievance, Exit Interview,
  Promotion, Training, Referral, Job Requisition.

**Done when:** every common hrms employee/HR action has a delightful screen.

## Phase 4 — Mobile & engagement
- PWA hardening + installable; **geo/selfie check-in**; **WhatsApp + push** notifications
  (align to hrms PWA Notification); offline-tolerant approvals.

## Phase 5 — Production hardening & open-source GTM
- DPDP/privacy (PII handling, consent, residency), audit trails, RBAC review.
- Performance/scale (large headcount lists, payroll runs), accessibility (WCAG AA).
- Golden payroll regression vs fixture companies; load tests.
- OSS packaging: pin to hrms v16, semantic releases, docs site, public demo, contribution guide,
  India statutory-pack subscription (commercial/open-core seam).

---

## Cross-cutting (every phase)
- **Testing/CI:** `selftest` green on each PR; build must pass.
- **Design system:** frappe-ui + espresso, brand green `#06B58B`, shared AsyncShell/FormDrawer/
  DetailDrawer; no bespoke one-offs.
- **i18n & currency**, **observability**, **docs**.

## Sequencing
P0 → P1 → P2 are the critical path to "complete, no-Desk, self-serviceable". P3 deepens, P4/P5
prepare for scale and release. Build strictly in order; each item ships behind a green self-test.
