import { computed, reactive } from "vue"
import { createResource, call } from "frappe-ui"
import { userResource } from "./user"
import { employeeResource } from "./employee"
import router from "@/router"

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
  let user = cookies.get("user_id")
  if (user === "Guest") user = null
  return user
}

function handleLogin(response) {
  if (response.message === "Logged In") {
    userResource.reload()
    employeeResource.reload()
    session.user = sessionUser()
    router.replace({ path: "/" })
  }
}

export const session = reactive({
  login: async (email, password) => {
    const response = await call("login", { usr: email, pwd: password })
    handleLogin(response)
    return response
  },
  logout: createResource({
    url: "logout",
    onSuccess() {
      userResource.reset()
      employeeResource.reset()
      session.user = sessionUser()
      window.location.href = "/login"
    },
  }),
  user: sessionUser(),
  isLoggedIn: computed(() => !!session.user),
})
