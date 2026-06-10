<script setup>
// Edit a Frappe "Single" doctype (e.g. HR Settings, Payroll Settings) fully in-UI,
// rendered from its metadata via the generic engine. No Desk.
import { ref, reactive, computed, watch } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const props = defineProps({ doctype: { type: String, required: true }, title: String, subtitle: String })

const meta = ref(null)
const form = reactive({})
const linkOptions = reactive({})
const ready = ref(false)

const metaRes = createResource({ url: "frappe_hr_ui.doctype_api.get_meta" })
const docRes = createResource({ url: "frappe_hr_ui.doctype_api.get_doc" })
const save = createResource({ url: "frappe_hr_ui.doctype_api.save_doc" })

const SKIP = ["Table", "Table MultiSelect", "Attach", "Attach Image", "Signature", "Geolocation", "Code", "HTML Editor", "HTML"]
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
const fields = computed(() => (meta.value?.fields || []).filter((f) => !f.hidden && !SKIP.includes(f.fieldtype)))
const canWrite = computed(() => meta.value?.perms?.write)
function optionsFor(f) {
  if (f.fieldtype === "Link") return linkOptions[f.fieldname] || []
  if (f.fieldtype === "Select") return (f.options || "").split("\n").map((o) => o.trim())
  return undefined
}

async function load() {
  ready.value = false
  Object.keys(form).forEach((k) => delete form[k])
  meta.value = await metaRes.fetch({ doctype: props.doctype })
  const doc = await docRes.fetch({ doctype: props.doctype, name: props.doctype })
  Object.assign(form, doc)
  await Promise.all(
    fields.value.filter((f) => f.fieldtype === "Link" && f.options).map(async (f) => {
      const r = await createResource({ url: "frappe_hr_ui.doctype_api.search_link" }).fetch({ doctype: f.options })
      linkOptions[f.fieldname] = r?.options || []
    })
  )
  ready.value = true
}
watch(() => props.doctype, load, { immediate: true })

function submit() {
  const payload = {}
  for (const f of fields.value) {
    if (!f.read_only && form[f.fieldname] !== undefined) payload[f.fieldname] = form[f.fieldname]
  }
  save.submit(
    { doctype: props.doctype, name: props.doctype, doc: JSON.stringify(payload) },
    { onSuccess: () => toast.success("Settings saved"), onError: (e) => toast.error(e?.messages?.[0] || "Couldn't save") }
  )
}
</script>

<template>
  <div class="mx-auto max-w-[900px] px-6 py-[22px]">
    <PageHeader :title="title || doctype" :subtitle="subtitle">
      <template #actions>
        <Button variant="solid" theme="blue" label="Save" :loading="save.loading" :disabled="!canWrite" @click="submit" />
      </template>
    </PageHeader>
    <AsyncShell :resource="docRes" loading-text="Loading settings…">
      <Card>
        <div class="grid grid-cols-2 gap-x-4 gap-y-4">
          <template v-for="f in fields" :key="f.fieldname">
            <div :class="f.fieldtype === 'Check' || ['Text','Small Text','Long Text','Text Editor'].includes(f.fieldtype) ? 'col-span-2' : 'col-span-1'">
              <FormControl :type="inputType(f.fieldtype)" :label="f.label" :options="optionsFor(f)" :disabled="f.read_only" v-model="form[f.fieldname]" />
            </div>
          </template>
        </div>
      </Card>
    </AsyncShell>
  </div>
</template>
