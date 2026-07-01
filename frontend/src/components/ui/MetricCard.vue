<script setup>
import { computed } from "vue"
import Card from "./Card.vue"
import Icon from "./Icon.vue"

const props = defineProps({
  label: String,
  value: [String, Number],
  sub: String,
  icon: String,
  tone: { type: String, default: "neutral" }, // neutral | accent | success | warning | danger
  delta: Object, // { up: Boolean, value: String }
})

const toneText = computed(
  () =>
    ({
      neutral: "text-ink-gray-7",
      accent: "text-blue-600",
      success: "text-green-600",
      warning: "text-orange-600",
      danger: "text-red-600",
    })[props.tone] || "text-ink-gray-7"
)
</script>

<template>
  <Card :pad="false" class="p-[18px]">
    <div class="flex items-start justify-between">
      <div class="text-xs font-medium text-ink-gray-5">{{ label }}</div>
      <div v-if="icon" class="opacity-85" :class="toneText"><Icon :name="icon" :size="17" /></div>
    </div>
    <div class="tnum mt-2 text-5xl font-medium tracking-tight text-ink-gray-9">{{ value }}</div>
    <div v-if="sub || delta" class="mt-1 flex items-center gap-1.5">
      <span
        v-if="delta"
        class="text-xs font-medium"
        :class="delta.up ? 'text-green-600' : 'text-red-600'"
        >{{ delta.up ? "↑" : "↓" }} {{ delta.value }}</span
      >
      <span v-if="sub" class="text-xs text-ink-gray-5">{{ sub }}</span>
    </div>
  </Card>
</template>
