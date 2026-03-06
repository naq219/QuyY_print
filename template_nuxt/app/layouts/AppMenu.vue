<script setup>
import AppMenuItem from './AppMenuItem.vue';

const { user, logout, fetchMyOrgs, switchOrg, orgName } = useAuth()
const { toggleDarkMode, isDarkTheme } = useLayout()

const isAdmin = computed(() => user.value?.role === 'admin')
const isAdminOrManager = computed(() => user.value?.role === 'admin' || user.value?.role === 'manager')

// Org switcher
const myOrgs = ref([])
const showOrgList = ref(false)
const switching = ref(false)

onMounted(async () => {
  myOrgs.value = await fetchMyOrgs()
})

const hasMultipleOrgs = computed(() => myOrgs.value.length > 1)

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

const model = computed(() => {
  const items = [
    {
      label: 'Tổng quan',
      items: [
        { label: 'Dashboard', icon: 'pi pi-fw pi-home', to: '/' }
      ]
    },
    {
      label: 'Thành viên',
      items: [
        { label: 'Danh sách thành viên', icon: 'pi pi-fw pi-users', to: '/members' },
        { label: 'Thêm thành viên', icon: 'pi pi-fw pi-user-plus', to: '/members/create' }
      ]
    },
    {
      label: 'Sự kiện',
      items: [
        { label: 'Danh sách sự kiện', icon: 'pi pi-fw pi-calendar', to: '/events' },
        { label: 'Nhắc nhở Follow-up', icon: 'pi pi-fw pi-bell', to: '/follow-ups' }
      ]
    }
  ]

  // Hệ thống: Nhóm chỉ admin/manager quản lý
  if (isAdminOrManager.value) {
    const systemItems = [
      { label: 'Danh sách nhóm', icon: 'pi pi-fw pi-sitemap', to: '/groups' },
      { label: 'Phân bổ nhóm', icon: 'pi pi-fw pi-arrows-h', to: '/groups/assign' },
      { label: 'Danh bạ (xoá lô)', icon: 'pi pi-fw pi-address-book', to: '/contacts' }
    ]
    if (isAdmin.value) {
      systemItems.push({ label: 'Tài khoản', icon: 'pi pi-fw pi-lock', to: '/users' })
    }
    items.push({ label: 'Hệ thống', items: systemItems })
  }

  return items
})
</script>

<template>
  <div class="layout-menu-container">
    <!-- User block ở đầu sidebar -->
    <div class="layout-menu-user">
      <div class="menu-user-info">
        <div class="menu-user-avatar">
          <i class="pi pi-user"></i>
        </div>
        <div class="menu-user-details" v-if="user">
          <span class="menu-user-name">{{ user.ho_ten }}</span>
          <span class="menu-user-role">{{ user.role }}</span>
        </div>
      </div>
      <div class="menu-user-actions">
        <button
          class="menu-action-btn"
          :title="isDarkTheme ? 'Chuyển sáng' : 'Chuyển tối'"
          @click="toggleDarkMode"
        >
          <i :class="['pi', isDarkTheme ? 'pi-sun' : 'pi-moon']"></i>
        </button>
        <button
          class="menu-action-btn menu-action-logout"
          title="Đăng xuất"
          @click="logout"
        >
          <i class="pi pi-sign-out"></i>
        </button>
      </div>
    </div>

    <!-- Org Switcher -->
    <div class="menu-org-container" v-if="orgName">
      <button
        class="menu-org-current flex items-center justify-between w-full p-2 mb-1 rounded-lg transition-colors"
        :class="hasMultipleOrgs ? 'hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer' : 'cursor-default'"
        @click="hasMultipleOrgs && (showOrgList = !showOrgList)"
      >
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-400 font-bold shrink-0">
            {{ orgName.charAt(0) }}
          </div>
          <div class="flex flex-col text-left min-w-0">
            <span class="text-sm font-bold text-surface-900 dark:text-surface-0 truncate leading-tight">{{ orgName }}</span>
            <span class="text-xs text-muted-color leading-tight">Đạo tràng làm việc</span>
          </div>
        </div>
        <i v-if="hasMultipleOrgs" class="pi pi-chevron-down text-xs text-muted-color transition-transform shrink-0" :class="{ 'rotate-180': showOrgList }"></i>
      </button>

      <!-- Dropdown list DTT -->
      <Transition name="slide-org">
        <div v-if="showOrgList && hasMultipleOrgs" class="menu-org-list px-2 py-1 mb-2 bg-surface-50 dark:bg-surface-900 rounded-lg mx-2 border border-surface-200 dark:border-surface-700">
          <button
            v-for="org in myOrgs"
            :key="org.org_id"
            class="flex items-center gap-2 w-full p-1.5 rounded-md transition-colors text-left"
            :class="org.is_current ? 'bg-primary-50 dark:bg-primary-900/40 cursor-default' : 'hover:bg-surface-200 dark:hover:bg-surface-800 cursor-pointer'"
            @click="!org.is_current && handleSwitchOrg(org.org_id)"
          >
            <div class="w-7 h-7 rounded flex items-center justify-center font-bold text-xs shrink-0"
                 :class="org.is_current ? 'bg-primary-100 dark:bg-primary-700 text-primary-700 dark:text-primary-100' : 'bg-surface-200 dark:bg-surface-800 text-surface-600 dark:text-surface-300'">
              {{ org.ten_to_chuc.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-semibold truncate leading-tight" :class="org.is_current ? 'text-primary-700 dark:text-primary-300' : 'text-surface-700 dark:text-surface-100'">
                {{ org.ten_to_chuc }}
              </div>
              <div class="text-[0.65rem] text-muted-color capitalize leading-tight mt-[1px]">
                {{ org.role === 'admin' ? '👑 Admin' : (org.role === 'manager' ? '📊 Quản lý' : '👤 Trưởng nhóm') }}
              </div>
            </div>
            <i v-if="org.is_current" class="pi pi-check text-xs text-primary-600 dark:text-primary-400 shrink-0"></i>
            <i v-else-if="switching" class="pi pi-spin pi-spinner text-xs shrink-0"></i>
          </button>
        </div>
      </Transition>
    </div>

    <ul class="layout-menu">
      <template v-for="(item, i) in model" :key="item">
        <AppMenuItem v-if="!item.separator" :item="item" :index="i" />
        <li v-if="item.separator" class="menu-separator"></li>
      </template>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
.layout-menu-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.layout-menu {
  flex: 1;
  overflow-y: auto;
}

// Org switcher block
.menu-org-block {
  margin: 0.75rem 1rem 0.5rem;
  border-radius: 8px;
  background: var(--primary-50);
  border: 1px solid var(--primary-100);
  overflow: hidden;

  .app-dark & {
    background: var(--primary-900);
    border-color: var(--primary-800);
  }
}

.menu-org-current {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 0.75rem;
  border: none;
  background: transparent;
  color: var(--primary-color);
  font-weight: 700;
  font-size: 0.9rem;
  text-align: left;

  .pi-building {
    font-size: 0.9rem;
    flex-shrink: 0;
  }
}

.menu-org-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-org-chevron {
  font-size: 0.6rem;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.rotate-180 {
  transform: rotate(180deg);
}

.menu-org-list {
  border-top: 1px solid var(--primary-200);
  padding: 0.25rem 0.5rem 0.5rem;

  .app-dark & {
    border-color: var(--primary-800);
  }
}

.menu-org-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: var(--primary-100);
    .app-dark & {
      background: var(--primary-900);
    }
  }

  &--active {
    background: var(--primary-100);
    cursor: default;
    .app-dark & {
      background: var(--primary-900);
    }
  }
}

// Transition
.slide-org-enter-active,
.slide-org-leave-active {
  transition: all 0.2s ease;
  max-height: 200px;
  overflow: hidden;
}
.slide-org-enter-from,
.slide-org-leave-to {
  max-height: 0;
  opacity: 0;
}

.layout-menu-user {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  margin: 0.5rem 0.5rem 0;
  border-radius: 8px;
  background: var(--surface-100);
  border-bottom: 1px solid var(--surface-border);

  .app-dark & {
    background: var(--surface-800);
  }
}

.menu-user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
  flex: 1;
}

.menu-user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.85rem;
}

.menu-user-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.menu-user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-user-role {
  font-size: 0.7rem;
  color: var(--text-color-secondary);
  text-transform: capitalize;
}

.menu-user-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.menu-action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-color-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
  font-size: 0.9rem;

  &:hover {
    background: var(--surface-200);
    color: var(--text-color);

    .app-dark & {
      background: var(--surface-700);
    }
  }
}

.menu-action-logout:hover {
  color: var(--red-500) !important;
}
</style>
