# Copyright (c) 2026, Asif Mulani and contributors
# For license information, please see license.txt

import unittest

from frappe_hr_ui.seed.data import (
	DEPARTMENTS,
	DESIGNATIONS,
	EMPLOYMENT_TYPES,
	GRADES,
	LOCATIONS,
	PEOPLE,
	_grade_for_ctc,
)

# Field positions in each PEOPLE tuple
IDENTIFIER, NAME, DESIGNATION, DEPARTMENT, LOCATION, STATUS, MANAGER, EMPLOYMENT_TYPE, CTC, DATE_OF_JOINING = range(10)


class TestSeedDataIntegrity(unittest.TestCase):
	"""Guards the hand-maintained demo data against typos and dangling references."""

	def test_every_person_has_ten_fields(self):
		for person in PEOPLE:
			self.assertEqual(len(person), 10, person)

	def test_employee_identifiers_are_unique(self):
		identifiers = [person[IDENTIFIER] for person in PEOPLE]
		self.assertEqual(len(identifiers), len(set(identifiers)))

	def test_references_point_to_known_masters(self):
		for person in PEOPLE:
			self.assertIn(person[DEPARTMENT], DEPARTMENTS, person[NAME])
			self.assertIn(person[DESIGNATION], DESIGNATIONS, person[NAME])
			self.assertIn(person[LOCATION], LOCATIONS, person[NAME])
			self.assertIn(person[EMPLOYMENT_TYPE], EMPLOYMENT_TYPES, person[NAME])

	def test_managers_reference_existing_employees(self):
		identifiers = {person[IDENTIFIER] for person in PEOPLE}
		for person in PEOPLE:
			if person[MANAGER]:
				self.assertIn(person[MANAGER], identifiers, person[NAME])

	def test_ctc_is_positive(self):
		for person in PEOPLE:
			self.assertGreater(person[CTC], 0, person[NAME])


class TestGradeForCtc(unittest.TestCase):
	def test_each_band_returns_expected_grade(self):
		self.assertEqual(_grade_for_ctc(500000), "L1")
		self.assertEqual(_grade_for_ctc(1000000), "L2")
		self.assertEqual(_grade_for_ctc(1500000), "L3")
		self.assertEqual(_grade_for_ctc(2200000), "L4")
		self.assertEqual(_grade_for_ctc(3500000), "L5")

	def test_just_below_a_boundary_stays_in_lower_band(self):
		self.assertEqual(_grade_for_ctc(999999), "L1")
		self.assertEqual(_grade_for_ctc(3499999), "L4")

	def test_every_person_maps_to_a_valid_grade(self):
		for person in PEOPLE:
			self.assertIn(_grade_for_ctc(person[CTC]), GRADES, person[NAME])


if __name__ == "__main__":
	unittest.main()
