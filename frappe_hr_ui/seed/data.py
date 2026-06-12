"""Shared sample-data constants and helpers for the demo seeder."""

import frappe


COMPANY = "Frappe Technologies Pvt. Ltd."

ABBR = "FT"

CURRENCY = "INR"

COUNTRY = "India"

DEPARTMENTS = [
    "Engineering", "Design", "Sales", "Marketing",
    "People", "Finance", "Customer Success", "Leadership",
]

LOCATIONS = ["Mumbai", "Bengaluru", "Pune", "Delhi", "Hyderabad", "Remote"]

DESIGNATIONS = [
    "VP Engineering", "Engineering Manager", "Senior Engineer", "Product Engineer",
    "Frontend Engineer", "Backend Engineer", "DevOps Engineer", "QA Engineer",
    "Data Analyst", "Design Lead", "Product Designer", "UX Researcher",
    "Sales Director", "Account Executive", "Sales Executive",
    "Marketing Manager", "Content Strategist", "HR Business Partner", "Recruiter",
    "Finance Controller", "Finance Analyst", "Support Engineer",
    "Customer Success Lead", "Intern - Engineering",
]

EMPLOYMENT_TYPES = ["Full-time", "Intern"]

LEAVE_TYPES = [
    ("Casual Leave", 12),
    ("Sick Leave", 8),
    ("Earned Leave", 18),
    ("Comp Off", 3),
]

HOLIDAYS = [
    ("2026-08-15", "Independence Day"),
    ("2026-08-26", "Ganesh Chaturthi"),
    ("2026-10-02", "Gandhi Jayanti"),
    ("2026-10-20", "Diwali (Lakshmi Pujan)"),
    ("2026-10-21", "Diwali (Balipratipada)"),
    ("2026-12-25", "Christmas"),
]

PEOPLE = [
    ("HR-1320", "Nikhil Shah",     "VP Engineering",       "Leadership",       "Mumbai",    "Active", None,      "Full-time", 6000000, "2015-06-01"),
    ("HR-1001", "Devika Rao",      "Engineering Manager",  "Engineering",      "Mumbai",    "Active", "HR-1320", "Full-time", 3600000, "2019-01-05"),
    ("HR-1119", "Meera Nair",      "Design Lead",          "Design",           "Mumbai",    "Active", "HR-1320", "Full-time", 3000000, "2018-11-11"),
    ("HR-1178", "Priya Menon",     "Sales Director",       "Sales",            "Delhi",     "Active", "HR-1320", "Full-time", 4200000, "2017-02-08"),
    ("HR-1289", "Rahul Khanna",    "Finance Controller",   "Finance",          "Mumbai",    "Active", "HR-1320", "Full-time", 3900000, "2016-04-12"),
    ("HR-1203", "Fatima Sheikh",   "HR Business Partner",  "People",           "Mumbai",    "Active", "HR-1320", "Full-time", 1860000, "2021-01-14"),
    ("HR-1345", "Amit Trivedi",    "Customer Success Lead","Customer Success", "Bengaluru", "Active", "HR-1320", "Full-time", 2520000, "2020-09-07"),
    ("HR-1042", "Aarav Mehta",     "Product Engineer",     "Engineering",      "Mumbai",    "Active", "HR-1001", "Full-time", 1704000, "2022-04-12"),
    ("HR-1067", "Karthik Iyer",    "Senior Engineer",      "Engineering",      "Bengaluru", "Active", "HR-1001", "Full-time", 2400000, "2020-08-22"),
    ("HR-1102", "Rohan Gupta",     "QA Engineer",          "Engineering",      "Pune",      "Active", "HR-1001", "Full-time", 1380000, "2022-07-15"),
    ("HR-1156", "Ananya Desai",    "Frontend Engineer",    "Engineering",      "Bengaluru", "Active", "HR-1001", "Full-time", 1560000, "2023-09-19"),
    ("HR-1190", "Arjun Reddy",     "DevOps Engineer",      "Engineering",      "Hyderabad", "Active", "HR-1001", "Full-time", 2160000, "2021-10-27"),
    ("HR-1221", "Aditya Joshi",    "Backend Engineer",     "Engineering",      "Pune",      "Active", "HR-1001", "Full-time", 1920000, "2022-05-05"),
    ("HR-1334", "Sneha Reddy",     "Data Analyst",         "Engineering",      "Hyderabad", "Active", "HR-1001", "Full-time", 1440000, "2024-02-14"),
    ("HR-1088", "Sana Kapoor",     "Product Designer",     "Design",           "Mumbai",    "Active", "HR-1119", "Full-time", 1980000, "2021-03-03"),
    ("HR-1356", "Kavya Pillai",    "UX Researcher",        "Design",           "Mumbai",    "Active", "HR-1119", "Full-time", 1740000, "2022-04-19"),
    ("HR-1134", "Vikram Singh",    "Account Executive",    "Sales",            "Delhi",     "Active", "HR-1178", "Full-time", 1620000, "2022-06-02"),
    ("HR-1301", "Manish Agarwal",  "Sales Executive",      "Sales",            "Delhi",     "Active", "HR-1178", "Full-time",  960000, "2026-03-02"),
    ("HR-1245", "Neha Verma",      "Marketing Manager",    "Marketing",        "Mumbai",    "Active", "HR-1178", "Full-time", 2280000, "2020-07-30"),
    ("HR-1312", "Divya Krishnan",  "Content Strategist",   "Marketing",        "Bengaluru", "Active", "HR-1245", "Full-time", 1320000, "2022-11-25"),
    ("HR-1277", "Ishita Banerjee", "Finance Analyst",      "Finance",          "Mumbai",    "Active", "HR-1289", "Full-time", 1500000, "2021-08-09"),
    ("HR-1294", "Pooja Patil",     "Recruiter",            "People",           "Pune",      "Active", "HR-1203", "Full-time", 1080000, "2023-06-18"),
    ("HR-1260", "Sandeep Kumar",   "Support Engineer",     "Customer Success", "Bengaluru", "Active", "HR-1001", "Full-time", 1140000, "2023-03-21"),
    ("HR-1361", "Rishi Malhotra",  "Intern - Engineering", "Engineering",      "Remote",    "Active", "HR-1221", "Intern",     480000, "2026-01-06"),
]

GRADES = ["L1", "L2", "L3", "L4", "L5"]

PERSONA_USERS = [
    ("HR-1042", "aarav.mehta@frappe.io", "Frappe@123", ["Employee"]),
    ("HR-1001", "devika.rao@frappe.io", "Frappe@123", ["Employee", "Leave Approver", "Expense Approver"]),
    ("HR-1203", "fatima.sheikh@frappe.io", "Frappe@123", ["Employee", "HR Manager", "HR User"]),
]

ANNOUNCEMENTS = [
    ("Updated work-from-home policy effective 1 July",
     "We're moving to a 3-days-in-office model for all Mumbai and Bengaluru teams starting 1 July 2026. Tuesdays and Thursdays are anchor days; the third day is flexible. Remote-first roles are unaffected."),
    ("May payslips released - investment proofs open",
     "Your May 2026 payslip is now available under Payslips. The window to submit investment proofs for FY 2025-26 is open until 31 December. Submitting early helps spread your TDS evenly."),
    ("Quarterly town hall - Saturday 6 June, 4:00 PM",
     "Join us for the Q1 review and product roadmap. In-person at the Mumbai office auditorium, or on the livestream for remote teammates. We'll close with an open AMA."),
    ("New mental wellness benefit - 6 free therapy sessions",
     "We've partnered with a wellness provider to offer every employee 6 confidential counselling sessions per year, fully covered. Book directly through the benefits portal."),
]


def _exists(doctype, name):
    return frappe.db.exists(doctype, name)


def _grade_for_ctc(ctc):
    if ctc >= 3500000:
        return "L5"
    if ctc >= 2200000:
        return "L4"
    if ctc >= 1500000:
        return "L3"
    if ctc >= 1000000:
        return "L2"
    return "L1"
