<script setup>
// Renders the generic metadata-driven list/form for a configured doctype.
// Route supplies the doctype + labels via props (see router).
import DocList from "@/components/ui/DocList.vue"
defineProps({ doctype: { type: String, required: true }, title: String, subtitle: String })
</script>

<template>
  <DocList :doctype="doctype" :title="title" :subtitle="subtitle" />
</template>
