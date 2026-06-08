import { createResource } from "frappe-ui"

// One aggregated resource backing the employee home dashboard.
export function useEmployeeHome() {
  return createResource({
    url: "frappe_hr_ui.api.get_employee_home",
    auto: true,
    cache: "frappe_hr_ui:employee_home",
  })
}

export function fmtMins(mins) {
  const m = Math.max(0, Math.round(mins || 0))
  return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, "0")}m`
}

// Leave-type accent -> tailwind classes (kept on-token, no raw hex).
export const LEAVE_THEME = {
  blue: { bar: "bg-blue-500", dot: "bg-blue-500" },
  green: { bar: "bg-green-500", dot: "bg-green-500" },
  violet: { bar: "bg-purple-500", dot: "bg-purple-500" },
  orange: { bar: "bg-orange-500", dot: "bg-orange-500" },
}
