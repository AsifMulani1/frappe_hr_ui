<script setup>
// In-UI access management — create users and grant HR/approver roles. No Desk.
import { ref, reactive, computed } from "vue"
import { Button, FormControl, Checkbox, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.access_api.list_users", auto: true })
const users = computed(() => r.data?.users || [])
const assignable = computed(() => r.data?.assignable || [])
const columns = [
  { key: "full_name", label: "User" },
  { key: "roles", label: "Roles" },
  { key: "employee", label: "Employee" },
  { key: "enabled", label: "Status" },
]

const create = createResource({ url: "frappe_hr_ui.access_api.create_user" })
const setAccess = createResource({ url: "frappe_hr_ui.access_api.set_user_access" })

const d = reactive({ open: false, mode: "new", email: "", first_name: "", last_name: "", roles: [], enabled: true })
function openNew() {
  Object.assign(d, { open: true, mode: "new", email: "", first_name: "", last_name: "", roles: [], enabled: true })
}
function openEdit(u) {
  Object.assign(d, { open: true, mode: "edit", email: u.email, first_name: u.full_name, last_name: "", roles: [...u.roles], enabled: u.enabled })
}
function toggleRole(role) {
  const i = d.roles.indexOf(role)
  if (i === -1) d.roles.push(role); else d.roles.splice(i, 1)
}
function submit() {
  if (d.mode === "new") {
    if (!d.email || !d.first_name) { toast.error("Name and email are required"); return }
    create.submit(
      { email: d.email, first_name: d.first_name, last_name: d.last_name, roles: JSON.stringify(d.roles), send_welcome_email: 0 },
      { onSuccess: () => { toast.success("User created"); d.open = false; r.reload() }, onError: (e) => toast.error(e?.messages?.[0] || "Couldn't create user") }
    )
  } else {
    setAccess.submit(
      { email: d.email, roles: JSON.stringify(d.roles), enabled: d.enabled ? 1 : 0 },
      { onSuccess: () => { toast.success("Access updated"); d.open = false; r.reload() }, onError: (e) => toast.error(e?.messages?.[0] || "Couldn't update") }
    )
  }
}
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Users & Access" subtitle="Create users and grant HR, approver and manager roles">
      <template #actions>
        <Button variant="solid" theme="blue" label="Add User" @click="openNew"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>

    <AsyncShell :resource="r" loading-text="Loading users…">
      <Card :pad="false" class="p-3">
        <DataTable :columns="columns" :rows="users" row-key="email" :loading="r.loading"
          empty-title="No users yet" empty-message="Add a user to grant access." @row-click="openEdit">
          <template #cell-full_name="{ row }">
            <div class="flex items-center gap-2.5"><InitialsAvatar :name="row.full_name" :size="30" />
              <div><div class="font-medium">{{ row.full_name }}</div><div class="text-xs text-ink-gray-5">{{ row.email }}</div></div></div>
          </template>
          <template #cell-roles="{ row }">
            <div class="flex flex-wrap gap-1">
              <StatusBadge v-for="role in row.roles" :key="role" tone="accent" size="sm" :label="role" />
              <span v-if="!row.roles.length" class="text-xs text-ink-gray-4">Employee only</span>
            </div>
          </template>
          <template #cell-employee="{ row }"><span class="text-ink-gray-7">{{ row.employee || "—" }}</span></template>
          <template #cell-enabled="{ row }"><StatusBadge :tone="row.enabled ? 'success' : 'neutral'" size="sm" dot :label="row.enabled ? 'Active' : 'Disabled'" /></template>
        </DataTable>
      </Card>
    </AsyncShell>

    <Drawer :open="d.open" :title="d.mode === 'new' ? 'Add user' : 'Edit access'" :subtitle="d.mode === 'edit' ? d.email : 'Create a login and grant roles'" :width="480" @close="d.open = false">
      <div class="flex flex-col gap-4">
        <template v-if="d.mode === 'new'">
          <div class="grid grid-cols-2 gap-3">
            <FormControl type="text" label="First name" v-model="d.first_name" />
            <FormControl type="text" label="Last name" v-model="d.last_name" />
          </div>
          <FormControl type="email" label="Email (login)" v-model="d.email" />
        </template>
        <div>
          <div class="mb-1.5 text-xs font-medium text-ink-gray-7">Roles</div>
          <div class="flex flex-col gap-2 rounded-md border border-outline-gray-1 p-3">
            <Checkbox v-for="role in assignable" :key="role" :model-value="d.roles.includes(role)" :label="role" @update:model-value="toggleRole(role)" />
          </div>
          <p class="mt-1.5 text-xs text-ink-gray-4">Employee self-service access comes from linking an Employee record to this user.</p>
        </div>
        <Checkbox v-if="d.mode === 'edit'" v-model="d.enabled" label="Account enabled" />
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="d.open = false" />
        <Button variant="solid" theme="blue" :label="d.mode === 'new' ? 'Create user' : 'Save access'" :loading="create.loading || setAccess.loading" @click="submit" />
      </template>
    </Drawer>
  </div>
</template>
