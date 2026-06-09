// Role-aware navigation, ported from the prototype shell.jsx NAV.
// `icon` values are keys into components/ui/Icon.vue's lucide registry.
// `route` is the Vue Router name (screens register their route as built;
// until then the item is shown but lands on a "coming soon" stub).

export const NAV = {
  employee: {
    label: "Employee",
    sub: "Self-service",
    items: [
      { id: "ess-home", label: "Home", icon: "home", route: "EmployeeHome" },
      { id: "ess-profile", label: "My profile", icon: "user", route: "EmployeeProfile" },
      { id: "ess-attendance", label: "Attendance", icon: "calcheck", route: "EssAttendance" },
      { id: "ess-leave", label: "Leave", icon: "calendar", route: "EssLeave" },
      { id: "ess-payslip", label: "Payslips", icon: "file", route: "EssPayslip" },
      { id: "ess-tax", label: "Tax & FBP", icon: "rupee", route: "EssTax" },
      { id: "ess-reimburse", label: "Reimbursements", icon: "wallet", route: "EssReimburse" },
      { id: "ess-expense", label: "Expenses & advances", icon: "card", route: "EssExpense" },
      { id: "ess-performance", label: "Performance", icon: "target", route: "EssPerformance" },
      { id: "ess-helpdesk", label: "Helpdesk", icon: "help", route: "EssHelpdesk" },
      { id: "ess-directory", label: "Directory", icon: "users", route: "EssDirectory" },
      { id: "ess-announcements", label: "Announcements", icon: "megaphone", route: "EssAnnouncements" },
    ],
  },
  manager: {
    label: "Manager",
    sub: "Team",
    items: [
      { id: "mgr-dashboard", label: "Team dashboard", icon: "home", route: "MgrDashboard" },
      { id: "mgr-approvals", label: "Approvals", icon: "inbox", route: "MgrApprovals" },
      { id: "mgr-attendance", label: "Team attendance", icon: "calcheck", route: "MgrAttendance" },
      { id: "mgr-leave", label: "Team leave", icon: "calendar", route: "MgrLeave" },
      { id: "mgr-performance", label: "Team performance", icon: "target", route: "MgrPerformance" },
      { id: "mgr-orgchart", label: "Org chart", icon: "users", route: "MgrOrgChart" },
    ],
  },
  hr: {
    label: "HR & Payroll",
    sub: "Administrator",
    groups: [
      { label: null, items: [{ id: "hr-dashboard", label: "Dashboard", icon: "home", route: "HrDashboard" }] },
      {
        label: "People",
        items: [
          { id: "hr-directory", label: "Employee directory", icon: "users", route: "HrDirectory" },
          { id: "hr-employee360", label: "Employee 360", icon: "user", route: "HrEmployee360" },
          { id: "hr-onboarding", label: "Onboarding", icon: "login", route: "HrOnboarding" },
          { id: "hr-transfers", label: "Transfers & promotions", icon: "arrowUpRight", route: "HrTransfers" },
          { id: "hr-separation", label: "Separation & exit", icon: "logout", route: "HrSeparation" },
          { id: "hr-orgbuilder", label: "Org chart builder", icon: "layers", route: "HrOrgBuilder" },
        ],
      },
      {
        label: "Attendance",
        items: [
          { id: "hr-attendance", label: "Attendance workspace", icon: "calcheck", route: "HrAttendance" },
          { id: "hr-roster", label: "Shift & roster", icon: "calendar", route: "HrRoster" },
          { id: "hr-biometric", label: "Biometric sync", icon: "dot", route: "HrBiometric" },
          { id: "hr-regularize", label: "Regularization queue", icon: "inbox", route: "HrRegularize" },
        ],
      },
      {
        label: "Payroll",
        items: [
          { id: "hr-payrun", label: "Payroll run", icon: "rupee", route: "HrPayrun" },
          { id: "hr-salstructure", label: "Salary structure", icon: "layers", route: "HrSalStructure" },
          { id: "hr-revisions", label: "Revisions & arrears", icon: "arrowUpRight", route: "HrRevisions" },
          { id: "hr-offcycle", label: "Bonus & off-cycle", icon: "gift", route: "HrOffcycle" },
          { id: "hr-reconcile", label: "Reconciliation", icon: "check", route: "HrReconcile" },
          { id: "hr-bankfile", label: "Bank disbursement", icon: "card", route: "HrBankfile" },
        ],
      },
      {
        label: "Compliance",
        items: [
          { id: "hr-pf", label: "PF dashboard", icon: "shield", route: "CompliancePf" },
          { id: "hr-esi", label: "ESI dashboard", icon: "shield", route: "ComplianceEsi" },
          { id: "hr-pt", label: "PT dashboard", icon: "shield", route: "CompliancePt" },
          { id: "hr-tds", label: "TDS dashboard", icon: "shield", route: "ComplianceTds" },
          { id: "hr-challan", label: "Challan & returns", icon: "file", route: "HrChallan" },
          { id: "hr-statcal", label: "Statutory calendar", icon: "calendar", route: "HrStatcal" },
        ],
      },
      {
        label: "Recruitment",
        items: [
          { id: "hr-jobs", label: "Job openings", icon: "briefcase", route: "HrJobs" },
          { id: "hr-pipeline", label: "Candidate pipeline", icon: "layers", route: "HrPipeline" },
          { id: "hr-interviews", label: "Interview scheduling", icon: "calendar", route: "HrInterviews" },
          { id: "hr-offers", label: "Offer management", icon: "file", route: "HrOffers" },
        ],
      },
      {
        label: "Performance",
        items: [
          { id: "hr-cycle", label: "Appraisal cycle", icon: "target", route: "HrCycle" },
          { id: "hr-calibration", label: "Calibration / 9-box", icon: "layers", route: "HrCalibration" },
          { id: "hr-survey", label: "Survey builder", icon: "edit", route: "HrSurvey" },
        ],
      },
      {
        label: "Analytics",
        items: [
          { id: "hr-analytics", label: "People analytics", icon: "chart", route: "HrAnalytics" },
          { id: "hr-reports", label: "Report builder", icon: "pieChart", route: "HrReports" },
        ],
      },
      { label: null, items: [{ id: "hr-settings", label: "Settings", icon: "settings", route: "HrSettings" }] },
    ],
  },
}

export const ROLES = [
  { id: "employee", label: "Employee", sub: "Self-service", icon: "user" },
  { id: "manager", label: "Manager", sub: "Team", icon: "users" },
  { id: "hr", label: "HR & Payroll", sub: "Administrator", icon: "briefcase" },
]

// Map a Frappe role list to the workspace roles this user may switch between.
// Everyone gets Employee; managers/HR unlock the extra workspaces.
export function rolesForUser(frappeRoles = []) {
  const set = new Set(["employee"])
  const r = frappeRoles || []
  if (r.includes("HR Manager") || r.includes("HR User") || r.includes("System Manager")) {
    set.add("hr")
    set.add("manager")
  }
  // A reporting manager (has direct reports) also gets the manager workspace;
  // resolved server-side later. For now any leave/expense approver role counts.
  if (r.includes("Leave Approver") || r.includes("Expense Approver")) set.add("manager")
  return ROLES.filter((role) => set.has(role.id))
}
