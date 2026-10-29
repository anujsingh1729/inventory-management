<template>
  <div
    class="app"
    :class="{ 'sidebar-collapsed': sidebarCollapsed, 'menu-open': mobileMenuOpen }"
  >
    <aside id="app-sidebar" class="sidebar" :aria-label="t('nav.mainNavigation')">
      <div class="sidebar-brand">
        <div class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 8l-9-5-9 5 9 5 9-5z" />
            <path d="M3 8v8l9 5 9-5V8" />
            <path d="M12 13v8" />
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">{{ t('nav.companyName') }}</span>
          <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: $route.path === item.to }"
          :aria-current="$route.path === item.to ? 'page' : undefined"
          :title="railMode ? t(item.labelKey) : undefined"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path v-for="d in item.paths" :key="d" :d="d" />
          </svg>
          <span class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <button
          type="button"
          class="footer-btn"
          :title="themeLabel"
          :aria-label="themeLabel"
          @click="toggleTheme"
        >
          <svg v-if="theme === 'dark'" class="footer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
          </svg>
          <svg v-else class="footer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
          </svg>
          <span class="footer-label">{{ themeLabel }}</span>
        </button>
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
        <button
          type="button"
          class="footer-btn collapse-btn"
          :title="collapseLabel"
          :aria-label="collapseLabel"
          :aria-expanded="sidebarExpanded"
          aria-controls="app-sidebar"
          @click="onToggleSidebar"
        >
          <svg class="footer-icon collapse-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5" />
          </svg>
          <span class="footer-label">{{ collapseLabel }}</span>
        </button>
      </div>
    </aside>

    <div v-if="mobileMenuOpen" class="sidebar-backdrop" @click="closeMobileMenu"></div>

    <div class="app-body">
      <header class="topbar">
        <FilterBar />
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { useTheme } from './composables/useTheme'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const {
      theme,
      sidebarCollapsed,
      mobileMenuOpen,
      toggleTheme,
      toggleSidebar,
      closeMobileMenu
    } = useTheme()

    // <=900px: sidebar is always an icon rail; mobileMenuOpen expands it as an
    // overlay (never persisted). >900px: sidebarCollapsed (persisted) rules.
    const SMALL_QUERY = '(max-width: 900px)'
    const mql = typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(SMALL_QUERY) : null
    const isSmall = ref(mql ? mql.matches : false)
    const onMqlChange = (e) => {
      isSmall.value = e.matches
      closeMobileMenu()
    }

    const sidebarExpanded = computed(() =>
      isSmall.value ? mobileMenuOpen.value : !sidebarCollapsed.value
    )
    const railMode = computed(() => !sidebarExpanded.value)
    const onToggleSidebar = () => {
      if (isSmall.value) {
        mobileMenuOpen.value = !mobileMenuOpen.value
      } else {
        toggleSidebar()
      }
    }

    const navItems = [
      { to: '/', labelKey: 'nav.overview', paths: ['M3 3h7v9H3z', 'M14 3h7v5h-7z', 'M14 12h7v9h-7z', 'M3 16h7v5H3z'] },
      { to: '/inventory', labelKey: 'nav.inventory', paths: ['M21 8l-9-5-9 5 9 5 9-5z', 'M3 8v8l9 5 9-5V8', 'M12 13v8'] },
      { to: '/orders', labelKey: 'nav.orders', paths: ['M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2', 'M9 3h6v4H9z', 'M9 12h6M9 16h4'] },
      { to: '/restocking', labelKey: 'nav.restocking', paths: ['M21 12a9 9 0 11-3-6.7', 'M21 4v5h-5', 'M12 8v8M8 12h8'] },
      { to: '/spending', labelKey: 'nav.finance', paths: ['M12 2v20', 'M17 6.5C17 4.6 14.8 3.5 12 3.5S7 4.6 7 6.5 9.2 9.5 12 10.5s5 1.9 5 4-2.2 3-5 3-5-1.1-5-3'] },
      { to: '/demand', labelKey: 'nav.demandForecast', paths: ['M3 3v18h18', 'M7 15l4-4 3 3 5-6'] },
      { to: '/reports', labelKey: 'nav.reports', paths: ['M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z', 'M14 3v5h5', 'M9 13h6M9 17h6'] }
    ]

    const themeLabel = computed(() =>
      theme.value === 'dark' ? t('nav.switchToLight') : t('nav.switchToDark')
    )
    const collapseLabel = computed(() =>
      sidebarExpanded.value ? t('nav.collapseSidebar') : t('nav.expandSidebar')
    )

    watch(() => route.path, closeMobileMenu)

    const onKeydown = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen.value) closeMobileMenu()
    }
    onMounted(() => {
      window.addEventListener('keydown', onKeydown)
      if (mql) mql.addEventListener('change', onMqlChange)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKeydown)
      if (mql) mql.removeEventListener('change', onMqlChange)
    })
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      navItems,
      theme,
      themeLabel,
      collapseLabel,
      sidebarCollapsed,
      mobileMenuOpen,
      sidebarExpanded,
      railMode,
      toggleTheme,
      onToggleSidebar,
      closeMobileMenu,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
:root {
  /* Surfaces */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;

  /* Text */
  --color-text: #0f172a;
  --color-text-secondary: #334155;
  --color-text-muted: #64748b;
  --color-text-inverse: #ffffff;

  /* Accent and status */
  --color-accent: #2563eb;
  --color-accent-strong: #1e40af;
  --color-accent-soft: #eff6ff;
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-danger: #dc2626;
  --color-danger-soft: #fef2f2;
  --color-focus-ring: rgba(37, 99, 235, 0.2);

  /* Status badge pairs (background / foreground) */
  --status-success-bg: #d1fae5;
  --status-success-fg: #065f46;
  --status-warning-bg: #fef3c7;
  --status-warning-fg: #92400e;
  --status-danger-bg: #fee2e2;
  --status-danger-fg: #991b1b;
  --status-info-bg: #dbeafe;
  --status-info-fg: #1e40af;
  --status-neutral-bg: #e0e7ff;
  --status-neutral-fg: #3730a3;

  /* Sidebar */
  --sidebar-bg: #0f172a;
  --sidebar-text: #cbd5e1;
  --sidebar-text-active: #ffffff;
  --sidebar-hover: rgba(255, 255, 255, 0.06);
  --sidebar-active: rgba(37, 99, 235, 0.22);
  --sidebar-border: rgba(255, 255, 255, 0.08);
  --sidebar-accent: #60a5fa;
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 64px;

  /* Spacing scale: multiples of 4px */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;

  /* Shape and depth */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 10px 25px rgba(15, 23, 42, 0.14);

  /* Type */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.9375rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;
  --text-3xl: 2.25rem;

  /* Layers */
  --z-sticky: 10;
  --z-topbar: 90;
  --z-sidebar: 100;
  --z-backdrop: 150;
  --z-drawer: 160;
  --z-dropdown: 200;
  --z-modal: 300;

  --transition: 160ms ease;

  color-scheme: light;
}

[data-theme="dark"] {
  --color-bg: #0b1120;
  --color-surface: #111a2e;
  --color-surface-muted: #172238;
  --color-border: #243049;
  --color-border-strong: #33425f;
  --color-text: #e2e8f0;
  --color-text-secondary: #cbd5e1;
  --color-text-muted: #94a3b8;
  --color-accent: #60a5fa;
  --color-accent-strong: #93c5fd;
  --color-accent-soft: rgba(96, 165, 250, 0.14);
  --color-success: #4ade80;
  --color-warning: #facc15;
  --color-danger: #f87171;
  --color-danger-soft: rgba(248, 113, 113, 0.12);
  --color-focus-ring: rgba(96, 165, 250, 0.3);

  --status-success-bg: rgba(34, 197, 94, 0.16);
  --status-success-fg: #86efac;
  --status-warning-bg: rgba(234, 179, 8, 0.16);
  --status-warning-fg: #fde047;
  --status-danger-bg: rgba(239, 68, 68, 0.16);
  --status-danger-fg: #fca5a5;
  --status-info-bg: rgba(59, 130, 246, 0.18);
  --status-info-fg: #93c5fd;
  --status-neutral-bg: rgba(129, 140, 248, 0.18);
  --status-neutral-fg: #c7d2fe;

  --sidebar-bg: #0a0f1c;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.55);

  color-scheme: dark;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ---------- Shell layout ---------- */
.app {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  transition: grid-template-columns var(--transition);
}

.app.sidebar-collapsed {
  --sidebar-width: var(--sidebar-width-collapsed);
}

.app-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  z-index: var(--z-sidebar);
  min-width: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--space-4);
  border-bottom: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.brand-mark {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-text-inverse);
}

[data-theme="dark"] .brand-mark {
  background: var(--sidebar-active);
  color: var(--sidebar-accent);
}

.brand-mark svg {
  width: 20px;
  height: 20px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--sidebar-text-active);
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--sidebar-text);
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 40px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  white-space: nowrap;
  transition: background var(--transition), color var(--transition);
}

.nav-link:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-active);
}

.nav-link.active {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: calc(-1 * var(--space-3));
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sidebar-accent);
}

.nav-link:focus-visible,
.footer-btn:focus-visible {
  outline: 2px solid var(--sidebar-accent);
  outline-offset: 2px;
}

.nav-icon,
.footer-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  height: 40px;
  padding: 0 var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}

.footer-btn:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-active);
}

.collapse-icon {
  transition: transform var(--transition);
}

.sidebar-collapsed .collapse-icon {
  transform: rotate(180deg);
}

.sidebar-backdrop {
  display: none;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: var(--z-topbar);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: var(--topbar-height);
  padding: var(--space-2) var(--space-6);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: var(--space-5) var(--space-6);
}

/* Collapsed (desktop only): icon-only rail */
@media (min-width: 901px) {
  .sidebar-collapsed .brand-text,
  .sidebar-collapsed .nav-label,
  .sidebar-collapsed .footer-label {
    display: none;
  }

  .sidebar-collapsed .sidebar-brand {
    justify-content: center;
    padding: 0;
  }

  .sidebar-collapsed .nav-link,
  .sidebar-collapsed .footer-btn {
    justify-content: center;
    padding: 0;
  }
}

/* Small screens: always-visible icon rail; expanding overlays the content */
@media (max-width: 900px) {
  .app,
  .app.sidebar-collapsed {
    display: block;
    transition: none;
  }

  .app-body {
    margin-left: var(--sidebar-width-collapsed);
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: var(--sidebar-width-collapsed);
    transition: width var(--transition);
  }

  .menu-open .sidebar {
    width: 280px;
    max-width: calc(100vw - var(--space-5));
    z-index: var(--z-drawer);
    box-shadow: var(--shadow-lg);
  }

  .app:not(.menu-open) .brand-text,
  .app:not(.menu-open) .nav-label,
  .app:not(.menu-open) .footer-label {
    display: none;
  }

  .app:not(.menu-open) .sidebar-brand {
    justify-content: center;
    padding: 0;
  }

  .app:not(.menu-open) .nav-link,
  .app:not(.menu-open) .footer-btn {
    justify-content: center;
    padding: 0;
  }

  .collapse-icon {
    transform: rotate(180deg);
  }

  .menu-open .collapse-icon {
    transform: none;
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: var(--z-backdrop);
    background: rgba(15, 23, 42, 0.5);
  }

  .topbar {
    padding: var(--space-2) var(--space-4);
  }

  .main-content {
    padding: var(--space-4);
  }
}

@media (prefers-reduced-motion: reduce) {
  .app,
  .sidebar,
  .collapse-icon {
    transition: none;
  }
}

/* ---------- Shared page classes ---------- */
.page-header {
  margin-bottom: var(--space-5);
}

.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-1);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-danger);
}

.stat-card.info .stat-value {
  color: var(--color-accent);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-surface-muted);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

tbody tr {
  transition: background-color var(--transition);
}

tbody tr:hover {
  background: var(--color-surface-muted);
}

.badge {
  display: inline-block;
  padding: 4px var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success,
.badge.increasing {
  background: var(--status-success-bg);
  color: var(--status-success-fg);
}

.badge.warning,
.badge.medium {
  background: var(--status-warning-bg);
  color: var(--status-warning-fg);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--status-danger-bg);
  color: var(--status-danger-fg);
}

.badge.info,
.badge.low {
  background: var(--status-info-bg);
  color: var(--status-info-fg);
}

.badge.stable {
  background: var(--status-neutral-bg);
  color: var(--status-neutral-fg);
}

.loading {
  text-align: center;
  padding: var(--space-7);
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--color-danger-soft);
  border: 1px solid var(--status-danger-bg);
  color: var(--status-danger-fg);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}
</style>
