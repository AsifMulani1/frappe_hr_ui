import { createRouter, createWebHistory } from "vue-router"
import { sessionUser } from "@/data/session"

const routes = [
  {
    path: "/",
    name: "EmployeeHome",
    component: () => import("@/pages/EmployeeHome.vue"),
  },
  {
    path: "/profile",
    name: "EmployeeProfile",
    component: () => import("@/pages/EmployeeProfile.vue"),
  },
  // Remaining screens are registered here as they are built, one per the
  // build plan (ess-attendance, ess-leave, … hr-settings).
]

const router = createRouter({
  // Served under /people — Frappe rewrites /people/<path> to this SPA.
  // (/hr and /hrms are already taken by the hrms app's roster + PWA.)
  history: createWebHistory("/people"),
  routes,
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!sessionUser()
  if (!isLoggedIn) {
    // Bounce to Frappe's login, return to the SPA afterwards.
    window.location.href = "/login?redirect-to=/people"
    return
  }
  next()
})

export default router
