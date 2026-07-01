<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { Button } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import { useUiStore } from "@/stores/ui"
import { NAV, SETTINGS, ADMIN_ROLES } from "@/data/nav"

const ui = useUiStore()
const router = useRouter()
const query = ref("")
const active = ref(0)
const inputRef = ref(null)
const listRef = ref(null)

// Every screen the user can reach, flattened across their workspaces.
const allItems = computed(() => {
  const out = []
  for (const role of ui.availableRoles) {
    const cfg = NAV[role.id]
    if (!cfg) continue
    const items = cfg.items || cfg.groups.flatMap((g) => (g.items || []).map((i) => ({ ...i, group: g.label })))
    for (const it of items) {
      out.push({ ...it, roleId: role.id, roleLabel: role.label })
    }
  }
  // Settings/config items (no longer in the operational nav) stay reachable via
  // ⌘K — but only categories the user can administer (same scoping as the hub).
  const ids = new Set(ui.availableRoles.map((r) => r.id))
  if (ADMIN_ROLES.some((r) => ids.has(r))) {
    for (const cat of SETTINGS) {
      if (!(cat.roles || []).some((r) => ids.has(r))) continue
      for (const it of cat.items) {
        out.push({ ...it, roleId: null, group: cat.label, roleLabel: "Settings" })
      }
    }
  }
  return out
})

const results = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return allItems.value
  return allItems.value.filter((i) =>
    (i.label + " " + (i.group || "") + " " + i.roleLabel).toLowerCase().includes(q)
  )
})

watch(results, () => { active.value = 0 })

watch(
  () => ui.searchOpen,
  (open) => {
    if (open) {
      query.value = ""
      active.value = 0
      nextTick(() => inputRef.value?.focus())
    }
  }
)

function go(item) {
  if (!item) return
  if (item.roleId !== ui.activeRole) ui.setRole(item.roleId)
  ui.closeSearch()
  router.push({ name: item.route }).catch(() => {})
}

function move(delta) {
  const n = results.value.length
  if (!n) return
  active.value = (active.value + delta + n) % n
  nextTick(() => {
    const el = listRef.value?.querySelector(`[data-idx="${active.value}"]`)
    el?.scrollIntoView({ block: "nearest" })
  })
}

function onGlobalKey(e) {
  if ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")) {
    e.preventDefault()
    ui.searchOpen ? ui.closeSearch() : ui.openSearch()
  } else if (e.key === "Escape" && ui.searchOpen) {
    ui.closeSearch()
  }
}
onMounted(() => document.addEventListener("keydown", onGlobalKey))
onUnmounted(() => document.removeEventListener("keydown", onGlobalKey))
</script>

<template>
  <Teleport to="body">
    <div v-if="ui.searchOpen" class="fixed inset-0 z-[80] flex items-start justify-center px-4 pt-[12vh]">
      <div class="absolute inset-0 bg-black/30" @click="ui.closeSearch()" />
      <div class="relative w-full max-w-[560px] overflow-hidden rounded-xl border border-outline-gray-2 bg-surface-white shadow-2xl">
        <!-- input -->
        <div class="flex items-center gap-2.5 border-b border-outline-gray-1 px-4">
          <Icon name="search" :size="17" class="text-ink-gray-5" />
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            placeholder="Search screens…"
            class="h-12 flex-1 border-none bg-transparent text-base text-ink-gray-9 shadow-none outline-none ring-0 focus:border-none focus:shadow-none focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0 placeholder:text-ink-gray-4"
            @keydown.down.prevent="move(1)"
            @keydown.up.prevent="move(-1)"
            @keydown.enter.prevent="go(results[active])"
          />
          <kbd class="rounded border border-outline-gray-2 bg-surface-gray-1 px-1.5 py-0.5 font-mono text-2xs text-ink-gray-5">esc</kbd>
        </div>

        <!-- results -->
        <div ref="listRef" class="max-h-[52vh] overflow-y-auto p-1.5">
          <Button
            v-for="(it, i) in results"
            :key="it.roleId + it.id"
            :data-idx="i"
            :variant="i === active ? 'subtle' : 'ghost'"
            theme="gray"
            class="w-full !justify-start"
            @click="go(it)"
            @mousemove="active = i"
          >
            <template #prefix>
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7">
                <Icon :name="it.icon" :size="15" />
              </div>
            </template>
            <span class="flex-1 truncate text-sm text-ink-gray-9">{{ it.label }}</span>
            <template #suffix>
              <span class="shrink-0 text-2xs text-ink-gray-5">{{ it.group ? `${it.roleLabel} · ${it.group}` : it.roleLabel }}</span>
            </template>
          </Button>
          <div v-if="!results.length" class="px-3 py-8 text-center text-sm text-ink-gray-5">
            No screens match “{{ query }}”.
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
