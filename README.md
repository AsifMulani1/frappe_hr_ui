# Frappe HR UI

A modern, desktop-first HRMS front-end for **Frappe HR (`hrms`)** — a consumer-grade
replacement for the Desk admin UI, tuned for the Indian market (₹, lakhs/crores,
PF/ESI/PT/TDS). Built with **Vue 3 + Vite + Tailwind + frappe-ui** and served by Frappe
at **`/people`**. It reuses the `hrms`/`erpnext` DocTypes and APIs — it replaces the
interface, not the data model.

Roles map to three workspaces (Employee · Manager · HR & Payroll) chosen by the
logged-in user's Frappe roles. 50 screens, all wired to live data through server-side
aggregators in `frappe_hr_ui/api.py`.

## Requirements

- Frappe **v16** + `erpnext` v16 + `hrms` v16 (hrms requires erpnext)
- **Python 3.14**, **Node ≥ 24**, Yarn 1.x

## Install (existing bench)

```bash
bench get-app https://github.com/frappe/erpnext --branch version-16   # if absent
bench get-app https://github.com/frappe/hrms --branch version-16      # if absent
bench get-app /path/to/frappe_hr_ui                                   # this app

bench --site <site> install-app erpnext hrms frappe_hr_ui
```

## Build the front-end (required — produces the served assets)

The SPA is built with Vite into `frappe_hr_ui/public/frontend/` and its HTML entry is
copied to `frappe_hr_ui/www/people.html`. **Build artifacts are git-ignored**, so every
deploy (and every fresh checkout) must run:

```bash
cd apps/frappe_hr_ui/frontend
yarn install
yarn build
bench --site <site> clear-cache
```

Then open **`/people`** (login required; guests are redirected to `/login`).

### Dev

```bash
bench start                      # bench services
cd apps/frappe_hr_ui/frontend
yarn dev                         # Vite on :8080, proxies /api to the bench
# open http://<site>:8080/people
```

## Sample data (optional, for demos / a fresh site)

`seed.py` creates the demo company, 24 employees, leave/attendance/payroll, recruitment,
and three persona logins. Idempotent.

```bash
# A fresh ERPNext site needs the setup wizard run once to create default masters:
bench --site <site> execute frappe_hr_ui.setup_company.run
bench --site <site> execute frappe_hr_ui.seed.run
```

Persona logins (password `Frappe@123`):

| User | Workspace |
|---|---|
| `aarav.mehta@frappe.io` | Employee |
| `devika.rao@frappe.io` | Manager |
| `fatima.sheikh@frappe.io` | HR & Payroll |

## Security

Read/write APIs enforce roles server-side: HR aggregators require **HR Manager / HR User /
System Manager**; manager aggregators require an approver role or actual direct reports;
employee APIs only ever return the session user's own records. The sidebar additionally
hides workspaces the user can't access. All writes go through whitelisted POST methods
with CSRF.

## Architecture

```
frontend/src/
  components/ui/      shared kit (DataTable, Drawer, Card, StatTiles, …)
  components/layout/  AppShell, Sidebar, Topbar
  components/home/    employee-home widgets
  pages/              one .vue per screen
  data/               session, user, employee, nav
  composables/ stores/ utils/
frappe_hr_ui/
  api.py              per-screen aggregators + write endpoints (role-gated)
  www/people.*        SPA host page (boot + CSRF)
  seed.py             demo data (dev only)
```

## License

mit
