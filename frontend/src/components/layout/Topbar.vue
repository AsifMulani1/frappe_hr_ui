<script setup>
import { ref, computed, inject } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Dropdown, createResource } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import { useUiStore } from "@/stores/ui"
import { session } from "@/data/session"

const ui = useUiStore()
const route = useRoute()
const router = useRouter()
const user = inject("$user")

const workspace = computed(() => ui.nav.label)

const title = computed(() => {
  const items = ui.nav.items || ui.nav.groups.flatMap((g) => g.items)
  const found = items.find((i) => i.route && i.route === route.name)
  return found ? found.label : route.meta?.title || "Home"
})

const fullName = computed(() => user?.data?.full_name || session.user || "User")

const userMenu = computed(() => [
  { label: "My profile", onClick: () => router.push("/profile") },
  { label: "Sign out", onClick: () => session.logout.submit() },
])

// Notifications (in-app)
const notifs = createResource({ url: "frappe_hr_ui.api.get_notifications", auto: true })
const markRead = createResource({ url: "frappe_hr_ui.api.mark_notifications_read" })
const notifOpen = ref(false)
const items = computed(() => notifs.data?.items || [])
const unread = computed(() => notifs.data?.unread || 0)
function toggleNotifs() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value && unread.value) {
    markRead.submit().then(() => notifs.reload())
  }
}
</script>

<template>
  <header
    class="flex h-12 shrink-0 items-center gap-2 border-b border-outline-gray-1 bg-surface-white pl-2 pr-4 lg:gap-3 lg:pl-5"
  >
    <!-- Hamburger (mobile only) -->
    <button
      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-ink-gray-7 hover:bg-surface-gray-2 lg:hidden"
      aria-label="Menu"
      @click="ui.toggleMobileNav()"
    >
      <Icon name="menu" :size="20" />
    </button>

    <!-- Breadcrumb -->
    <div class="flex min-w-0 flex-1 items-center gap-1.5">
      <span class="whitespace-nowrap text-sm text-ink-gray-5">{{ workspace }}</span>
      <Icon name="chevRight" :size="14" class="text-ink-gray-4" />
      <span class="truncate text-sm font-medium text-ink-gray-9">{{ title }}</span>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-1">
      <button class="flex h-9 w-9 items-center justify-center rounded-md text-ink-gray-7 hover:bg-surface-gray-2"
        title="Help" @click="router.push('/helpdesk')">
        <Icon name="help" :size="18" />
      </button>

      <!-- Notifications -->
      <div class="relative">
        <button class="relative flex h-9 w-9 items-center justify-center rounded-md text-ink-gray-7 hover:bg-surface-gray-2"
          title="Notifications" @click="toggleNotifs">
          <Icon name="bell" :size="18" />
          <span v-if="unread" class="absolute right-1.5 top-1.5 h-[7px] w-[7px] rounded-full bg-red-500 ring-2 ring-surface-white" />
        </button>
        <template v-if="notifOpen">
          <div class="fixed inset-0 z-[59]" @click="notifOpen = false" />
          <div class="absolute right-0 z-[60] mt-1 w-[340px] rounded-lg border border-outline-gray-1 bg-surface-white shadow-xl">
            <div class="flex items-center justify-between border-b border-outline-gray-1 px-4 py-2.5">
              <span class="text-[13px] font-medium text-ink-gray-9">Notifications</span>
            </div>
            <div class="max-h-[360px] overflow-y-auto">
              <div v-if="!items.length" class="px-4 py-8 text-center text-[12.5px] text-ink-gray-5">You're all caught up.</div>
              <div v-for="n in items" :key="n.name" class="flex gap-2.5 border-b border-outline-gray-1 px-4 py-3 last:border-b-0">
                <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon name="bell" :size="14" /></div>
                <div class="min-w-0 flex-1">
                  <div class="text-[12.5px] leading-snug text-ink-gray-9">{{ n.subject }}</div>
                  <div class="mt-0.5 text-[11px] text-ink-gray-5">{{ n.time }}</div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="mx-1.5 h-[22px] w-px bg-outline-gray-1" />
      <Dropdown :options="userMenu" placement="right">
        <button class="flex items-center gap-2 rounded-md py-1 pl-1 pr-2 hover:bg-surface-gray-2">
          <InitialsAvatar :name="fullName" :size="24" />
          <span class="whitespace-nowrap text-[13px] font-medium text-ink-gray-9">{{ fullName.split(" ")[0] }}</span>
          <Icon name="chevDown" :size="14" class="text-ink-gray-5" />
        </button>
      </Dropdown>
    </div>
  </header>
</template>
