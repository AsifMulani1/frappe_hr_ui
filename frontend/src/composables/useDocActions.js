// Shared helpers for the in-app (UI-first) create/edit drawers.
//
// Every admin "create" action in the SPA opens a Drawer with FormControls and
// posts to the role-gated `create_doc` endpoint — no Desk redirects. Link-field
// dropdowns are populated from `get_link_options`.

import { ref, reactive, computed } from "vue"
import { createResource, toast } from "frappe-ui"

/**
 * Options for a Link field's target doctype, as [{label, value}].
 * Returns a `computed` ref; fetches once on first use.
 */
export function useLinkOptions(doctype, filters) {
  const res = createResource({
    url: "frappe_hr_ui.api.get_link_options",
    params: { doctype, filters: filters ? JSON.stringify(filters) : undefined },
    auto: true,
  })
  return computed(() => res.data?.options || [])
}

/**
 * A create-drawer controller bound to one doctype.
 * Usage:
 *   const add = useCreate("Job Opening", { onDone: () => r.reload() })
 *   add.openDrawer()              // open
 *   add.submit(form, ["job_title"])  // validate required keys then POST
 */
export function useCreate(doctype, { onDone, successLabel } = {}) {
  const open = ref(false)
  const create = createResource({
    url: "frappe_hr_ui.api.create_doc",
    onSuccess(r) {
      toast.success(successLabel || `${doctype} created`)
      open.value = false
      if (onDone) onDone(r)
    },
    onError(e) {
      toast.error(e?.messages?.[0] || `Couldn't create ${doctype.toLowerCase()}`)
    },
  })
  function openDrawer() {
    open.value = true
  }
  function submit(values, requiredKeys = []) {
    const missing = requiredKeys.filter((k) => !values[k])
    if (missing.length) {
      toast.error("Please fill in the required fields")
      return
    }
    create.submit({ doctype, values: JSON.stringify(values) })
  }
  // IMPORTANT: return a reactive() object, not a plain one. Pages bind
  // `:open="add.open"` — a ref nested in a *plain* object is NOT unwrapped in
  // templates (it reads as a truthy ref object, so the drawer is stuck open and
  // `add.open = false` never re-renders). reactive() unwraps the ref and keeps
  // get/set reactive, so every create drawer opens and closes correctly.
  return reactive({ open, create, openDrawer, submit })
}
