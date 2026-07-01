<script setup>
import { ref, computed } from "vue"
import { useRouter, useRoute } from "vue-router"
import { Dropdown, Button } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import BrandLogo from "@/components/ui/BrandLogo.vue"
import { useUiStore } from "@/stores/ui"
import { ADMIN_ROLES } from "@/data/nav"

const ui = useUiStore()
const router = useRouter()
const route = useRoute()

const collapsed = computed(() => ui.sidebarCollapsed)
const showSettings = computed(() => ADMIN_ROLES.includes(ui.activeRole))
const settingsActive = computed(() => String(route.name || "").startsWith("Settings") || String(route.path || "").startsWith("/settings") || String(route.path || "").startsWith("/config"))
const cfg = computed(() => ui.nav)
const currentRole = computed(() => ui.availableRoles.find((r) => r.id === ui.activeRole) || ui.availableRoles[0])

const roleOptions = computed(() =>
  ui.availableRoles.map((r) => ({
    label: r.label,
    onClick: () => ui.setRole(r.id),
  }))
)

// Flatten groups -> items for active-state matching.
function navItems(c) {
  return c.items || c.groups.flatMap((g) => g.items)
}

function go(item) {
  if (item.route) router.push({ name: item.route })
  else router.push(`/screen/${item.id}`)
  ui.closeMobileNav()
}

function isActive(item) {
  return (item.route && route.name === item.route) || route.params.id === item.id
}
</script>

<template>
  <aside
    class="fixed inset-y-0 left-0 z-[70] flex h-full w-[232px] flex-col border-r border-outline-gray-1 bg-surface-menu-bar transition-transform lg:static lg:z-auto lg:translate-x-0 lg:transition-all"
    :class="[
      collapsed ? 'lg:w-[60px]' : 'lg:w-[232px]',
      ui.mobileNavOpen ? 'translate-x-0' : '-translate-x-full',
    ]"
  >
    <!-- Workspace switcher -->
    <div class="px-2.5 pb-1.5 pt-2.5">
      <Dropdown :options="roleOptions" placement="left">
        <Button
          variant="ghost"
          class="w-full"
          :class="collapsed ? '!justify-center' : '!justify-start'"
        >
          <template #prefix><BrandLogo :size="26" class="shrink-0" /></template>
          <span v-if="!collapsed" class="min-w-0 flex-1 text-left leading-tight">
            <span class="block truncate text-[13px] font-medium text-ink-gray-9">Frappe HR</span>
            <span class="block truncate text-[11px] text-ink-gray-5">{{ currentRole?.label }}</span>
          </span>
          <template v-if="!collapsed" #suffix><Icon name="chevUpDown" :size="15" class="text-ink-gray-5" /></template>
        </Button>
      </Dropdown>
    </div>

    <!-- Search -->
    <div v-if="!collapsed" class="px-2.5 pb-2">
      <Button
        variant="ghost"
        class="w-full !justify-start"
        @click="ui.openSearch()"
      >
        <template #prefix><Icon name="search" :size="14" /></template>
        <span class="flex-1 text-left text-[13px]">Search</span>
        <template #suffix>
          <kbd
            class="rounded border border-outline-gray-1 bg-surface-white px-1 font-mono text-[11px] text-ink-gray-5"
            >⌘K</kbd
          >
        </template>
      </Button>
    </div>
    <!-- collapsed: search icon -->
    <div v-else class="px-2.5 pb-2">
      <Button
        variant="ghost"
        class="w-full !justify-center"
        label="Search"
        tooltip="Search (⌘K)"
        @click="ui.openSearch()"
      >
        <template #icon><Icon name="search" :size="15" /></template>
      </Button>
    </div>

    <!-- Nav -->
    <nav class="flex flex-1 flex-col gap-px overflow-y-auto px-2.5 py-0.5">
      <!-- Flat items (employee / manager) -->
      <template v-if="cfg.items">
        <Button
          v-for="it in cfg.items"
          :key="it.id"
          :variant="isActive(it) ? 'subtle' : 'ghost'"
          theme="gray"
          class="w-full"
          :class="collapsed ? '!justify-center' : '!justify-start'"
          :label="collapsed ? it.label : undefined"
          :tooltip="collapsed ? it.label : undefined"
          @click="go(it)"
        >
          <template v-if="collapsed" #icon>
            <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
          </template>
          <template v-else #prefix>
            <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
          </template>
          <span v-if="!collapsed" class="flex-1 truncate text-left">{{ it.label }}</span>
          <template v-if="!collapsed && it.badge" #suffix>
            <span
              class="flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-surface-gray-3 px-1.5 text-[11px] font-medium text-ink-gray-7"
              >{{ it.badge }}</span
            >
          </template>
        </Button>
      </template>

      <!-- Grouped items (hr) -->
      <template v-else>
        <div v-for="(g, gi) in cfg.groups" :key="gi" :class="g.label ? 'mb-2' : 'mb-px'">
          <div
            v-if="g.label && !collapsed"
            class="px-2 pb-1 pt-2.5 text-[11px] tracking-[.01em] text-ink-gray-5"
          >
            {{ g.label }}
          </div>
          <div class="flex flex-col gap-0.5">
            <Button
              v-for="it in g.items"
              :key="it.id"
              :variant="isActive(it) ? 'subtle' : 'ghost'"
              theme="gray"
              class="w-full"
              :class="collapsed ? '!justify-center' : '!justify-start'"
              :label="collapsed ? it.label : undefined"
              :tooltip="collapsed ? it.label : undefined"
              @click="go(it)"
            >
              <template v-if="collapsed" #icon>
                <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
              </template>
              <template v-else #prefix>
                <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
              </template>
              <span v-if="!collapsed" class="flex-1 truncate text-left">{{ it.label }}</span>
            </Button>
          </div>
        </div>
      </template>
    </nav>

    <!-- Settings (admin workspaces only) + Collapse toggle -->
    <div class="border-t border-outline-gray-1 p-3">
      <Button
        v-if="showSettings"
        :variant="settingsActive ? 'subtle' : 'ghost'"
        theme="gray"
        class="mb-0.5 w-full"
        :class="collapsed ? '!justify-center' : '!justify-start'"
        :label="collapsed ? 'Settings' : undefined"
        :tooltip="collapsed ? 'Settings' : undefined"
        @click="router.push({ name: 'Settings' }); ui.closeMobileNav()"
      >
        <template v-if="collapsed" #icon>
          <Icon name="settings" :size="16" :class="settingsActive ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
        </template>
        <template v-else #prefix>
          <Icon name="settings" :size="16" :class="settingsActive ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
        </template>
        <span v-if="!collapsed" class="flex-1 text-left">Settings</span>
      </Button>
      <Button
        variant="ghost"
        class="hidden w-full lg:flex"
        :class="collapsed ? '!justify-center' : '!justify-start'"
        :label="collapsed ? 'Expand' : undefined"
        :tooltip="collapsed ? 'Expand' : undefined"
        @click="ui.toggleSidebar()"
      >
        <template v-if="collapsed" #icon><Icon name="chevRight" :size="18" /></template>
        <template v-else #prefix><Icon name="chevLeft" :size="18" /></template>
        <span v-if="!collapsed" class="text-[13px]">Collapse</span>
      </Button>
    </div>
  </aside>
</template>
