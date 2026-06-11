# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

import unittest

from frappe_hr_ui.statutory_files import StatutoryFile, compute_ecr_amounts, to_csv


class FakeFile(StatutoryFile):
	"""Minimal subclass so the base class can be tested without the database."""

	title = "Fake"
	columns = ["A", "B"]

	def build(self):
		self.warn("missing something")
		return [[1, 2], [3, 4]]


class TestComputeEcrAmounts(unittest.TestCase):
	def test_member_below_pension_ceiling(self):
		amounts = compute_ecr_amounts(provident_fund=1200, working_days=30, payment_days=30)
		self.assertEqual(amounts["provident_fund_wages"], 10000)
		self.assertEqual(amounts["pension_wages"], 10000)
		self.assertEqual(amounts["employee_provident_fund"], 1200)
		self.assertEqual(amounts["employer_pension"], 833)
		self.assertEqual(amounts["employer_provident_fund"], 367)
		self.assertEqual(amounts["non_contributing_days"], 0)

	def test_pension_wages_capped_at_ceiling(self):
		amounts = compute_ecr_amounts(provident_fund=3000, working_days=30, payment_days=30)
		self.assertEqual(amounts["provident_fund_wages"], 25000)
		self.assertEqual(amounts["pension_wages"], 15000)

	def test_non_contributing_days_from_loss_of_pay(self):
		amounts = compute_ecr_amounts(provident_fund=1200, working_days=30, payment_days=24)
		self.assertEqual(amounts["non_contributing_days"], 6)


class TestStatutoryFileBase(unittest.TestCase):
	def test_rows_build_once_and_cache(self):
		statutory_file = FakeFile(None, None, None)
		self.assertEqual(statutory_file.rows, [[1, 2], [3, 4]])
		_ = statutory_file.rows  # second access must not re-run build()
		self.assertEqual(statutory_file.warnings, ["missing something"])

	def test_csv_content_includes_header(self):
		self.assertIn("A,B", FakeFile(None, None, None).content())


class TestToCsv(unittest.TestCase):
	def test_writes_header_and_rows(self):
		self.assertEqual(to_csv([["a", "b"], [1, 2]]).splitlines(), ["a,b", "1,2"])


if __name__ == "__main__":
	unittest.main()
