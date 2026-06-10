// Shared action helpers used to wire up buttons across the SPA.
//
// The SPA replaces the *interface* for the common flows (drawers + whitelisted
// API writes), but the long tail of admin create/edit screens reuse Frappe's
// Desk forms — they're the real, permission-checked editors for the underlying
// DocTypes. These helpers open those forms in a new tab, export the data the
// page already has as CSV, or download a server-rendered PDF.

import { toast } from "frappe-ui"

/** Slugify a DocType name for a Desk URL ("Job Opening" -> "job-opening"). */
function slug(doctype) {
  return String(doctype).trim().toLowerCase().replace(/\s+/g, "-")
}

/** Open an arbitrary Desk path (e.g. "/app/employee/new") in a new tab. */
export function openDesk(path) {
  const url = path.startsWith("/") ? path : `/app/${path}`
  window.open(url, "_blank", "noopener")
}

/** Open an existing document in the Desk form view. */
export function openDoc(doctype, name) {
  if (!name) {
    toast.error("Nothing to open yet")
    return
  }
  openDesk(`/app/${slug(doctype)}/${encodeURIComponent(name)}`)
}

/** Open a blank Desk form to create a new document of `doctype`. */
export function newDoc(doctype, params) {
  let url = `/app/${slug(doctype)}/new`
  if (params && Object.keys(params).length) {
    const q = new URLSearchParams(params).toString()
    url += `?${q}`
  }
  openDesk(url)
}

/** Open a Frappe (query) report in Desk. */
export function openReport(reportName) {
  openDesk(`/app/query-report/${encodeURIComponent(reportName)}`)
}

/** Download a server-rendered PDF for a document via Frappe's print engine.
 *  Fetches the file so failures (e.g. wkhtmltopdf not installed) surface as a
 *  friendly toast instead of a raw traceback in a blank tab. */
export async function downloadPdf(doctype, name, format = "Standard") {
  if (!name) {
    toast.error("Select a record first")
    return
  }
  const q = new URLSearchParams({ doctype, name, format, no_letterhead: "0" })
  try {
    const res = await fetch(`/api/method/frappe.utils.print_format.download_pdf?${q.toString()}`)
    if (!res.ok) {
      let msg = "Couldn't generate the PDF."
      try {
        const j = await res.json()
        const sm = j?._server_messages && JSON.parse(j._server_messages)
        if (sm?.length) msg = JSON.parse(sm[0]).message
        else if (j?.exception) msg = j.exception
      } catch (_) { /* non-JSON error body */ }
      if (/wkhtmltopdf/i.test(msg)) {
        msg = "The server's PDF tool (wkhtmltopdf) isn't installed. Ask your admin to install it."
      }
      toast.error(msg)
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${name}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (_) {
    toast.error("Couldn't download the PDF. Please try again.")
  }
}

/** Compose an email to one or more recipients. */
export function mailto(email, subject) {
  if (!email) {
    toast.error("No email address on file")
    return
  }
  const q = subject ? `?subject=${encodeURIComponent(subject)}` : ""
  window.location.href = `mailto:${email}${q}`
}

function csvCell(v) {
  if (v == null) v = ""
  const s = String(v)
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

/**
 * Export rows the page already holds as a CSV download.
 * @param {string} filename  e.g. "attendance"
 * @param {Array<{key:string,label:string}>} columns
 * @param {Array<object>} rows
 */
export function downloadCSV(filename, columns, rows) {
  if (!rows || !rows.length) {
    toast.error("Nothing to export")
    return
  }
  const header = columns.map((c) => csvCell(c.label)).join(",")
  const body = rows
    .map((row) => columns.map((c) => csvCell(typeof c.value === "function" ? c.value(row) : row[c.key])).join(","))
    .join("\n")
  const blob = new Blob([`${header}\n${body}`], { type: "text/csv;charset=utf-8;" })
  const link = document.createElement("a")
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}
