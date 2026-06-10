# Frappe HR UI

A modern, **consumer-grade front-end for [Frappe HR](https://github.com/frappe/hrms)** —
an open-source replacement for the Desk interface, tuned for the Indian market
(₹, lakhs/crores, PF/ESI/PT/TDS). Built with **Vue 3 + Vite + Tailwind + frappe-ui**
and served by Frappe at **`/people`**.

It replaces the *interface*, not the engine: `hrms` stays the system of record (payroll,
statutory compliance, leave, attendance), and this app reuses its DocTypes, controllers
and permissions. **Users never need to open Frappe Desk** — configuration, onboarding and
day-to-day work all happen in this UI.

Three role-based workspaces (Employee · Manager · HR & Payroll), chosen by the logged-in
user's Frappe roles.

## Why it's different

- **No Desk, ever.** A generic, metadata-driven doctype engine (`doctype_api.py` +
  `DocList`/`DocForm`) renders a permission-aware list/form for *any* HR/Payroll doctype —
  so masters, settings (incl. child tables like Salary Structure), and the long tail are
  all editable in-UI. Adding a config screen is one route + one nav entry.
- **Self-serviceable onboarding.** A `/setup` wizard applies India payroll defaults
  (salary components, leave types, a standard salary structure, holiday list), imports
  employees from CSV, and gets you live in an afternoon.
- **Binds to hrms, not around it.** Calculations (leave balance, holidays, leave-days)
  come from hrms; permissions defer to `frappe.has_permission` — upgrade-safe.
- **In-UI access management.** Create users and grant HR/approver roles without Desk.
- **Verified.** A one-command golden self-test (`frappe_hr_ui.selftest.run`) exercises
  every read, write, the engine and RBAC after each change.

## The stack

`frappe_hr_ui` is the **UI** for a three-app stack:

| App | Role |
|-----|------|
| [`hrms`](https://github.com/frappe/hrms) | core HR + payroll engine (system of record) |
| [`india_payroll`](https://github.com/frappe/india-payroll) | India statutory engine — PT, ESI, LWF, income-tax surcharge, statutory registers |
| **`frappe_hr_ui`** (this app) | the no-Desk front-end at `/people` |

`india_payroll` is **strongly recommended** for the India market (the compliance
dashboards light up with real computed PT/ESI/LWF/TDS). The UI degrades gracefully if
it's absent.

## Requirements

- Frappe **v16** + `erpnext` v16 + `hrms` v16 (hrms requires erpnext)
- `india_payroll` (recommended, for India statutory compliance)
- Built assets ship **in the repo**, so no Node/Yarn is needed to *deploy* — only to
  develop the front-end (Node ≥ 24, Yarn 1.x).

## Install on Frappe Cloud (recommended for DIY)

In your Frappe Cloud **Bench → Apps → Add App**, add each from GitHub, then install on a
fresh site (Site → Apps):

1. `frappe/erpnext` (version-16) · `frappe/hrms` (version-16)
2. `frappe/india-payroll` (develop)
3. `AsifMulani1/frappe_hr_ui` (main) ← this repo

The front-end assets are committed, so the site serves **`/people`** immediately after
install — no build step on the cloud. Then follow **First-run setup** below.

## Install (self-hosted bench)

```bash
bench get-app https://github.com/frappe/erpnext --branch version-16     # if absent
bench get-app https://github.com/frappe/hrms --branch version-16        # if absent
bench get-app https://github.com/frappe/india-payroll --branch develop
bench get-app https://github.com/AsifMulani1/frappe_hr_ui --branch main
bench --site <site> install-app erpnext hrms india_payroll frappe_hr_ui
bench --site <site> clear-cache
```

Open **`/people`** (login required). Built assets are committed, so no `yarn build` is
needed on install.

### Front-end development

Only needed if you change the UI. Rebuild + commit the assets after edits:

```bash
cd apps/frappe_hr_ui/frontend
yarn install
yarn build          # outputs to ../frappe_hr_ui/public/frontend + www/people.html
# or: yarn dev      # Vite :8080, proxies /api to the bench → http://<site>:8080/people
bench --site <site> clear-cache
```

### Dev

```bash
bench start
cd apps/frappe_hr_ui/frontend && yarn dev   # Vite :8080, proxies /api to the bench
# open http://<site>:8080/people
```

## DIY: zero → payroll, entirely in-UI (no Desk)

A 30-person SMB can self-implement end to end:

1. **Setup wizard** (`/setup`, or Settings → System → Setup wizard) → **Apply India
   defaults** — seeds salary components, leave types, a standard salary structure, a
   holiday list, and **turns on the statutory engine** (PT/ESI/LWF). Idempotent.
2. **Directory → Import (CSV)** — download the template, fill in employees, upload.
   Departments & designations are **auto-created**, so a real sheet doesn't error.
3. **Payroll → Salary structure → Assign to employees** — a grid of everyone without
   compensation; set base + **employment state** (drives PT/LWF) and assign in one go.
4. **Payroll → Run payroll** — pick a month, confirm, and it **generates + submits a
   salary slip for every eligible employee**, with PT/ESI/LWF/PF/TDS computed automatically.
5. **Payroll → Compliance** (PF · ESI · PT · LWF · TDS) and **Reports → Statutory
   registers** (ESIC / LWF / Bank Mandate) reflect the run.

Or seed India defaults from the CLI:

```bash
bench --site <site> execute frappe_hr_ui.india_defaults.apply
```

## Self-host with Docker

Build a custom image (frappe + erpnext + hrms + this app) with the official
[`frappe_docker`](https://github.com/frappe/frappe_docker) flow, using
[`docker/apps.json`](./docker/apps.json) (edit the `frappe_hr_ui` URL to your fork):

```bash
export APPS_JSON_BASE64=$(base64 -w 0 docker/apps.json)
git clone https://github.com/frappe/frappe_docker && cd frappe_docker
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --tag=frappe-hr-ui:latest --file=images/custom/Containerfile .
```

Then run with `frappe_docker`'s `compose.yaml` (point `CUSTOM_IMAGE`/`image` at
`frappe-hr-ui:latest`), create a site, `bench --site <site> install-app erpnext hrms
frappe_hr_ui`, and open `/people`. The front-end assets are built into the app, so no
separate `yarn build` is needed in the image.

## Sample data (demos / a fresh site)

`seed.py` creates a demo company, 24 employees, leave/attendance/payroll, recruitment and
three persona logins. Idempotent.

```bash
bench --site <site> execute frappe_hr_ui.setup_company.run   # fresh ERPNext site only
bench --site <site> execute frappe_hr_ui.seed.run
```

Persona logins (password `Frappe@123`): `aarav.mehta@frappe.io` (Employee),
`devika.rao@frappe.io` (Manager), `fatima.sheikh@frappe.io` (HR & Payroll).

## Self-test (run after any change)

```bash
bench --site <site> execute frappe_hr_ui.selftest.run
```

Exercises every screen aggregator, every action (create → assert → cleanup), the generic
engine, RBAC and access management as all three personas. Prints a PASS/FAIL report.

## Security & permissions

- **Permissions defer to Frappe.** The generic engine and write paths gate on
  `frappe.has_permission(...)` (no `ignore_permissions`), so access follows whatever roles
  an admin configures in hrms — one source of truth, upgrade-safe.
- Employee APIs only ever return the session user's own records; ESS create flows force
  `employee = self` server-side.
- Access management is gated on **User-create** capability (System Manager), not read/write
  (Frappe grants every user read/write on their *own* User record).
- All writes are whitelisted POST methods with CSRF.

## Architecture

```
frontend/src/
  components/ui/      kit + engine: DataTable, Drawer, FormDrawer, DocList, DocForm,
                     DetailDrawer, ReportDrawer, AsyncShell, BrandLogo …
  components/layout/  AppShell, Sidebar, Topbar, CommandPalette (⌘K)
  pages/              one .vue per screen + generic ConfigDoctype/ConfigSingle/EssRequest
  composables/        useDocActions (create/link helpers), useEmployeeHome
  data/ stores/ utils/
frappe_hr_ui/
  api.py              per-screen aggregators + ESS/HR write endpoints (hrms-bound)
  doctype_api.py      generic permission-aware doctype engine (meta/list/get/save/…)
  access_api.py       in-UI user + role management
  india_defaults.py   idempotent India payroll defaults pack
  employee_import.py   CSV bulk employee import
  selftest.py         golden regression test
  www/people.*        SPA host page (boot + CSRF)
  seed.py             demo data (dev only)
```

Brand accent is the Frappe HR logo green `#06B58B` (remapped in `tailwind.config.js`).
Execution plan and progress: see [`ROADMAP.md`](./ROADMAP.md).

## License

mit
