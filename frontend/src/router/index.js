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
  {
    path: "/advances", name: "EssAdvance", component: () => import("@/pages/EssRequest.vue"),
    props: {
      doctype: "Employee Advance", title: "Advances", subtitle: "Request a salary or travel advance", addLabel: "New advance",
      fields: [
        { key: "purpose", label: "Purpose", type: "textarea", cols: 2, placeholder: "What is this advance for?" },
        { key: "advance_amount", label: "Amount (₹)", type: "number", cols: 1, placeholder: "0" },
      ],
      required: ["purpose", "advance_amount"],
      listColumns: [{ key: "name", label: "Reference" }, { key: "purpose", label: "Purpose" }, { key: "advance_amount", label: "Amount" }, { key: "posting_date", label: "Date" }],
    },
  },
  {
    path: "/comp-off", name: "EssCompOff", component: () => import("@/pages/EssRequest.vue"),
    props: {
      doctype: "Compensatory Leave Request", title: "Comp-off", subtitle: "Claim time off for working on a holiday", addLabel: "Request comp-off",
      fields: [
        { key: "work_from_date", label: "Worked from", type: "date", cols: 1 },
        { key: "work_end_date", label: "Worked to", type: "date", cols: 1 },
        { key: "reason", label: "Reason", type: "textarea", cols: 2 },
      ],
      required: ["work_from_date", "work_end_date", "reason"],
      listColumns: [{ key: "name", label: "Reference" }, { key: "work_from_date", label: "Worked on" }, { key: "reason", label: "Reason" }],
    },
  },
  {
    path: "/encashment", name: "EssEncashment", component: () => import("@/pages/EssRequest.vue"),
    props: {
      doctype: "Leave Encashment", title: "Leave encashment", subtitle: "Encash your eligible leave balance", addLabel: "Request encashment",
      fields: [
        { key: "leave_period", label: "Leave period", type: "select", linkDoctype: "Leave Period", cols: 2 },
        { key: "leave_type", label: "Leave type", type: "select", linkDoctype: "Leave Type", cols: 2 },
      ],
      required: ["leave_period", "leave_type"],
      listColumns: [{ key: "name", label: "Reference" }, { key: "leave_type", label: "Leave type" }],
    },
  },

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
  { path: "/compliance/lwf", name: "ComplianceLwf", component: () => import("@/pages/ComplianceScreen.vue"), props: { kind: "lwf" } },
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
  { path: "/payroll", name: "PayrollDashboard", component: () => import("@/pages/PayrollDashboard.vue") },
  { path: "/recruitment", name: "RecruitmentDashboard", component: () => import("@/pages/RecruitmentDashboard.vue") },
  { path: "/settings", name: "Settings", component: () => import("@/pages/SettingsHub.vue") },
  { path: "/settings/statutory", name: "StatutoryProfile", component: () => import("@/pages/StatutoryProfile.vue") },
  { path: "/settings/general", name: "HrSettings", component: () => import("@/pages/HrSettings.vue") },

  // Configuration (generic metadata-driven doctype admin — no Desk)
  {
    path: "/config/leave-types", name: "CfgLeaveType",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Leave Type", title: "Leave Types", subtitle: "Configure leave types and accrual rules" },
  },
  {
    path: "/config/salary-components", name: "CfgSalaryComponent",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Salary Component", title: "Salary Components", subtitle: "Earnings and deductions used in salary structures" },
  },
  {
    path: "/config/leave-policies", name: "CfgLeavePolicy",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Leave Policy", title: "Leave Policies", subtitle: "Bundle leave types into assignable policies" },
  },
  {
    path: "/config/shift-types", name: "CfgShiftType",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Shift Type", title: "Shift Types", subtitle: "Working-hour patterns and grace rules" },
  },
  {
    path: "/config/holiday-lists", name: "CfgHolidayList",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Holiday List", title: "Holiday Lists", subtitle: "Company and location holiday calendars" },
  },
  {
    path: "/config/expense-types", name: "CfgExpenseType",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Expense Claim Type", title: "Expense Types", subtitle: "Categories employees can claim against" },
  },
  {
    path: "/config/income-tax-slabs", name: "CfgTaxSlab",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Income Tax Slab", title: "Income Tax Slabs", subtitle: "Tax regimes and slab rates" },
  },
  {
    path: "/config/departments", name: "CfgDepartment",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Department", title: "Departments", subtitle: "Org structure" },
  },
  {
    path: "/config/designations", name: "CfgDesignation",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Designation", title: "Designations", subtitle: "Job titles" },
  },
  {
    path: "/config/grades", name: "CfgGrade",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Employee Grade", title: "Employee Grades", subtitle: "Grades and default structures" },
  },
  {
    path: "/config/employment-types", name: "CfgEmploymentType",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Employment Type", title: "Employment Types", subtitle: "Full-time, contract, intern, etc." },
  },
  {
    path: "/config/appraisal-templates", name: "CfgAppraisalTemplate",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Appraisal Template", title: "Appraisal Templates", subtitle: "KRA templates with weightings" },
  },
  {
    path: "/config/kras", name: "CfgKRA",
    component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "KRA", title: "KRAs", subtitle: "Key result areas for appraisals" },
  },
  // Single-doctype settings
  {
    path: "/config/hr-settings", name: "CfgHRSettings",
    component: () => import("@/pages/ConfigSingle.vue"),
    props: { doctype: "HR Settings", title: "HR Settings", subtitle: "Leave, attendance and employee defaults" },
  },
  {
    path: "/config/payroll-settings", name: "CfgPayrollSettings",
    component: () => import("@/pages/ConfigSingle.vue"),
    props: { doctype: "Payroll Settings", title: "Payroll Settings", subtitle: "Payroll, salary slip and tax defaults" },
  },
  { path: "/config/access", name: "HrAccess", component: () => import("@/pages/HrAccess.vue") },
  { path: "/setup", name: "SetupWizard", component: () => import("@/pages/SetupWizard.vue") },

  // HR transactional screens via the generic engine
  {
    path: "/cases/grievances", name: "CfgGrievance", component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Employee Grievance", title: "Grievances", subtitle: "Employee grievances and resolutions" },
  },
  {
    path: "/cases/exit-interviews", name: "CfgExitInterview", component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Exit Interview", title: "Exit Interviews", subtitle: "Feedback captured during offboarding" },
  },
  {
    path: "/cases/full-and-final", name: "CfgFnF", component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Full and Final Statement", title: "Full & Final", subtitle: "Final settlement on exit" },
  },
  {
    path: "/cases/promotions", name: "CfgPromotion", component: () => import("@/pages/ConfigDoctype.vue"),
    props: { doctype: "Employee Promotion", title: "Promotions", subtitle: "Employee promotions" },
  },

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
