// Shared ₹ formatting — Indian grouping + lakh/crore short form.
// Single source of truth used by every screen (per build spec §6).

const inrFormatter = new Intl.NumberFormat("en-IN", {
  maximumFractionDigits: 0,
})

export function formatINR(value) {
  const n = Number(value || 0)
  return "₹" + inrFormatter.format(Math.round(n))
}

// Short form: ₹3.42 Cr / ₹1.42 L / ₹98,640
export function formatINRShort(value) {
  const n = Number(value || 0)
  if (Math.abs(n) >= 10000000) {
    return "₹" + (n / 10000000).toFixed(2).replace(/\.00$/, "") + " Cr"
  }
  if (Math.abs(n) >= 100000) {
    return "₹" + (n / 100000).toFixed(2).replace(/\.00$/, "") + " L"
  }
  return formatINR(n)
}

export function initials(name) {
  if (!name) return "?"
  const parts = String(name).trim().split(/\s+/)
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase()
}
