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
      { id: "ess-profile", label: "My profile", icon: "user" },
      { id: "ess-attendance", label: "Attendance", icon: "calcheck" },
      { id: "ess-leave", label: "Leave", icon: "calendar" },
      { id: "ess-payslip", label: "Payslips", icon: "file" },
      { id: "ess-tax", label: "Tax & FBP", icon: "rupee" },
      { id: "ess-reimburse", label: "Reimbursements", icon: "wallet" },
      { id: "ess-expense", label: "Expenses & advances", icon: "card" },
      { id: "ess-performance", label: "Performance", icon: "target" },
      { id: "ess-helpdesk", label: "Helpdesk", icon: "help" },
      { id: "ess-directory", label: "Directory", icon: "users" },
      { id: "ess-announcements", label: "Announcements", icon: "megaphone" },
    ],
  },
  manager: {
    label: "Manager",
    sub: "Team",
    items: [
      { id: "mgr-dashboard", label: "Team dashboard", icon: "home" },
      { id: "mgr-approvals", label: "Approvals", icon: "inbox", badge: 6 },
      { id: "mgr-attendance", label: "Team attendance", icon: "calcheck" },
      { id: "mgr-leave", label: "Team leave", icon: "calendar" },
      { id: "mgr-performance", label: "Team performance", icon: "target" },
      { id: "mgr-orgchart", label: "Org chart", icon: "users" },
    ],
  },
  hr: {
    label: "HR & Payroll",
    sub: "Administrator",
    groups: [
      { label: null, items: [{ id: "hr-dashboard", label: "Dashboard", icon: "home" }] },
      {
        label: "People",
        items: [
          { id: "hr-directory", label: "Employee directory", icon: "users" },
          { id: "hr-employee360", label: "Employee 360", icon: "user" },
          { id: "hr-onboarding", label: "Onboarding", icon: "login" },
          { id: "hr-transfers", label: "Transfers & promotions", icon: "arrowUpRight" },
          { id: "hr-separation", label: "Separation & exit", icon: "logout" },
          { id: "hr-orgbuilder", label: "Org chart builder", icon: "layers" },
        ],
      },
      {
        label: "Attendance",
        items: [
          { id: "hr-attendance", label: "Attendance workspace", icon: "calcheck" },
          { id: "hr-roster", label: "Shift & roster", icon: "calendar" },
          { id: "hr-biometric", label: "Biometric sync", icon: "dot" },
          { id: "hr-regularize", label: "Regularization queue", icon: "inbox" },
        ],
      },
      {
        label: "Payroll",
        items: [
          { id: "hr-payrun", label: "Payroll run", icon: "rupee" },
          { id: "hr-salstructure", label: "Salary structure", icon: "layers" },
          { id: "hr-revisions", label: "Revisions & arrears", icon: "arrowUpRight" },
          { id: "hr-offcycle", label: "Bonus & off-cycle", icon: "gift" },
          { id: "hr-reconcile", label: "Reconciliation", icon: "check" },
          { id: "hr-bankfile", label: "Bank disbursement", icon: "card" },
        ],
      },
      {
        label: "Compliance",
        items: [
          { id: "hr-pf", label: "PF dashboard", icon: "shield" },
          { id: "hr-esi", label: "ESI dashboard", icon: "shield" },
          { id: "hr-pt", label: "PT dashboard", icon: "shield" },
          { id: "hr-tds", label: "TDS dashboard", icon: "shield" },
          { id: "hr-challan", label: "Challan & returns", icon: "file" },
          { id: "hr-statcal", label: "Statutory calendar", icon: "calendar" },
        ],
      },
      {
        label: "Recruitment",
        items: [
          { id: "hr-jobs", label: "Job openings", icon: "briefcase" },
          { id: "hr-pipeline", label: "Candidate pipeline", icon: "layers" },
          { id: "hr-interviews", label: "Interview scheduling", icon: "calendar" },
          { id: "hr-offers", label: "Offer management", icon: "file" },
        ],
      },
      {
        label: "Performance",
        items: [
          { id: "hr-cycle", label: "Appraisal cycle", icon: "target" },
          { id: "hr-calibration", label: "Calibration / 9-box", icon: "layers" },
          { id: "hr-survey", label: "Survey builder", icon: "edit" },
        ],
      },
      {
        label: "Analytics",
        items: [
          { id: "hr-analytics", label: "People analytics", icon: "chart" },
          { id: "hr-reports", label: "Report builder", icon: "pieChart" },
        ],
      },
      { label: null, items: [{ id: "hr-settings", label: "Settings", icon: "settings" }] },
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
