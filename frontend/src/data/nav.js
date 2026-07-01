// Role-aware navigation. The admin surface is split into three focused
// workspaces — People, Recruitment, Payroll — instead of one overwhelming
// "HR & Payroll" rail. Configuration is NOT here; it lives in the Settings hub
// (see SETTINGS below) behind a gear, so the operational nav stays calm.
//
// `icon` values are keys into components/ui/Icon.vue's lucide registry.
// `route` is the Vue Router name. Each workspace uses `items` (flat) or
// `groups` ([{ label, items }]); the Sidebar + CommandPalette read both shapes.

export const NAV = {
  employee: {
    label: "Me",
    sub: "Self-service",
    groups: [
      {
        label: null,
        items: [
          { id: "ess-home", label: "Home", icon: "home", route: "EmployeeHome" },
          { id: "ess-profile", label: "My Profile", icon: "user", route: "EmployeeProfile" },
        ],
      },
      {
        label: "Time off & Attendance",
        items: [
          { id: "ess-attendance", label: "Attendance", icon: "calcheck", route: "EssAttendance" },
          { id: "ess-leave", label: "Leave", icon: "calendar", route: "EssLeave" },
          { id: "ess-compoff", label: "Comp-off", icon: "clock", route: "EssCompOff" },
          { id: "ess-encashment", label: "Leave Encashment", icon: "rupee", route: "EssEncashment" },
        ],
      },
      {
        label: "Pay & Expenses",
        items: [
          { id: "ess-payslip", label: "Payslips", icon: "file", route: "EssPayslip" },
          { id: "ess-tax", label: "Tax & FBP", icon: "rupee", route: "EssTax" },
          { id: "ess-reimburse", label: "Reimbursements", icon: "wallet", route: "EssReimburse" },
          { id: "ess-expense", label: "Expenses & Advances", icon: "card", route: "EssExpense" },
          { id: "ess-advance", label: "Advances", icon: "wallet", route: "EssAdvance" },
        ],
      },
      {
        label: "Workplace",
        items: [
          { id: "ess-performance", label: "Performance", icon: "target", route: "EssPerformance" },
          { id: "ess-helpdesk", label: "Helpdesk", icon: "help", route: "EssHelpdesk" },
          { id: "ess-directory", label: "Directory", icon: "users", route: "EssDirectory" },
          { id: "ess-announcements", label: "Announcements", icon: "megaphone", route: "EssAnnouncements" },
        ],
      },
    ],
  },

  manager: {
    label: "Team",
    sub: "Manager",
    items: [
      { id: "mgr-dashboard", label: "Team Dashboard", icon: "home", route: "MgrDashboard" },
      { id: "mgr-approvals", label: "Approvals", icon: "inbox", route: "MgrApprovals" },
      { id: "mgr-attendance", label: "Team Attendance", icon: "calcheck", route: "MgrAttendance" },
      { id: "mgr-leave", label: "Team Leave", icon: "calendar", route: "MgrLeave" },
      { id: "mgr-performance", label: "Team Performance", icon: "target", route: "MgrPerformance" },
      { id: "mgr-orgchart", label: "Org Chart", icon: "users", route: "MgrOrgChart" },
    ],
  },

  people: {
    label: "People",
    sub: "HR",
    groups: [
      { label: null, items: [{ id: "hr-dashboard", label: "Dashboard", icon: "home", route: "HrDashboard" }] },
      {
        label: "People",
        items: [
          { id: "hr-directory", label: "Employee Directory", icon: "users", route: "HrDirectory" },
          { id: "hr-employee360", label: "Employee 360", icon: "user", route: "HrEmployee360" },
          { id: "hr-onboarding", label: "Onboarding", icon: "login", route: "HrOnboarding" },
          { id: "hr-transfers", label: "Transfers & Promotions", icon: "arrowUpRight", route: "HrTransfers" },
          { id: "hr-separation", label: "Separation & Exit", icon: "logout", route: "HrSeparation" },
          { id: "hr-orgbuilder", label: "Org Chart Builder", icon: "layers", route: "HrOrgBuilder" },
        ],
      },
      {
        label: "Time & Attendance",
        items: [
          { id: "hr-attendance", label: "Attendance Workspace", icon: "calcheck", route: "HrAttendance" },
          { id: "hr-roster", label: "Shift & Roster", icon: "calendar", route: "HrRoster" },
          { id: "hr-biometric", label: "Biometric Sync", icon: "dot", route: "HrBiometric" },
          { id: "hr-regularize", label: "Regularization Queue", icon: "inbox", route: "HrRegularize" },
        ],
      },
      {
        label: "Performance",
        items: [
          { id: "hr-cycle", label: "Appraisal Cycle", icon: "target", route: "HrCycle" },
          { id: "hr-calibration", label: "Calibration / 9-Box", icon: "layers", route: "HrCalibration" },
          { id: "hr-survey", label: "Survey Builder", icon: "edit", route: "HrSurvey" },
        ],
      },
      {
        label: "Cases",
        items: [
          { id: "hr-grievances", label: "Grievances", icon: "inbox", route: "CfgGrievance" },
          { id: "hr-promotions", label: "Promotions", icon: "arrowUpRight", route: "CfgPromotion" },
          { id: "hr-exit-interviews", label: "Exit Interviews", icon: "logout", route: "CfgExitInterview" },
        ],
      },
      {
        label: "Insights",
        items: [
          { id: "hr-analytics", label: "People Analytics", icon: "chart", route: "HrAnalytics" },
          { id: "hr-reports", label: "Report Builder", icon: "pieChart", route: "HrReports" },
        ],
      },
    ],
  },

  recruitment: {
    label: "Recruitment",
    sub: "Hiring",
    groups: [
      { label: null, items: [{ id: "rec-dashboard", label: "Dashboard", icon: "home", route: "RecruitmentDashboard" }] },
      {
        label: "Hiring",
        items: [
          { id: "hr-jobs", label: "Job Openings", icon: "briefcase", route: "HrJobs" },
          { id: "hr-pipeline", label: "Candidate Pipeline", icon: "layers", route: "HrPipeline" },
          { id: "hr-interviews", label: "Interview Scheduling", icon: "calendar", route: "HrInterviews" },
          { id: "hr-offers", label: "Offer Management", icon: "file", route: "HrOffers" },
        ],
      },
    ],
  },

  payroll: {
    label: "Payroll",
    sub: "Pay & compliance",
    groups: [
      { label: null, items: [{ id: "pay-dashboard", label: "Dashboard", icon: "home", route: "PayrollDashboard" }] },
      {
        label: "Pay",
        items: [
          { id: "hr-payrun", label: "Payroll Run", icon: "rupee", route: "HrPayrun" },
          { id: "hr-salstructure", label: "Salary Structure", icon: "layers", route: "HrSalStructure" },
          { id: "hr-revisions", label: "Revisions & Arrears", icon: "arrowUpRight", route: "HrRevisions" },
          { id: "hr-offcycle", label: "Bonus & Off-cycle", icon: "gift", route: "HrOffcycle" },
          { id: "hr-reconcile", label: "Reconciliation", icon: "check", route: "HrReconcile" },
          { id: "hr-bankfile", label: "Bank Disbursement", icon: "card", route: "HrBankfile" },
        ],
      },
      {
        label: "Compliance",
        items: [
          { id: "hr-pf", label: "PF Dashboard", icon: "shield", route: "CompliancePf" },
          { id: "hr-esi", label: "ESI Dashboard", icon: "shield", route: "ComplianceEsi" },
          { id: "hr-pt", label: "PT Dashboard", icon: "shield", route: "CompliancePt" },
          { id: "hr-lwf", label: "LWF Dashboard", icon: "shield", route: "ComplianceLwf" },
          { id: "hr-tds", label: "TDS Dashboard", icon: "shield", route: "ComplianceTds" },
          { id: "hr-challan", label: "Challan & Returns", icon: "file", route: "HrChallan" },
          { id: "hr-statcal", label: "Statutory Calendar", icon: "calendar", route: "HrStatcal" },
        ],
      },
      {
        label: "Offboarding",
        items: [
          { id: "hr-fnf", label: "Full & Final", icon: "rupee", route: "CfgFnF" },
        ],
      },
    ],
  },
}

// ---- Settings hub --------------------------------------------------------
// Configuration lives here, NOT in the operational nav. Rendered by
// pages/SettingsHub.vue as a categorized, macOS-Settings-style surface and
// reached via the gear in the sidebar footer (admins only). Every item reuses
// an existing route/page — this is pure information architecture, no new CRUD.
// Each category declares the workspaces (`roles`) it belongs to. SettingsHub
// and the command palette show a category only if the user can access one of
// those workspaces — so a recruiter never sees Payroll settings.
export const SETTINGS = [
  {
    label: "Organization",
    icon: "layers",
    roles: ["people", "payroll"],
    items: [
      { id: "cfg-departments", label: "Departments", icon: "layers", route: "CfgDepartment", desc: "Org units and reporting lines" },
      { id: "cfg-designations", label: "Designations", icon: "briefcase", route: "CfgDesignation", desc: "Job titles across the company" },
      { id: "cfg-grades", label: "Employee Grades", icon: "users", route: "CfgGrade", desc: "Bands that drive pay and policy" },
      { id: "cfg-employment-types", label: "Employment Types", icon: "user", route: "CfgEmploymentType", desc: "Full-time, contract, intern…" },
    ],
  },
  {
    label: "Time & Leave",
    icon: "calendar",
    roles: ["people"],
    items: [
      { id: "cfg-leave-types", label: "Leave Types", icon: "calendar", route: "CfgLeaveType", desc: "Casual, sick, earned and more" },
      { id: "cfg-leave-policies", label: "Leave Policies", icon: "file", route: "CfgLeavePolicy", desc: "Allocation rules by grade" },
      { id: "cfg-shift-types", label: "Shift Types", icon: "clock", route: "CfgShiftType", desc: "Working hours and rosters" },
      { id: "cfg-holiday-lists", label: "Holiday Lists", icon: "calendar", route: "CfgHolidayList", desc: "Regional holiday calendars" },
    ],
  },
  {
    label: "Payroll",
    icon: "rupee",
    roles: ["payroll"],
    items: [
      { id: "cfg-salary-components", label: "Salary Components", icon: "rupee", route: "CfgSalaryComponent", desc: "Earnings and deductions" },
      { id: "cfg-tax-slabs", label: "Income Tax Slabs", icon: "rupee", route: "CfgTaxSlab", desc: "Regime and slab rates" },
      { id: "cfg-expense-types", label: "Expense Types", icon: "wallet", route: "CfgExpenseType", desc: "Claimable expense categories" },
      { id: "cfg-payroll-settings", label: "Payroll Settings", icon: "settings", route: "CfgPayrollSettings", desc: "Pay cycle and statutory defaults" },
    ],
  },
  {
    label: "Performance",
    icon: "target",
    roles: ["people"],
    items: [
      { id: "cfg-appraisal-templates", label: "Appraisal Templates", icon: "target", route: "CfgAppraisalTemplate", desc: "Review forms and rating scales" },
      { id: "cfg-kras", label: "KRAs", icon: "target", route: "CfgKRA", desc: "Key result areas" },
    ],
  },
  {
    label: "System",
    icon: "settings",
    roles: ["people", "payroll", "recruitment"],
    items: [
      { id: "cfg-setup", label: "Setup Wizard", icon: "check", route: "SetupWizard", desc: "Guided first-run setup" },
      { id: "cfg-statutory", label: "Statutory Profile", icon: "shield", route: "StatutoryProfile", desc: "PF / ESI / PT / TAN registration numbers" },
      { id: "cfg-hr-settings", label: "HR Settings", icon: "settings", route: "CfgHRSettings", desc: "Org-wide HR preferences" },
      { id: "cfg-access", label: "Users & Access", icon: "users", route: "HrAccess", desc: "Invite users and assign roles" },
    ],
  },
]

export const ROLES = [
  { id: "employee", label: "Me", sub: "Self-service", icon: "user" },
  { id: "manager", label: "Team", sub: "Manager", icon: "users" },
  { id: "people", label: "People", sub: "HR", icon: "briefcase" },
  { id: "recruitment", label: "Recruitment", sub: "Hiring", icon: "target" },
  { id: "payroll", label: "Payroll", sub: "Pay & compliance", icon: "rupee" },
]

// Admin workspaces that unlock the Settings hub (gear in the sidebar footer).
export const ADMIN_ROLES = ["people", "recruitment", "payroll"]

// Map a Frappe role list to the workspaces this user may switch between.
// Everyone gets self-service; HR unlocks the full admin set; a recruiter gets
// just Recruitment; an approver/reporting manager gets Team.
export function rolesForUser(frappeRoles = []) {
  const r = frappeRoles || []
  const set = new Set(["employee"])
  const isHR = r.includes("HR Manager") || r.includes("HR User") || r.includes("System Manager")
  if (isHR) {
    set.add("manager")
    set.add("people")
    set.add("recruitment")
    set.add("payroll")
  }
  if (r.includes("Recruiter")) set.add("recruitment")
  if (r.includes("Leave Approver") || r.includes("Expense Approver")) set.add("manager")
  return ROLES.filter((role) => set.has(role.id))
}
