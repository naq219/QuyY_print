<script setup>
import AppMenuItem from './AppMenuItem.vue';

const { toggleDarkMode, isDarkTheme } = useLayout()

const model = computed(() => [
  {
    label: 'In Ấn',
    items: [
      { label: 'Chỉnh Tọa Độ & In Thử', icon: 'pi pi-fw pi-arrows-alt', to: '/' }
    ]
  }
])
</script>

<template>
  <div class="layout-menu-container">
    <!-- App title -->
    <div class="layout-menu-user">
      <div class="menu-user-info">
        <div class="menu-user-avatar">
          <i class="pi pi-print"></i>
        </div>
        <div class="menu-user-details">
          <span class="menu-user-name">QuyY Print</span>
          <span class="menu-user-role">Web Edition</span>
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
      </div>
    </div>

    <ul class="layout-menu">
      <template v-for="(item, i) in model" :key="item">
        <AppMenuItem :item="item" :index="i" />
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
}

.menu-user-role {
  font-size: 0.7rem;
  color: var(--text-color-secondary);
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
</style>
