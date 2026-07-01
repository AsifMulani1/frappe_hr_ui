<script setup>
// Generic, metadata-driven create/edit form for ANY hrms doctype — including
// child tables (add/remove rows). Reads/writes via the permission-aware engine.
import { ref, reactive, computed, watch } from "vue"
import { Button, FormControl, Select, TextInput, createResource, toast } from "frappe-ui"
import Drawer from "./Drawer.vue"
import Icon from "./Icon.vue"
import LinkControl from "./LinkControl.vue"
import DateField from "./DateField.vue"

const props = defineProps({
  open: Boolean,
  doctype: { type: String, required: true },
  name: { type: String, default: null }, // null = create
})
const emit = defineEmits(["close", "saved"])

const meta = ref(null)
const form = reactive({})
const linkOptions = reactive({})        // scalar link field -> options
const childMeta = reactive({})          // table field -> [child column defs]
const childLinkOptions = reactive({})   // "table.childfield" -> options
const loading = ref(false)

const metaRes = createResource({ url: "frappe_hr_ui.doctype_api.get_meta" })
const docRes = createResource({ url: "frappe_hr_ui.doctype_api.get_doc" })
const save = createResource({ url: "frappe_hr_ui.doctype_api.save_doc" })

const SKIP = ["Table MultiSelect", "Attach", "Attach Image", "Signature", "Geolocation", "Code", "HTML Editor", "HTML"]
function inputType(ft) {
  if (["Int", "Float", "Currency", "Percent"].includes(ft)) return "number"
  if (ft === "Date") return "date"
  if (ft === "Datetime") return "datetime-local"
  if (ft === "Time") return "time"
  if (ft === "Check") return "checkbox"
  if (["Select", "Link"].includes(ft)) return "select"
  if (["Text", "Small Text", "Long Text", "Text Editor", "Markdown Editor", "JSON"].includes(ft)) return "textarea"
  return "text"
}
const visible = computed(() =>
  (meta.value?.fields || []).filter((f) => !f.hidden && !SKIP.includes(f.fieldtype)
    && f.fieldname !== "naming_series" && f.fieldname !== "amended_from")
)
const scalarFields = computed(() => visible.value.filter((f) => f.fieldtype !== "Table"))
const tableFields = computed(() => visible.value.filter((f) => f.fieldtype === "Table"))
const title = computed(() => (props.name ? `Edit ${props.doctype}` : `New ${props.doctype}`))
const canSave = computed(() => meta.value?.perms?.[props.name ? "write" : "create"])

function optionsFor(f) {
  if (f.fieldtype === "Select") return (f.options || "").split("\n").map((o) => o.trim())
  return undefined
}
function childSelectOptions(cf) {
  return (cf.options || "").split("\n").map((o) => ({ label: o.trim(), value: o.trim() }))
}

// Inline "+ New" for a Link field: open a nested create drawer (DocForm refers
// to itself recursively), then hand the new record's name back to the picker.
const inlineCreate = reactive({ open: false, doctype: null, cb: null })
function onRequestCreate({ doctype, onCreated }) {
  inlineCreate.doctype = doctype
  inlineCreate.cb = onCreated
  inlineCreate.open = true
}
function onInlineSaved(r) {
  const name = r?.name || (typeof r === "string" ? r : null)
  if (inlineCreate.cb && name) inlineCreate.cb(name)
}

async function load() {
  loading.value = true
  Object.keys(form).forEach((k) => delete form[k])
  Object.keys(linkOptions).forEach((k) => delete linkOptions[k])
  Object.keys(childMeta).forEach((k) => delete childMeta[k])

  try {
    await loadInner()
  } catch (e) {
    toast.error(e?.messages?.[0] || `Can't open ${props.doctype} here`)
    loading.value = false
    emit("close")
    return
  }
  loading.value = false
}

async function loadInner() {
  meta.value = await metaRes.fetch({ doctype: props.doctype })
  for (const f of meta.value.fields) {
    if (f.fieldtype === "Table") form[f.fieldname] = []
    else if (f.default != null) form[f.fieldname] = f.fieldtype === "Check" ? !!Number(f.default) : f.default
  }
  if (props.name) {
    const doc = await docRes.fetch({ doctype: props.doctype, name: props.name })
    Object.assign(form, doc)
  }

  // scalar link options
  await Promise.all(scalarFields.value.filter((f) => f.fieldtype === "Link" && f.options).map(async (f) => {
    const r = await createResource({ url: "frappe_hr_ui.doctype_api.search_link" }).fetch({ doctype: f.options })
    linkOptions[f.fieldname] = r?.options || []
  }))

  // child table columns (+ their link options)
  for (const tf of tableFields.value) {
    const cm = await createResource({ url: "frappe_hr_ui.doctype_api.get_meta" }).fetch({ doctype: tf.options })
    const cols = (cm?.fields || []).filter((c) => (c.in_list_view || c.reqd) && !c.hidden && !["Table", "Table MultiSelect", "HTML", "Section Break", "Column Break"].includes(c.fieldtype))
    childMeta[tf.fieldname] = cols.slice(0, 5)
    if (!Array.isArray(form[tf.fieldname])) form[tf.fieldname] = []
    await Promise.all(childMeta[tf.fieldname].filter((c) => c.fieldtype === "Link" && c.options).map(async (c) => {
      const r = await createResource({ url: "frappe_hr_ui.doctype_api.search_link" }).fetch({ doctype: c.options })
      childLinkOptions[`${tf.fieldname}.${c.fieldname}`] = r?.options || []
    }))
  }
}
watch(() => [props.open, props.doctype, props.name], ([open]) => { if (open) load() }, { immediate: true })

function addRow(tf) { form[tf.fieldname].push({}) }
function removeRow(tf, i) { form[tf.fieldname].splice(i, 1) }

function submitForm() {
  const missing = scalarFields.value.filter((f) => f.reqd && !f.read_only && !form[f.fieldname])
  if (missing.length) { toast.error(`Required: ${missing.map((f) => f.label).join(", ")}`); return }
  const payload = {}
  for (const f of scalarFields.value) if (!f.read_only && form[f.fieldname] !== undefined) payload[f.fieldname] = form[f.fieldname]
  for (const tf of tableFields.value) if ((form[tf.fieldname] || []).length) payload[tf.fieldname] = form[tf.fieldname]
  save.submit(
    { doctype: props.doctype, name: props.name || undefined, doc: JSON.stringify(payload) },
    {
      onSuccess: (r) => { toast.success(props.name ? "Saved" : "Created"); emit("saved", r); emit("close") },
      onError: (e) => toast.error(e?.messages?.[0] || "Couldn't save"),
    }
  )
}
</script>

<template>
  <Drawer :open="open" :title="title" :subtitle="doctype" :width="560" @close="emit('close')">
    <div v-if="loading" class="py-10 text-center text-[13px] text-ink-gray-5">Loading…</div>
    <div v-else class="flex flex-col gap-4">
      <!-- scalar fields: Link fields get an inline "+ New"; everything else is
           a frappe-ui FormControl (which renders the espresso checkbox for Check) -->
      <template v-for="f in scalarFields" :key="f.fieldname">
        <LinkControl v-if="f.fieldtype === 'Link'"
          :doctype="f.options" :label="f.label + (f.reqd ? ' *' : '')"
          :options="linkOptions[f.fieldname] || []" :disabled="f.read_only"
          v-model="form[f.fieldname]" @create="onRequestCreate" />
        <DateField v-else-if="f.fieldtype === 'Date'"
          :label="f.label + (f.reqd ? ' *' : '')" v-model="form[f.fieldname]" />
        <FormControl v-else
          :type="inputType(f.fieldtype)" :label="f.label + (f.reqd ? ' *' : '')"
          :options="optionsFor(f)" :disabled="f.read_only" v-model="form[f.fieldname]" />
      </template>

      <!-- child tables -->
      <div v-for="tf in tableFields" :key="tf.fieldname" class="rounded-md border border-outline-gray-1 p-3">
        <div class="mb-2 flex items-center justify-between">
          <span class="text-[12.5px] font-medium text-ink-gray-8">{{ tf.label }}</span>
          <Button variant="subtle" theme="gray" size="sm" label="Add row" @click="addRow(tf)"><template #prefix><Icon name="plus" :size="13" /></template></Button>
        </div>
        <div v-if="!(form[tf.fieldname] || []).length" class="py-2 text-center text-[12px] text-ink-gray-4">No rows yet.</div>
        <div v-for="(row, i) in form[tf.fieldname]" :key="i" class="mb-1.5 flex items-end gap-1.5">
          <div v-for="c in childMeta[tf.fieldname]" :key="c.fieldname" class="min-w-0 flex-1">
            <div class="mb-0.5 truncate text-[10.5px] text-ink-gray-5">{{ c.label }}</div>
            <LinkControl v-if="c.fieldtype === 'Link'" compact :doctype="c.options"
              :options="childLinkOptions[`${tf.fieldname}.${c.fieldname}`] || []"
              v-model="row[c.fieldname]" @create="onRequestCreate" />
            <Select v-else-if="c.fieldtype === 'Select'" v-model="row[c.fieldname]" :options="childSelectOptions(c)" size="md" placeholder="" />
            <DateField v-else-if="c.fieldtype === 'Date'" v-model="row[c.fieldname]" />
            <TextInput v-else :type="inputType(c.fieldtype)" v-model="row[c.fieldname]" size="md" />
          </div>
          <Button variant="ghost" size="sm" label="Remove row" class="mb-px shrink-0" @click="removeRow(tf, i)"><template #icon><Icon name="x" :size="14" /></template></Button>
        </div>
      </div>

      <p class="text-[11.5px] text-ink-gray-4">Fields and validations follow Frappe HR.</p>
    </div>
    <template #footer>
      <Button variant="ghost" label="Cancel" @click="emit('close')" />
      <Button variant="solid" theme="blue" :label="name ? 'Save' : 'Create'" :loading="save.loading" :disabled="!canSave" @click="submitForm" />
    </template>
  </Drawer>

  <!-- Nested create drawer for inline "+ New" on Link fields (recursive). -->
  <DocForm v-if="inlineCreate.doctype" :open="inlineCreate.open" :doctype="inlineCreate.doctype"
    @close="inlineCreate.open = false" @saved="onInlineSaved" />
</template>
