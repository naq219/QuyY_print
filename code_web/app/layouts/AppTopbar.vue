<script setup>
const { toggleMenu } = useLayout();
const route = useRoute()

const PAGE_TITLES = {
  '/': 'Chỉnh Tọa Độ & In Thử',
}

const pageTitle = computed(() => {
  return PAGE_TITLES[route.path] || 'QuyY Print Web'
})
</script>

<template>
  <div class="layout-topbar">
    <div class="layout-topbar-logo-container">
      <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
        <i class="pi pi-bars"></i>
      </button>
      <span class="layout-topbar-logo" style="cursor: default; text-decoration: none; pointer-events: none;">
        <span class="font-semibold text-lg">{{ pageTitle }}</span>
      </span>
    </div>
  </div>
</template>
