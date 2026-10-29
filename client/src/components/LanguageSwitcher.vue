<template>
  <div class="language-switcher">
    <button
      class="language-button"
      :title="localeName"
      aria-haspopup="menu"
      :aria-expanded="isDropdownOpen"
      @click="toggleDropdown"
      @blur="handleBlur"
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        class="globe-icon"
        aria-hidden="true"
      >
        <circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.5"/>
        <path d="M3 10H17" stroke="currentColor" stroke-width="1.5"/>
        <path d="M10 3C10 3 7.5 5.5 7.5 10C7.5 14.5 10 17 10 17" stroke="currentColor" stroke-width="1.5"/>
        <path d="M10 3C10 3 12.5 5.5 12.5 10C12.5 14.5 10 17 10 17" stroke="currentColor" stroke-width="1.5"/>
      </svg>
      <span class="language-label">{{ localeName }}</span>
      <svg
        class="chevron"
        :class="{ 'chevron-open': isDropdownOpen }"
        aria-hidden="true"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
      >
        <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>

    <div v-if="isDropdownOpen" class="dropdown-menu">
      <button
        v-for="locale in availableLocales"
        :key="locale"
        class="dropdown-item"
        :class="{ active: currentLocale === locale }"
        @mousedown.prevent="selectLanguage(locale)"
      >
        <span class="language-name">{{ getLanguageName(locale) }}</span>
        <svg
          v-if="currentLocale === locale"
          width="18"
          height="18"
          viewBox="0 0 18 18"
          fill="none"
          class="check-icon"
        >
          <path d="M4 9L7.5 12.5L14 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../composables/useI18n'

const { currentLocale, setLocale, availableLocales, localeName } = useI18n()

const isDropdownOpen = ref(false)

const languageNames = {
  en: 'English',
  ja: '日本語'
}

const getLanguageName = (locale) => {
  return languageNames[locale] || locale
}

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const handleBlur = () => {
  // Delay to allow mousedown events on dropdown items to fire first
  setTimeout(() => {
    isDropdownOpen.value = false
  }, 200)
}

const selectLanguage = (locale) => {
  setLocale(locale)
  isDropdownOpen.value = false
}
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.language-button {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  height: 40px;
  padding: 0 var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
  font-family: inherit;
  font-size: var(--text-sm);
  color: var(--sidebar-text);
  text-align: left;
}

.language-button:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-active);
}

.language-button:focus-visible {
  outline: 2px solid var(--sidebar-accent);
  outline-offset: 2px;
}

.globe-icon {
  flex-shrink: 0;
}

.language-label {
  flex: 1;
  font-weight: 500;
  white-space: nowrap;
}

.chevron {
  flex-shrink: 0;
  transform: rotate(180deg);
  transition: transform var(--transition);
}

.chevron-open {
  transform: rotate(0deg);
}

/* Opens upward from the sidebar footer */
.dropdown-menu {
  position: absolute;
  bottom: calc(100% + var(--space-2));
  left: 0;
  min-width: 160px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  overflow: hidden;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition);
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.dropdown-item:hover {
  background: var(--color-surface-muted);
}

.dropdown-item.active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.language-name {
  flex: 1;
}

.check-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}
</style>

<style>
/* Collapsed rail (desktop): icon only, menu opens to the right */
@media (min-width: 901px) {
  .sidebar-collapsed .language-switcher .language-label,
  .sidebar-collapsed .language-switcher .chevron {
    display: none;
  }

  .sidebar-collapsed .language-switcher .language-button {
    justify-content: center;
    padding: 0;
  }

  .sidebar-collapsed .language-switcher .dropdown-menu {
    bottom: 0;
    left: calc(100% + var(--space-3));
  }
}

/* Small screens, rail (not expanded): icon only, menu opens to the right */
@media (max-width: 900px) {
  .app:not(.menu-open) .language-switcher .language-label,
  .app:not(.menu-open) .language-switcher .chevron {
    display: none;
  }

  .app:not(.menu-open) .language-switcher .language-button {
    justify-content: center;
    padding: 0;
  }

  .app:not(.menu-open) .language-switcher .dropdown-menu {
    bottom: 0;
    left: calc(100% + var(--space-3));
  }
}
</style>
