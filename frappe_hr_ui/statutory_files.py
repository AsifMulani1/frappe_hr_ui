"""Statutory & disbursement file generation — the India compliance moat.

Turns a submitted payroll run into the artifacts a company actually files / uses,
not just on-screen registers. Each artifact is a small ``StatutoryFile`` subclass
with one responsibility:

  • BankAdvice              — salary disbursement file (bank-uploadable CSV)
  • ProvidentFundEcr        — EPFO ECR text file (member-wise, #~# delimited)
  • EmployeeStateInsuranceReturn — ESIC monthly contribution file
  • ProfessionalTaxStatement     — state-wise PT summary (challan basis)

The base class owns the shared plumbing (period, slip access, CSV rendering,
warning collection); a subclass implements only ``build`` and overrides
``content`` when the file is not CSV. The wage/contribution maths live in pure
module functions so they can be unit-tested without the database.

Formats follow the published EPFO/ESIC layouts but must be validated against the
employer's own portal/bank template before live filing — wage-base policy varies.
"""

import csv
import io

import frappe
from frappe.utils import flt, get_last_day, getdate

EMPLOYEE_PROVIDENT_FUND_RATE = 0.12
EMPLOYER_PENSION_RATE = 0.0833
PENSION_WAGE_CEILING = 15000
EMPLOYEE_STATE_INSURANCE_WAGE_CEILING = 21000

PROVIDENT_FUND_COMPONENT = "Provident Fund"
EMPLOYEE_STATE_INSURANCE_COMPONENT = "Employee State Insurance"
PROFESSIONAL_TAX_COMPONENT = "Professional Tax"


# ───────────────────────── shared utilities ─────────────────────────

def require_hr_permission():
	from frappe_hr_ui.api import _require_hr

	return _require_hr()


def default_company(company=None):
	from frappe_hr_ui.api import COMPANY_NAME

	return company or COMPANY_NAME()


def period_slips(start_date, end_date, company):
	"""Submitted salary slips for the period, employee-sorted."""
	filters = {"docstatus": 1, "start_date": [">=", start_date], "end_date": ["<=", end_date]}
	if company:
		filters["company"] = company
	return frappe.get_all(
		"Salary Slip", filters=filters,
		fields=["name", "employee", "employee_name", "gross_pay", "net_pay", "total_deduction",
				"payment_days", "total_working_days", "bank_name", "bank_account_no"],
		order_by="employee_name")


def deducted_amount(slip_name, component):
	"""Amount of a single deduction component on a slip (zero if absent)."""
	amounts = frappe.get_all(
		"Salary Detail",
		filters={"parent": slip_name, "parentfield": "deductions", "salary_component": component},
		pluck="amount")
	return flt(sum(amounts))


def employee_details(employee):
	return frappe.db.get_value(
		"Employee", employee,
		["provident_fund_account", "pan_number", "bank_name", "bank_ac_no", "ifsc_code",
		 "account_type", "esic_card_no"], as_dict=True) or frappe._dict()


def employment_state(employee, on_date):
	"""Employment state from the latest effective salary-structure assignment."""
	return frappe.db.get_value(
		"Salary Structure Assignment",
		{"employee": employee, "docstatus": 1, "from_date": ["<=", on_date]},
		"employment_state", order_by="from_date desc") or ""


def to_csv(table):
	buffer = io.StringIO()
	csv.writer(buffer).writerows(table)
	return buffer.getvalue()


def compute_ecr_amounts(provident_fund, working_days, payment_days):
	"""Pure EPFO ECR wage/contribution maths for one member (no database)."""
	provident_fund_wages = round(provident_fund / EMPLOYEE_PROVIDENT_FUND_RATE)
	pension_wages = min(provident_fund_wages, PENSION_WAGE_CEILING)
	employee_provident_fund = round(provident_fund)
	employer_pension = round(pension_wages * EMPLOYER_PENSION_RATE)
	return {
		"provident_fund_wages": provident_fund_wages,
		"pension_wages": pension_wages,
		"employee_provident_fund": employee_provident_fund,
		"employer_pension": employer_pension,
		"employer_provident_fund": employee_provident_fund - employer_pension,
		"non_contributing_days": max(0, round(working_days - payment_days)),
	}


# ───────────────────────── generators ─────────────────────────

class StatutoryFile:
	"""Base for a period's statutory/disbursement artifact.

	A subclass sets ``title``/``extension``/``columns`` and implements ``build``,
	reporting any missing identifier via ``self.warn``. Rows build once and cache;
	``content`` defaults to CSV and is overridden where the format differs."""

	title = ""
	extension = "csv"
	mime = "text/csv"
	columns: list = []
	note = ""

	def __init__(self, start_date, end_date, company):
		self.start_date = start_date
		self.end_date = end_date
		self.company = company
		self.warnings: list = []
		self.cached_rows = None

	def slips(self):
		return period_slips(self.start_date, self.end_date, self.company)

	def warn(self, message):
		self.warnings.append(message)

	def build(self) -> list:
		raise NotImplementedError

	def totals(self) -> dict:
		return {}

	@property
	def rows(self) -> list:
		if self.cached_rows is None:
			self.cached_rows = self.build()
		return self.cached_rows

	def content(self) -> str:
		return to_csv([self.columns] + self.rows)

	def as_dict(self) -> dict:
		result = {
			"columns": self.columns, "rows": self.rows, "content": self.content(),
			"mime": self.mime, "totals": self.totals(), "warnings": self.warnings,
		}
		if self.note:
			result["note"] = self.note
		return result


class BankAdvice(StatutoryFile):
	"""Salary disbursement file — one row per employee with net pay + bank details."""

	title = "Salary disbursement (bank advice)"
	columns = ["Employee", "Employee Name", "Bank", "Account Number", "IFSC", "Account Type", "Amount (INR)"]

	def build(self):
		return [self.row(slip) for slip in self.slips()]

	def row(self, slip):
		details = employee_details(slip.employee)
		account = details.bank_ac_no or slip.bank_account_no
		if not account or not details.ifsc_code:
			self.warn(f"{slip.employee_name}: missing bank account / IFSC")
		return [slip.employee, slip.employee_name, details.bank_name or slip.bank_name or "",
				account or "", details.ifsc_code or "", details.account_type or "Savings",
				round(flt(slip.net_pay), 2)]

	def totals(self):
		return {"count": len(self.rows), "amount": round(sum(row[-1] for row in self.rows), 2)}


class ProvidentFundEcr(StatutoryFile):
	"""EPFO ECR text file — member-wise, '#~#' delimited per the ECR v2 layout."""

	title = "PF ECR file"
	extension = "txt"
	mime = "text/plain"
	columns = ["UAN", "Name", "Gross", "EPF Wages", "EPS Wages", "EE EPF", "ER EPS", "ER EPF", "NCP", "Refund"]

	def build(self):
		self.members = [self.member(slip) for slip in self.slips()
						if deducted_amount(slip.name, PROVIDENT_FUND_COMPONENT)]
		return [self.preview_row(member) for member in self.members]

	def member(self, slip):
		details = employee_details(slip.employee)
		universal_account_number = (details.provident_fund_account or "").strip()
		if not universal_account_number:
			self.warn(f"{slip.employee_name}: missing UAN (Provident Fund A/C)")
		amounts = compute_ecr_amounts(deducted_amount(slip.name, PROVIDENT_FUND_COMPONENT),
									  flt(slip.total_working_days), flt(slip.payment_days))
		return {"universal_account_number": universal_account_number,
				"name": (slip.employee_name or "").upper(), "gross": round(flt(slip.gross_pay)), **amounts}

	def preview_row(self, member):
		return [member["universal_account_number"] or "—", member["name"], member["gross"],
				member["provident_fund_wages"], member["pension_wages"], member["employee_provident_fund"],
				member["employer_pension"], member["employer_provident_fund"], member["non_contributing_days"], 0]

	def content(self):
		self.rows  # ensure build() ran and populated members
		return "\n".join(self.ecr_line(member) for member in self.members)

	def ecr_line(self, member):
		return "#~#".join(str(value) for value in [
			member["universal_account_number"] or "UAN_MISSING", member["name"], member["gross"],
			member["provident_fund_wages"], member["pension_wages"], member["pension_wages"],
			member["employee_provident_fund"], member["employer_pension"],
			member["employer_provident_fund"], member["non_contributing_days"], 0])

	def totals(self):
		return {"members": len(self.members),
				"employee_provident_fund": round(sum(m["employee_provident_fund"] for m in self.members)),
				"employer_pension": round(sum(m["employer_pension"] for m in self.members))}


class EmployeeStateInsuranceReturn(StatutoryFile):
	"""ESIC monthly contribution file — one row per insured person who had ESI deducted."""

	title = "ESIC contribution file"
	columns = ["IP Number", "IP Name", "Number of Days", "Total Monthly Wages", "Employee Contribution"]
	note = f"Only employees with gross ≤ ₹{EMPLOYEE_STATE_INSURANCE_WAGE_CEILING:,} are ESI-covered."

	def build(self):
		rows = []
		for slip in self.slips():
			contribution = deducted_amount(slip.name, EMPLOYEE_STATE_INSURANCE_COMPONENT)
			if contribution:
				rows.append(self.row(slip, contribution))
		return rows

	def row(self, slip, contribution):
		insured_person_number = (employee_details(slip.employee).esic_card_no or "").strip()
		if not insured_person_number:
			self.warn(f"{slip.employee_name}: missing ESI IP number")
		return [insured_person_number or "IP_MISSING", slip.employee_name,
				round(flt(slip.payment_days)), round(flt(slip.gross_pay)), round(contribution)]

	def totals(self):
		return {"members": len(self.rows), "employee_contribution": round(sum(row[-1] for row in self.rows))}


class ProfessionalTaxStatement(StatutoryFile):
	"""State-wise Professional Tax summary — the basis for each state's PT challan."""

	title = "Professional Tax statement"
	columns = ["State", "Employees", "Total PT (INR)"]

	def build(self):
		totals_by_state: dict = {}
		for slip in self.slips():
			professional_tax = deducted_amount(slip.name, PROFESSIONAL_TAX_COMPONENT)
			if professional_tax:
				self.add(totals_by_state, slip, professional_tax)
		return [[state, count, round(amount)] for state, (count, amount) in sorted(totals_by_state.items())]

	def add(self, totals_by_state, slip, professional_tax):
		state = employment_state(slip.employee, self.start_date) or "Unspecified"
		count, amount = totals_by_state.get(state, (0, 0.0))
		totals_by_state[state] = (count + 1, amount + professional_tax)

	def totals(self):
		return {"states": len(self.rows), "professional_tax": round(sum(row[2] for row in self.rows))}


GENERATORS = {
	"bank": BankAdvice,
	"pf": ProvidentFundEcr,
	"esi": EmployeeStateInsuranceReturn,
	"pt": ProfessionalTaxStatement,
}


# ───────────────────────── whitelisted API ─────────────────────────

@frappe.whitelist()
def generate(kind, start_date, company=None):
	"""Build a statutory/disbursement file for the period (kind ∈ bank|pf|esi|pt)."""
	require_hr_permission()
	if kind not in GENERATORS:
		frappe.throw(frappe._("Unknown file type: {0}").format(kind))
	company = default_company(company)
	start = getdate(start_date)
	generator = GENERATORS[kind](start, get_last_day(start), company)
	result = generator.as_dict()
	result.update({
		"kind": kind, "title": generator.title, "period": start.strftime("%B %Y"), "company": company,
		"filename": f"{kind}-{company.replace(' ', '_')[:18]}-{start.strftime('%Y-%m')}.{generator.extension}",
	})
	return result


@frappe.whitelist()
def available(start_date, company=None):
	"""Which files can be produced for a period, and how many slips it has."""
	require_hr_permission()
	company = default_company(company)
	start = getdate(start_date)
	slips = period_slips(start, get_last_day(start), company)
	return {"period": start.strftime("%B %Y"), "slips": len(slips), "company": company,
			"files": [{"kind": kind, "title": generator.title} for kind, generator in GENERATORS.items()]}
