import frappe
from frappe.boot import load_translations

no_cache = 1


def get_context(context):
	# Guests are bounced to login, returning to the SPA afterwards.
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/people"
		raise frappe.Redirect

	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosemgrep
	context = frappe._dict()
	context.csrf_token = csrf_token
	context.boot = get_boot()
	context.site_name = frappe.local.site
	return context


def get_boot():
	bootinfo = frappe._dict(
		{
			"site_name": frappe.local.site,
			"default_route": "/people",
		}
	)
	bootinfo.lang = frappe.local.lang
	load_translations(bootinfo)
	return bootinfo
