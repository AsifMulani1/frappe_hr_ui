import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { NAV, ROLES, rolesForUser } from "@/data/nav"
import { userResource } from "@/data/user"

export const useUiStore = defineStore("ui", () => {
  const activeRole = ref("employee")
  const sidebarCollapsed = ref(false)
  const searchOpen = ref(false)
  const mobileNavOpen = ref(false) // off-canvas sidebar on phones

  function toggleMobileNav() {
    mobileNavOpen.value = !mobileNavOpen.value
  }
  function closeMobileNav() {
    mobileNavOpen.value = false
  }

  function openSearch() {
    searchOpen.value = true
  }
  function closeSearch() {
    searchOpen.value = false
  }

  const availableRoles = computed(() => {
    const frappeRoles = userResource.data?.roles || []
    const roles = rolesForUser(frappeRoles)
    return roles.length ? roles : ROLES.filter((r) => r.id === "employee")
  })

  const nav = computed(() => NAV[activeRole.value])

  function setRole(id) {
    if (NAV[id]) activeRole.value = id
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return { activeRole, sidebarCollapsed, searchOpen, openSearch, closeSearch, availableRoles, nav, setRole, toggleSidebar, mobileNavOpen, toggleMobileNav, closeMobileNav }
})
