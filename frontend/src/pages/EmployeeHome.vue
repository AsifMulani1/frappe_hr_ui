<script setup>
import { inject } from "vue"
import { createResource } from "frappe-ui"

// Placeholder for screen 1 (Employee home dashboard). This proves the full
// stack end-to-end — session, frappe-ui resources, ₹ data, routing — and is
// replaced by the faithful ess_home.jsx reproduction in the next step.
const user = inject("$user")

const stats = createResource({
  url: "frappe.client.get_count",
  params: { doctype: "Employee" },
  auto: true,
})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-6">
    <h1 class="text-[22px] font-medium tracking-tight text-ink-gray-9">
      Good morning{{ user?.data?.full_name ? `, ${user.data.full_name.split(" ")[0]}` : "" }}
    </h1>
    <p class="mt-1 text-[13.5px] text-ink-gray-5">
      Frappe HR UI is wired up and serving from <code>/hr</code>.
    </p>

    <div class="mt-5 rounded-[10px] border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
      <div class="text-[15px] font-medium text-ink-gray-9">Setup verified</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">
        Live data from the seeded site:
        <span class="font-medium text-ink-gray-9 tnum">{{ stats.data ?? "…" }}</span>
        employees in the directory.
      </p>
      <p class="mt-3 text-[12.5px] text-ink-gray-5">
        Screen 1 (employee home dashboard) is built next as a faithful
        reproduction of <code>ess_home.jsx</code>.
      </p>
    </div>
  </div>
</template>
