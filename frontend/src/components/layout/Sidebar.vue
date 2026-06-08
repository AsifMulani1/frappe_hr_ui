<script setup>
import { ref, computed } from "vue"
import { useRouter, useRoute } from "vue-router"
import { Dropdown } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import { useUiStore } from "@/stores/ui"

const ui = useUiStore()
const router = useRouter()
const route = useRoute()

const collapsed = computed(() => ui.sidebarCollapsed)
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
}

function isActive(item) {
  return (item.route && route.name === item.route) || route.params.id === item.id
}
</script>

<template>
  <aside
    class="flex h-full flex-col border-r border-outline-gray-1 bg-surface-menu-bar transition-all"
    :class="collapsed ? 'w-[60px]' : 'w-[232px]'"
  >
    <!-- Workspace switcher -->
    <div class="px-2.5 pb-1.5 pt-2.5">
      <Dropdown :options="roleOptions" placement="left">
        <button
          class="flex h-10 w-full items-center gap-2.5 rounded-md px-2 hover:bg-surface-gray-2"
          :class="collapsed ? 'justify-center' : ''"
        >
          <span
            class="flex h-[26px] w-[26px] shrink-0 items-center justify-center rounded-[7px] bg-gray-900 text-[13px] font-semibold text-white"
            >F</span
          >
          <span v-if="!collapsed" class="min-w-0 flex-1 text-left leading-tight">
            <span class="block truncate text-[13px] font-medium text-ink-gray-9">Frappe HR</span>
            <span class="block truncate text-[11px] text-ink-gray-5">{{ currentRole?.label }}</span>
          </span>
          <Icon v-if="!collapsed" name="chevUpDown" :size="15" class="text-ink-gray-5" />
        </button>
      </Dropdown>
    </div>

    <!-- Search -->
    <div v-if="!collapsed" class="px-2.5 pb-2">
      <div
        class="flex h-[30px] items-center gap-1.5 rounded-md bg-surface-gray-2 px-2 text-ink-gray-5"
      >
        <Icon name="search" :size="14" />
        <span class="flex-1 text-[13px]">Search</span>
        <kbd
          class="rounded border border-outline-gray-1 bg-surface-white px-1 font-mono text-[11px] text-ink-gray-5"
          >⌘K</kbd
        >
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex flex-1 flex-col gap-px overflow-y-auto px-2.5 py-0.5">
      <!-- Flat items (employee / manager) -->
      <template v-if="cfg.items">
        <button
          v-for="it in cfg.items"
          :key="it.id"
          :title="collapsed ? it.label : undefined"
          class="flex h-8 items-center gap-2.5 rounded-md border-none text-[13px] transition-colors"
          :class="[
            collapsed ? 'justify-center px-0' : 'px-2',
            isActive(it)
              ? 'bg-surface-gray-3 font-medium text-ink-gray-9'
              : 'font-normal text-ink-gray-7 hover:bg-surface-gray-2',
          ]"
          @click="go(it)"
        >
          <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
          <span v-if="!collapsed" class="flex-1 truncate text-left">{{ it.label }}</span>
          <span
            v-if="!collapsed && it.badge"
            class="flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-surface-gray-3 px-1.5 text-[11px] font-medium text-ink-gray-7"
            >{{ it.badge }}</span
          >
        </button>
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
            <button
              v-for="it in g.items"
              :key="it.id"
              :title="collapsed ? it.label : undefined"
              class="flex h-8 items-center gap-2.5 rounded-md border-none text-[13px] transition-colors"
              :class="[
                collapsed ? 'justify-center px-0' : 'px-2',
                isActive(it)
                  ? 'bg-surface-gray-3 font-medium text-ink-gray-9'
                  : 'font-normal text-ink-gray-7 hover:bg-surface-gray-2',
              ]"
              @click="go(it)"
            >
              <Icon :name="it.icon" :size="16" :class="isActive(it) ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
              <span v-if="!collapsed" class="flex-1 truncate text-left">{{ it.label }}</span>
            </button>
          </div>
        </div>
      </template>
    </nav>

    <!-- Collapse toggle -->
    <div class="border-t border-outline-gray-1 p-3">
      <button
        class="flex h-[34px] w-full items-center gap-2.5 rounded-md border-none bg-transparent text-ink-gray-5 hover:bg-surface-gray-2"
        :class="collapsed ? 'justify-center px-0' : 'px-2.5'"
        @click="ui.toggleSidebar()"
      >
        <Icon :name="collapsed ? 'chevRight' : 'chevLeft'" :size="18" />
        <span v-if="!collapsed" class="text-[13px]">Collapse</span>
      </button>
    </div>
  </aside>
</template>
