<script setup>
import { watch, onUnmounted } from "vue"
import Icon from "./Icon.vue"
const props = defineProps({
  open: Boolean,
  title: String,
  subtitle: String,
  width: { type: Number, default: 460 },
})
const emit = defineEmits(["close"])

function onKey(e) {
  if (e.key === "Escape") emit("close")
}
watch(
  () => props.open,
  (open) => {
    if (open) document.addEventListener("keydown", onKey)
    else document.removeEventListener("keydown", onKey)
  }
)
onUnmounted(() => document.removeEventListener("keydown", onKey))
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[60]">
      <div class="absolute inset-0 bg-black/30" @click="emit('close')" />
      <div
        class="absolute bottom-0 right-0 top-0 flex max-w-[94vw] flex-col bg-surface-white shadow-2xl"
        :style="{ width: width + 'px' }"
      >
        <div class="flex items-start justify-between gap-3 border-b border-outline-gray-1 px-5 py-4">
          <slot name="head">
            <div>
              <div class="text-[15.5px] font-medium text-ink-gray-9">{{ title }}</div>
              <div v-if="subtitle" class="mt-0.5 text-[12.5px] text-ink-gray-5">{{ subtitle }}</div>
            </div>
          </slot>
          <button type="button" aria-label="Close" class="flex h-8 w-8 items-center justify-center rounded-md text-ink-gray-6 hover:bg-surface-gray-2" @click="emit('close')">
            <Icon name="x" :size="18" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-5"><slot /></div>
        <div v-if="$slots.footer" class="flex justify-end gap-2 border-t border-outline-gray-1 bg-surface-gray-1 px-5 py-3.5">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
