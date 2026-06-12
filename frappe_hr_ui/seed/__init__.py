"""Demo data seeder. Run: bench --site <site> execute frappe_hr_ui.seed.run"""

import frappe

from .data import COMPANY, DEPARTMENTS, DESIGNATIONS, EMPLOYMENT_TYPES, LOCATIONS
from .org import ensure_company, ensure_simple, ensure_holiday_list, ensure_holiday_assignment, ensure_leave_types, ensure_grades
from .people import ensure_employees, ensure_profile_details, ensure_users
from .payroll import ensure_salary_structure, ensure_expense_claims, ensure_salary_slips
from .leave import ensure_leave_allocations, ensure_leave_applications, ensure_attendance
from .talent import ensure_recruitment, ensure_announcements, ensure_issues, ensure_appraisal, ensure_lifecycle


def run():
    print("Seeding Frappe HR sample data ...")
    ensure_company()
    ensure_simple("Department", DEPARTMENTS)
    ensure_simple("Designation", DESIGNATIONS)
    ensure_simple("Branch", [l for l in LOCATIONS if l != "Remote"])
    ensure_simple("Employment Type", EMPLOYMENT_TYPES)
    hl = ensure_holiday_list()
    # Make it the company default so leave + salary-slip working-day lookups resolve.
    if frappe.db.exists("Company", COMPANY):
        frappe.db.set_value("Company", COMPANY, "default_holiday_list", hl)
        frappe.db.commit()
    ensure_holiday_assignment(hl)
    ensure_leave_types()
    id_to_name = ensure_employees()
    ensure_grades(id_to_name)
    ensure_profile_details(id_to_name)
    ensure_salary_structure(id_to_name)
    ensure_leave_allocations(id_to_name)
    ensure_leave_applications(id_to_name)
    ensure_attendance(id_to_name)
    ensure_salary_slips(id_to_name)
    ensure_expense_claims(id_to_name)
    ensure_recruitment()
    ensure_announcements()
    ensure_issues(id_to_name)
    ensure_appraisal(id_to_name)
    ensure_lifecycle(id_to_name)
    ensure_users(id_to_name)
    frappe.db.commit()
    print("Done. Sign in as aarav.mehta@frappe.io / Frappe@123 and open /people")
