<script setup>
import { ToastProvider, Dialogs } from "frappe-ui"
import AppShell from "@/components/layout/AppShell.vue"
</script>

<template>
  <AppShell />
  <ToastProvider />
  <Dialogs />
</template>
