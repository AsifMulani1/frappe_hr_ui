# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

import unittest

from frappe.utils import getdate

from frappe_hr_ui.api.base import _tenure


class TestTenure(unittest.TestCase):
	def test_missing_date_of_joining_returns_dash(self):
		self.assertEqual(_tenure(None), "—")

	def test_joining_today_is_zero_months(self):
		self.assertEqual(_tenure(getdate()), "0 months")

	def test_future_joining_date_is_clamped_to_zero(self):
		self.assertEqual(_tenure("2999-01-01"), "0 months")

	def test_output_is_human_readable(self):
		self.assertIn("month", _tenure("2000-01-01"))


if __name__ == "__main__":
	unittest.main()
