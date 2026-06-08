import { createResource } from "frappe-ui"

// Employee record for the logged-in user (id, designation, department, etc.).
export const employeeResource = createResource({
  url: "hrms.api.get_current_employee_info",
  cache: "frappe_hr_ui:employee",
  auto: false,
})
