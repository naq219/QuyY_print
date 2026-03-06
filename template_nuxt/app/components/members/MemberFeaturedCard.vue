<script setup>
const props = defineProps({
  members: { type: Array, default: () => [] },
  title: { type: String, default: '✨ Hôm nay hãy hỏi thăm...' },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['care', 'refresh'])

const memberLabel = (m) => {
  if (m.phap_danh) return `${m.ho_ten} - ${m.phap_danh}`
  return m.ho_ten
}
</script>

<template>
  <!-- Loading skeleton -->
  <div v-if="loading" class="h-6 rounded-lg bg-surface-100 dark:bg-surface-800 animate-pulse w-3/4" />

  <!-- Compact inline display -->
  <div
    v-else-if="members.length"
    class="flex items-center gap-1.5 flex-wrap px-1 py-1.5 rounded-lg bg-gradient-to-r from-rose-50/60 to-amber-50/60 dark:from-rose-950/20 dark:to-amber-950/20 border border-rose-200/50 dark:border-rose-800/30"
  >
    <span class="text-xs text-muted-color font-medium">✨ Hôm nay hãy hỏi thăm</span>
    <template v-for="(member, idx) in members" :key="member.id">
      <span v-if="idx > 0" class="text-xs text-muted-color">,</span>
      <button
        class="text-xs font-semibold text-primary hover:underline cursor-pointer transition-colors"
        :title="`Ghi chú chăm sóc – ${member.ho_ten}`"
        @click="$emit('care', member)"
      >{{ memberLabel(member) }}</button>
    </template>
    <button
      class="text-muted-color hover:text-surface-700 dark:hover:text-surface-300 transition-colors p-0.5 ml-auto"
      title="Đổi người khác"
      @click="$emit('refresh')"
    >
      <i class="pi pi-refresh text-[0.65rem]"></i>
    </button>
  </div>
</template>

