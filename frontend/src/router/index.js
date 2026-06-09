import { createRouter, createWebHistory } from "vue-router"
import { sessionUser } from "@/data/session"

const routes = [
  {
    path: "/",
    name: "EmployeeHome",
    component: () => import("@/pages/EmployeeHome.vue"),
  },
  { path: "/profile", name: "EmployeeProfile", component: () => import("@/pages/EmployeeProfile.vue") },
  { path: "/attendance", name: "EssAttendance", component: () => import("@/pages/EssAttendance.vue") },
  { path: "/leave", name: "EssLeave", component: () => import("@/pages/EssLeave.vue") },
  { path: "/payslips", name: "EssPayslip", component: () => import("@/pages/EssPayslip.vue") },
  { path: "/tax", name: "EssTax", component: () => import("@/pages/EssTax.vue") },
  {
    path: "/reimbursements", name: "EssReimburse",
    component: () => import("@/pages/ClaimsView.vue"),
    props: { title: "Reimbursements", subtitle: "Claim work expenses paid out of pocket", addLabel: "New reimbursement" },
  },
  {
    path: "/expenses", name: "EssExpense",
    component: () => import("@/pages/ClaimsView.vue"),
    props: { title: "Expenses & advances", subtitle: "Submit travel expenses and request salary advances", addLabel: "New expense claim" },
  },
  { path: "/performance", name: "EssPerformance", component: () => import("@/pages/EssPerformance.vue") },
  { path: "/helpdesk", name: "EssHelpdesk", component: () => import("@/pages/EssHelpdesk.vue") },
  { path: "/directory", name: "EssDirectory", component: () => import("@/pages/EssDirectory.vue") },
  { path: "/announcements", name: "EssAnnouncements", component: () => import("@/pages/EssAnnouncements.vue") },

  // Manager
  { path: "/team", name: "MgrDashboard", component: () => import("@/pages/MgrDashboard.vue") },
  { path: "/approvals", name: "MgrApprovals", component: () => import("@/pages/MgrApprovals.vue") },
  { path: "/team-attendance", name: "MgrAttendance", component: () => import("@/pages/MgrAttendance.vue") },
  { path: "/team-leave", name: "MgrLeave", component: () => import("@/pages/MgrLeave.vue") },
  { path: "/team-performance", name: "MgrPerformance", component: () => import("@/pages/MgrPerformance.vue") },
  { path: "/org-chart", name: "MgrOrgChart", component: () => import("@/pages/MgrOrgChart.vue") },

  { path: "/screen/:id", name: "ComingSoon", component: () => import("@/pages/ComingSoon.vue") },
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
