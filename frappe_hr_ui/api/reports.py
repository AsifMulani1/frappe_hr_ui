# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

"""In-app report builders — salary register, employees, leave balance,
attendance, bank file and TDS — surfaced through ``get_report_data``."""

import frappe
from frappe.utils import flt, formatdate

from .core import COMPANY_NAME, _require_hr

def _money(v):
	return frappe.utils.fmt_money(v or 0, currency="INR")


def _report_salary_register():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
		fields=["employee_name", "department", "end_date", "gross_pay", "total_deduction", "net_pay"],
		order_by="net_pay desc", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Department", "key": "dept"},
			{"label": "Period", "key": "period"}, {"label": "Gross", "key": "gross"},
			{"label": "Deductions", "key": "ded"}, {"label": "Net pay", "key": "net"}]
	rows = [{"emp": s.employee_name, "dept": (s.department or "").split(" - ")[0],
			 "period": formatdate(s.end_date, "MMM yyyy") if s.end_date else "—",
			 "gross": _money(s.gross_pay), "ded": _money(s.total_deduction), "net": _money(s.net_pay)}
			for s in slips]
	return cols, rows


def _report_employees():
	emps = frappe.get_all("Employee", filters={"status": ["in", ["Active", "On Leave"]]},
		fields=["employee_name", "employee_number", "department", "designation", "date_of_joining", "status"],
		order_by="employee_name", limit=500)
	cols = [{"label": "Name", "key": "n"}, {"label": "ID", "key": "id"}, {"label": "Department", "key": "dept"},
			{"label": "Designation", "key": "desig"}, {"label": "Joined", "key": "doj"}, {"label": "Status", "key": "st"}]
	rows = [{"n": e.employee_name, "id": e.employee_number, "dept": (e.department or "").split(" - ")[0],
			 "desig": e.designation, "doj": formatdate(e.date_of_joining, "dd MMM yyyy") if e.date_of_joining else "—",
			 "st": e.status} for e in emps]
	return cols, rows


def _report_leave_balance():
	allocs = frappe.get_all("Leave Allocation", filters={"docstatus": 1},
		fields=["employee_name", "leave_type", "total_leaves_allocated", "from_date", "to_date"],
		order_by="employee_name", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Leave type", "key": "lt"},
			{"label": "Allocated", "key": "alloc"}, {"label": "Period", "key": "period"}]
	rows = [{"emp": a.employee_name, "lt": a.leave_type, "alloc": a.total_leaves_allocated,
			 "period": f"{formatdate(a.from_date, 'dd MMM')} – {formatdate(a.to_date, 'dd MMM yyyy')}" if a.from_date else "—"}
			for a in allocs]
	return cols, rows


def _report_attendance():
	att = frappe.get_all("Attendance", filters={"docstatus": 1},
		fields=["employee_name", "attendance_date", "status", "working_hours"],
		order_by="attendance_date desc", limit=500)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Date", "key": "date"},
			{"label": "Status", "key": "st"}, {"label": "Hours", "key": "hrs"}]
	rows = [{"emp": a.employee_name, "date": formatdate(a.attendance_date, "dd MMM yyyy"),
			 "st": a.status, "hrs": round(a.working_hours or 0, 1)} for a in att]
	return cols, rows


def _report_bankfile():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
		fields=["employee", "employee_name", "net_pay"], order_by="net_pay desc", limit=500)
	# batch bank details for all employees (avoid N+1)
	emp_ids = list({s.employee for s in slips})
	bank_map = {e.name: e for e in frappe.get_all("Employee", filters={"name": ["in", emp_ids]},
		fields=["name", "bank_name", "bank_ac_no"])} if emp_ids else {}
	cols = [{"label": "Employee", "key": "emp"}, {"label": "Bank", "key": "bank"},
			{"label": "Account", "key": "ac"}, {"label": "Net pay", "key": "net"}]
	rows = []
	for s in slips:
		info = bank_map.get(s.employee) or {}
		ac = info.get("bank_ac_no") or ""
		rows.append({"emp": s.employee_name, "bank": info.get("bank_name") or "—",
					 "ac": ("XXXX " + ac[-4:]) if ac else "—", "net": _money(s.net_pay)})
	return cols, rows


def _report_tds():
	slips = frappe.get_all("Salary Slip", filters={"docstatus": 1}, fields=["name", "employee", "employee_name"], limit=2000)
	# batch TDS across all slips in one query (also fixes a bug: parent was never selected)
	tds_rows = frappe.get_all("Salary Detail",
		filters={"parent": ["in", [s.name for s in slips]], "parentfield": "deductions", "salary_component": "TDS"},
		fields=["parent", "amount"]) if slips else []
	tds_by_slip = {}
	for d in tds_rows:
		tds_by_slip[d.parent] = tds_by_slip.get(d.parent, 0) + (d.amount or 0)
	agg = {}
	for s in slips:
		row = agg.setdefault(s.employee, {"emp": s.employee_name, "tds": 0})
		row["tds"] += tds_by_slip.get(s.name, 0)
	cols = [{"label": "Employee", "key": "emp"}, {"label": "TDS deducted (FY)", "key": "tds"}]
	rows = [{"emp": v["emp"], "tds": _money(v["tds"])} for v in sorted(agg.values(), key=lambda x: -x["tds"])]
	return cols, rows


_REPORT_PROVIDERS = {
	"Salary Register": _report_salary_register,
	"Employee Information": _report_employees,
	"Employee Leave Balance": _report_leave_balance,
	"Monthly Attendance Sheet": _report_attendance,
	"Bank Remittance": _report_bankfile,
	"Income Tax Computation": _report_tds,
}


@frappe.whitelist()
def get_report_data(report_name, filters=None):
	"""Return columns + rows for an in-app report. Uses real-data providers for the
	known reports; falls back to running a standard Frappe query report otherwise."""
	_require_hr()
	provider = _REPORT_PROVIDERS.get(report_name)
	if provider:
		try:
			cols, rows = provider()
			return {"columns": cols, "rows": rows, "report": report_name}
		except Exception as e:
			return {"error": str(e), "columns": [], "rows": []}

	from frappe.desk.query_report import run
	flt = frappe.parse_json(filters) if filters else {"company": COMPANY_NAME()}
	try:
		res = run(report_name, filters=flt, ignore_prepared_report=True) or {}
	except Exception as e:
		return {"error": str(e), "columns": [], "rows": []}
	cols = []
	for c in (res.get("columns") or []):
		if isinstance(c, dict):
			cols.append({"label": c.get("label") or c.get("fieldname"), "key": c.get("fieldname") or c.get("label")})
		else:
			cols.append({"label": str(c), "key": str(c)})
	rows = []
	for r in (res.get("result") or []):
		if isinstance(r, dict):
			rows.append(r)
		elif isinstance(r, (list, tuple)):
			rows.append({cols[i]["key"]: v for i, v in enumerate(r) if i < len(cols)})
	return {"columns": cols, "rows": rows[:500], "report": report_name}

