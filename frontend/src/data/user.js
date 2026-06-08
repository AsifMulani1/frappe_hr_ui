import router from "@/router"
import { createResource } from "frappe-ui"

// Current logged-in user info (name, full_name, roles, etc.).
// Reuses hrms's endpoint, which returns user + roles for the session.
export const userResource = createResource({
  url: "hrms.api.get_current_user_info",
  cache: "frappe_hr_ui:user",
  onError(error) {
    if (error && error.exc_type === "AuthenticationError") {
      router.push({ name: "Login" })
    }
  },
})
