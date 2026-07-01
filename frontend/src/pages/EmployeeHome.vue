<script setup>
import { computed, inject, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource, toast } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import { userResource } from "@/data/user"
import GettingStarted from "@/components/home/GettingStarted.vue"
import CheckinHero from "@/components/home/CheckinHero.vue"
import LeaveBalanceCard from "@/components/home/LeaveBalanceCard.vue"
import QuickActions from "@/components/home/QuickActions.vue"
import TasksCard from "@/components/home/TasksCard.vue"
import AnnouncementsCard from "@/components/home/AnnouncementsCard.vue"
import PayslipMini from "@/components/home/PayslipMini.vue"
import WhoIsOut from "@/components/home/WhoIsOut.vue"
import HolidaysCard from "@/components/home/HolidaysCard.vue"
import CelebrationsCard from "@/components/home/CelebrationsCard.vue"
import { useEmployeeHome } from "@/composables/useEmployeeHome"

const dayjs = inject("$dayjs")
const router = useRouter()
const home = useEmployeeHome()

const d = computed(() => home.data || {})
const emp = computed(() => d.value.employee)

const greeting = computed(() => {
  const h = dayjs().hour()
  return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening"
})
const dateLine = computed(() => {
  const parts = [dayjs().format("dddd, D MMMM YYYY")]
  if (emp.value?.location) parts.push(emp.value.location)
  if (emp.value?.shift_label) parts.push(emp.value.shift_label)
  return parts.join(" · ")
})

const headerToggle = createResource({
  url: "frappe_hr_ui.api.toggle_checkin",
  onSuccess: () => {
    toast.success(checkedIn.value ? "Checked out" : "Checked in")
    home.reload()
  },
  onError: (e) => toast.error(e?.messages?.[0] || "Couldn't update your check-in. Please try again."),
})
const checkedIn = computed(() => d.value.today?.checked_in)

// Admins drive setup; show them the getting-started checklist even before they
// have an Employee record (a fresh-site owner has none).
onMounted(() => { if (!userResource.data && !userResource.loading) userResource.fetch() })
const isAdmin = computed(() =>
  (userResource.data?.roles || []).some((r) => ["System Manager", "HR Manager", "HR User"].includes(r)))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <!-- loading -->
    <div v-if="home.loading && !home.data" class="flex h-[60vh] items-center justify-center text-ink-gray-5">
      <div class="flex items-center gap-2 text-sm">
        <Icon name="dot" :size="18" class="animate-pulse" /> Loading your dashboard…
      </div>
    </div>

    <!-- error -->
    <div v-else-if="home.error" class="flex h-[60vh] flex-col items-center justify-center gap-2 text-center">
      <div class="text-md font-medium text-ink-gray-8">Couldn't load your dashboard</div>
      <div class="max-w-md text-sm text-ink-gray-5">{{ home.error.messages?.[0] || home.error }}</div>
      <Button class="mt-2" variant="subtle" theme="gray" label="Retry" @click="home.reload()" />
    </div>

    <!-- admin onboarding + self-service dashboard -->
    <template v-else>
      <GettingStarted v-if="isAdmin" class="mb-5" />

      <!-- no employee linked (shown only to non-admins; admins get the checklist above) -->
      <div v-if="!emp && !isAdmin" class="flex h-[60vh] flex-col items-center justify-center gap-2 text-center">
        <Icon name="user" :size="26" class="text-ink-gray-4" />
        <div class="text-md font-medium text-ink-gray-8">No employee record linked</div>
        <div class="max-w-md text-sm text-ink-gray-5">
          This user isn't linked to an Employee. Sign in as an employee (e.g. aarav.mehta@frappe.io)
          to see the self-service dashboard.
        </div>
      </div>

      <!-- self-service dashboard -->
      <template v-else-if="emp">
      <div class="mb-[18px] flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 class="text-3xl font-medium tracking-tight text-ink-gray-9">
            {{ greeting }}, {{ emp.first_name || emp.employee_name }}
          </h1>
          <div class="mt-1 text-sm text-ink-gray-5">{{ dateLine }}</div>
        </div>
        <div class="flex gap-2">
          <Button variant="outline" theme="gray" label="Apply for Leave" @click="router.push('/leave')">
            <template #prefix><Icon name="calendar" :size="15" /></template>
          </Button>
          <Button
            variant="solid"
            theme="gray"
            :loading="headerToggle.loading"
            :label="checkedIn ? 'Check out' : 'Check in'"
            @click="headerToggle.submit()"
          >
            <template #prefix><Icon :name="checkedIn ? 'logout' : 'login'" :size="15" /></template>
          </Button>
        </div>
      </div>

      <div class="grid items-start gap-5" style="grid-template-columns: minmax(0, 1fr) 312px">
        <div class="flex flex-col gap-5">
          <CheckinHero
            :today="d.today"
            :week="d.week"
            :summary="d.attendance_summary"
            :shift="emp.shift_label"
            :on-reload="() => home.reload()"
          />
          <LeaveBalanceCard :balances="d.leave_balance || []" />
          <QuickActions />
          <div class="grid grid-cols-2 gap-5">
            <TasksCard :tasks="d.tasks || []" />
            <AnnouncementsCard :announcements="d.announcements || []" />
          </div>
        </div>
        <div class="flex flex-col gap-5">
          <PayslipMini :payslip="d.latest_payslip" />
          <WhoIsOut :people="d.who_is_out || []" />
          <HolidaysCard :holidays="d.holidays || []" />
          <CelebrationsCard :celebrations="d.celebrations || []" />
        </div>
      </div>
      </template>
    </template>
  </div>
</template>
