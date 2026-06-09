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

  // HR — People
  { path: "/hr-dashboard", name: "HrDashboard", component: () => import("@/pages/HrDashboard.vue") },
  { path: "/hr-directory", name: "HrDirectory", component: () => import("@/pages/HrDirectory.vue") },
  { path: "/employee-360", name: "HrEmployee360", component: () => import("@/pages/HrEmployee360.vue") },
  { path: "/onboarding", name: "HrOnboarding", component: () => import("@/pages/HrOnboarding.vue") },
  { path: "/transfers", name: "HrTransfers", component: () => import("@/pages/HrTransfers.vue") },
  { path: "/separation", name: "HrSeparation", component: () => import("@/pages/HrSeparation.vue") },
  { path: "/org-builder", name: "HrOrgBuilder", component: () => import("@/pages/HrOrgBuilder.vue") },
  // HR — Attendance
  { path: "/attendance-workspace", name: "HrAttendance", component: () => import("@/pages/HrAttendance.vue") },
  { path: "/roster", name: "HrRoster", component: () => import("@/pages/HrRoster.vue") },
  { path: "/biometric", name: "HrBiometric", component: () => import("@/pages/HrBiometric.vue") },
  { path: "/regularize", name: "HrRegularize", component: () => import("@/pages/HrRegularize.vue") },
  // HR — Payroll
  { path: "/payroll-run", name: "HrPayrun", component: () => import("@/pages/HrPayrun.vue") },
  { path: "/salary-structure", name: "HrSalStructure", component: () => import("@/pages/HrSalStructure.vue") },
  { path: "/revisions", name: "HrRevisions", component: () => import("@/pages/HrRevisions.vue") },
  { path: "/off-cycle", name: "HrOffcycle", component: () => import("@/pages/HrOffcycle.vue") },
  { path: "/reconcile", name: "HrReconcile", component: () => import("@/pages/HrReconcile.vue") },
  { path: "/bank-file", name: "HrBankfile", component: () => import("@/pages/HrBankfile.vue") },
  // HR — Compliance
  { path: "/compliance/pf", name: "CompliancePf", component: () => import("@/pages/ComplianceScreen.vue"), props: { kind: "pf" } },
  { path: "/compliance/esi", name: "ComplianceEsi", component: () => import("@/pages/ComplianceScreen.vue"), props: { kind: "esi" } },
  { path: "/compliance/pt", name: "CompliancePt", component: () => import("@/pages/ComplianceScreen.vue"), props: { kind: "pt" } },
  { path: "/compliance/tds", name: "ComplianceTds", component: () => import("@/pages/ComplianceScreen.vue"), props: { kind: "tds" } },
  { path: "/challan", name: "HrChallan", component: () => import("@/pages/HrChallan.vue") },
  { path: "/statutory-calendar", name: "HrStatcal", component: () => import("@/pages/HrStatcal.vue") },
  // HR — Recruitment
  { path: "/jobs", name: "HrJobs", component: () => import("@/pages/HrJobs.vue") },
  { path: "/pipeline", name: "HrPipeline", component: () => import("@/pages/HrPipeline.vue") },
  { path: "/interviews", name: "HrInterviews", component: () => import("@/pages/HrInterviews.vue") },
  { path: "/offers", name: "HrOffers", component: () => import("@/pages/HrOffers.vue") },
  // HR — Performance / Analytics / Settings
  { path: "/appraisal-cycle", name: "HrCycle", component: () => import("@/pages/HrCycle.vue") },
  { path: "/calibration", name: "HrCalibration", component: () => import("@/pages/HrCalibration.vue") },
  { path: "/survey", name: "HrSurvey", component: () => import("@/pages/HrSurvey.vue") },
  { path: "/analytics", name: "HrAnalytics", component: () => import("@/pages/HrAnalytics.vue") },
  { path: "/reports", name: "HrReports", component: () => import("@/pages/HrReports.vue") },
  { path: "/settings", name: "HrSettings", component: () => import("@/pages/HrSettings.vue") },

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
