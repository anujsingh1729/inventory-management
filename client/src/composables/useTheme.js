import { ref, watch } from 'vue'

const THEME_KEY = 'app-theme'
const SIDEBAR_KEY = 'app-sidebar-collapsed'

const readStorage = (key) => {
  try {
    return localStorage.getItem(key)
  } catch (e) {
    return null
  }
}

const writeStorage = (key, value) => {
  try {
    localStorage.setItem(key, value)
  } catch (e) {
    // Storage unavailable; state stays in memory only
  }
}

const getInitialTheme = () => {
  const saved = readStorage(THEME_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  try {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } catch (e) {
    return 'light'
  }
}

const theme = ref(getInitialTheme())
const sidebarCollapsed = ref(readStorage(SIDEBAR_KEY) === 'true')
const mobileMenuOpen = ref(false)

const applyTheme = (value) => {
  document.documentElement.setAttribute('data-theme', value)
}

// Apply immediately so first paint uses the right theme
applyTheme(theme.value)

watch(theme, (value) => {
  applyTheme(value)
  writeStorage(THEME_KEY, value)
})

watch(sidebarCollapsed, (value) => {
  writeStorage(SIDEBAR_KEY, String(value))
})

export function useTheme() {
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  const openMobileMenu = () => { mobileMenuOpen.value = true }
  const closeMobileMenu = () => { mobileMenuOpen.value = false }

  return {
    theme,
    sidebarCollapsed,
    mobileMenuOpen,
    toggleTheme,
    toggleSidebar,
    openMobileMenu,
    closeMobileMenu
  }
}
