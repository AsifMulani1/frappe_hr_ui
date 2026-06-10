"""In-UI access management — create users and grant HR/Manager/Employee roles
without ever opening Desk. Gated by Frappe's own User permissions (System Manager),
and the assignable roles are deliberately limited to the HR set (never System Manager).
"""

import frappe

# Roles an admin may grant from this UI. System Manager is intentionally excluded
# (too privileged to grant here). "Employee" is intentionally NOT listed: erpnext/hrms
# auto-manage it via the Employee↔User link, so it only sticks when an Employee record
# is linked to the user — granting it directly here would silently no-op.
ASSIGNABLE_ROLES = ["HR Manager", "HR User", "Leave Approver", "Expense Approver"]


def _require_user_admin(*args, **kwargs):
	# "User create" is the right signal for a user-administrator (System Manager).
	# Note: User read/write pass for everyone via if-owner (own profile), so they
	# can't be used to gate an admin screen.
	if not frappe.has_permission("User", "create"):
		frappe.throw(frappe._("You are not permitted to manage user access."), frappe.PermissionError)


def _managed_roles(email):
	"""Read assigned roles straight from the DB (avoids the per-request role cache)."""
	roles = frappe.get_all("Has Role", filters={"parent": email, "parenttype": "User"}, pluck="role")
	return sorted(set(roles) & set(ASSIGNABLE_ROLES))


@frappe.whitelist()
def get_assignable_roles():
	return {"roles": ASSIGNABLE_ROLES}


@frappe.whitelist()
def list_users(search=None):
	# managing access requires User-write capability (System Manager), not mere read
	_require_user_admin("write")
	filters = {"user_type": "System User", "name": ["not in", ["Administrator", "Guest"]]}
	if search:
		filters["full_name"] = ["like", f"%{search}%"]
	users = frappe.get_all("User", filters=filters, fields=["name", "full_name", "enabled"],
		order_by="full_name", limit=200)
	emp_map = {e.user_id: e.employee_name for e in frappe.get_all("Employee",
		filters={"user_id": ["is", "set"]}, fields=["user_id", "employee_name"])}
	out = []
	for u in users:
		out.append({"email": u.name, "full_name": u.full_name, "enabled": bool(u.enabled),
					"roles": _managed_roles(u.name), "employee": emp_map.get(u.name)})
	return {"users": out, "assignable": ASSIGNABLE_ROLES}


@frappe.whitelist()
def get_user_access(email):
	_require_user_admin("write", doc=email)
	u = frappe.db.get_value("User", email, ["full_name", "enabled"], as_dict=True) or {}
	return {"email": email, "full_name": u.get("full_name"), "enabled": bool(u.get("enabled")), "roles": _managed_roles(email)}


@frappe.whitelist(methods=["POST"])
def create_user(email, first_name, last_name=None, roles=None, send_welcome_email=0):
	_require_user_admin("create")
	roles = frappe.parse_json(roles) if roles else []
	roles = [r for r in roles if r in ASSIGNABLE_ROLES]
	if frappe.db.exists("User", email):
		frappe.throw(frappe._("A user with this email already exists."))
	doc = frappe.get_doc({
		"doctype": "User", "email": email, "first_name": first_name, "last_name": last_name,
		"user_type": "System User", "send_welcome_email": 1 if frappe.utils.cint(send_welcome_email) else 0,
	})
	doc.insert()  # respects User create perm
	doc.add_roles(*roles)
	frappe.db.commit()
	return {"name": doc.name, "roles": roles}


@frappe.whitelist(methods=["POST"])
def set_user_access(email, roles=None, enabled=None):
	"""Reconcile only the managed roles (never touches System Manager etc.) + enable flag."""
	_require_user_admin("write", doc=email)
	if email in ("Administrator", "Guest"):
		frappe.throw(frappe._("This user can't be managed here."))
	want = set(r for r in (frappe.parse_json(roles) if roles else []) if r in ASSIGNABLE_ROLES)
	have = set(_managed_roles(email))
	doc = frappe.get_doc("User", email)
	to_add, to_remove = want - have, have - want
	if to_add:
		doc.add_roles(*to_add)
	if to_remove:
		doc.remove_roles(*to_remove)
	if enabled is not None:
		doc.db_set("enabled", 1 if frappe.utils.cint(enabled) else 0)
	frappe.db.commit()
	return {"name": email, "roles": sorted(want)}
