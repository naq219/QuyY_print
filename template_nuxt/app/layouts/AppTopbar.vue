<script setup>
const { toggleMenu } = useLayout();
const { fetchMyOrgs, switchOrg, orgName } = useAuth();
const route = useRoute()

// DTT menu
const orgMenuRef = ref(null)
const myOrgs = ref([])
const switching = ref(false)

// Lấy danh sách DTT khi mounted
onMounted(async () => {
  myOrgs.value = await fetchMyOrgs()
})

const handleSwitchOrg = async (orgId) => {
  if (switching.value) return
  switching.value = true
  const result = await switchOrg(orgId)
  
  if (result.success) {
    window.location.href = '/'
  } else {
    switching.value = false
  }
}

// Chỉ hiện switcher nếu có từ 2 DTT trở lên
const hasMultipleOrgs = computed(() => myOrgs.value.length > 1)

// Map route path → tiêu đề trang
const PAGE_TITLES = {
  '/': 'Tổng quan',
  '/members': 'Chăm sóc thành viên',
  '/members/create': 'Thêm thành viên',
  '/events': 'Danh sách sự kiện',
  '/events/create': 'Tạo sự kiện',
  '/follow-ups': 'Nhắc nhở Follow-up',
  '/groups': 'Quản lý nhóm (NTT)',
  '/users': 'Tài khoản',
  '/groups/assign': 'Phân bổ nhóm',
  '/contacts': 'Danh bạ',
}

const pageTitle = computed(() => {
  const path = route.path
  if (PAGE_TITLES[path]) return PAGE_TITLES[path]
  // fallback: /members/123/edit → Thành viên
  if (path.startsWith('/members')) return 'Thành viên'
  if (path.startsWith('/events')) return 'Sự kiện'
  if (path.startsWith('/groups')) return 'Nhóm (NTT)'
  if (path.startsWith('/users')) return 'Tài khoản'
  return 'Chăm Sóc Thành Viên'
})
</script>

<template>
  <div class="layout-topbar">
    <div class="layout-topbar-logo-container">
      <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
        <i class="pi pi-bars"></i>
      </button>
      <!-- Title trang hiện tại -->
      <span class="layout-topbar-logo" style="cursor: default; text-decoration: none; pointer-events: none;">
        <span class="font-semibold text-lg">{{ pageTitle }}</span>
      </span>
    </div>

    <div class="layout-topbar-actions">
      <!-- Nút chuyển DTT (chỉ hiện khi user thuộc nhiều DTT) -->
      <div v-if="hasMultipleOrgs" class="relative">
        <button
          id="org-switcher-btn"
          type="button"
          class="layout-topbar-action flex items-center gap-1"
          :title="orgName || 'Chuyển đổi đạo tràng'"
          v-styleclass="{ selector: '#org-switcher-menu', enterFromClass: 'hidden', enterActiveClass: 'p-anchored-overlay-enter-active', leaveToClass: 'hidden', leaveActiveClass: 'p-anchored-overlay-leave-active', hideOnOutsideClick: true }"
        >
          <i class="pi pi-building"></i>
          <span class="hidden lg:inline text-sm max-w-32 truncate">{{ orgName }}</span>
          <i class="pi pi-chevron-down text-xs"></i>
        </button>

        <div id="org-switcher-menu" class="hidden absolute right-0 top-full z-50 mt-1">
          <div class="card p-2 shadow-lg min-w-52 border">
            <p class="text-xs text-muted-color px-2 py-1 font-semibold uppercase tracking-wide mb-1">
              Chuyển đạo tràng
            </p>
            <div
              v-for="org in myOrgs"
              :key="org.org_id"
              class="flex items-center gap-2 px-3 py-2 rounded cursor-pointer transition-colors"
              :class="org.is_current
                ? 'bg-primary/10 text-primary'
                : 'hover:bg-surface-100 dark:hover:bg-surface-800'"
              @click="!org.is_current && handleSwitchOrg(org.org_id)"
            >
              <i class="pi pi-building text-sm"></i>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ org.ten_to_chuc }}</p>
                <p class="text-xs text-muted-color">{{ org.role }}</p>
              </div>
              <i v-if="org.is_current" class="pi pi-check text-sm text-primary"></i>
              <i v-else-if="switching" class="pi pi-spin pi-spinner text-sm"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Chỉ hiện tên đạo tràng nếu chỉ có 1 DTT (không cần switcher) -->
      <div v-else-if="orgName" class="hidden lg:flex items-center gap-1 px-2 text-sm text-muted-color">
        <i class="pi pi-building text-xs"></i>
        <span>{{ orgName }}</span>
      </div>
    </div>
  </div>
</template>
