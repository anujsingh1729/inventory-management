---
name: saas-sidebar-redesign
description: Redesign this Vue 3 inventory app's UI into a modern SaaS dashboard - a collapsible vertical sidebar on the left replacing the top nav bar, a design-token system for consistent spacing, light and dark themes, and a polished professional look. Use this skill whenever the user asks to restyle, modernize, re-theme, or re-layout the frontend, move the navigation to a sidebar or left rail, add dark mode, clean up spacing or visual consistency, or make the app look like a SaaS product, even if they never say "sidebar" or "redesign".
---

# SaaS sidebar redesign

Turn the app shell from "logo + horizontal tabs + filter strip" into a left sidebar layout with a slim top bar, driven by CSS design tokens. The goal is a coherent system, not a coat of paint: every view should pick up the new spacing, colors and type through shared tokens, so a later change to one token restyles the whole app.

Read `references/tokens.md` before writing any CSS; it holds the token set and the spacing scale to use.

## How this repo is wired (why the plan below looks the way it does)

- The whole shell lives in `client/src/App.vue`: a `.top-nav` header, `<FilterBar />`, then `<main class="main-content"><router-view/></main>`. The global (unscoped) `<style>` block in the same file defines the shared classes every view uses: `.card`, `.stat-card`, `.page-header`, `.badge`, `.table-container`, `.loading`, `.error`. Restyling those once restyles every view, which is why tokens belong there.
- Nav links are `<router-link>` entries using `t('nav.*')` (Reports is currently a hardcoded string, so give it a `nav.reports` key in both locales while you are there). Routes are in `client/src/main.js`.
- `ProfileMenu`, `LanguageSwitcher` and `FilterBar` are separate components with their own scoped styles. `ProfileMenu` and `LanguageSwitcher` open dropdowns downward and right-aligned, which will clip or overflow once they sit at the bottom-left of the screen.
- Views carry many hardcoded hex colors in their scoped styles. Dark mode only works if those become `var(--...)` references; that sweep is the bulk of the work and the step most likely to be skipped.
- Filters (`useFilters`) are shared singletons across views, so relocating `FilterBar` must not change how it is mounted or what it binds to.

## Constraints from CLAUDE.md that apply here

- Any creation or significant edit of a `.vue` file must be delegated to the **vue-expert** subagent. Brief it with the plan below and the token reference; do not hand-edit `.vue` files yourself.
- No emojis in the UI. Icons are inline SVG (no new dependency; `client/.npmrc` pins the public registry and the repo is public, so do not add packages).
- Keep slate/gray as the base palette with blue as the accent; status colors stay green/blue/yellow/red.
- New visible strings need keys in both `client/src/locales/en.js` and `ja.js`.
- Use unique keys in `v-for` (never the index).

## Workflow

1. **Survey.** Read `App.vue`, `FilterBar.vue`, `ProfileMenu.vue`, `LanguageSwitcher.vue`, and grep the views and components for hardcoded colors (`grep -rnE "#[0-9a-fA-F]{3,8}\b" client/src --include=*.vue`). Count them; this tells you how big the dark-mode sweep is.
2. **Tokens first.** Add the token set from `references/tokens.md` to the global style block (`:root` plus a `[data-theme="dark"]` override). Point `body`, `.card`, `.stat-card`, `.badge`, `.table-container` and the other shared classes at tokens. Do this before touching layout so the diff is easy to review.
3. **Shell.** In `App.vue` replace `.top-nav` with a fixed-width `<aside class="sidebar">` (brand at the top, nav links with an inline SVG icon and label, language switcher and profile menu in the footer). Add a slim `.topbar` above `<main>` holding the page-level controls, and mount `FilterBar` inside it so it keeps working as is. The layout becomes `display: grid; grid-template-columns: var(--sidebar-width) 1fr`. Keep `$route.path` active-state logic and add `aria-current="page"`.
4. **Collapse and responsive.** Collapsed state shows icons only (about 72px), persists in `localStorage` (wrapped in try/catch), and animates `--sidebar-width`. Below ~900px the sidebar becomes an off-canvas drawer opened from a hamburger in the top bar, with a backdrop and Escape to close. Give collapsed links a `title` attribute so labels stay discoverable.
5. **Dropdowns.** Rework `ProfileMenu` and `LanguageSwitcher` dropdown positioning to open upward/rightward from the sidebar footer (`bottom: 100%`, `left: 0`) and verify neither clips against the viewport edge or the sidebar's overflow.
6. **Dark mode.** Add a theme toggle (sidebar footer), store the choice in `localStorage`, default to `prefers-color-scheme`, and set `data-theme` on `<html>`. Then replace the hardcoded hex colors found in step 1 with tokens, view by view. Charts are custom SVG, so check their strokes, fills and text.
7. **Spacing pass.** Normalize padding, gaps and margins in views to the spacing scale (multiples of 4px via `--space-*`). Remove one-off values rather than adding new tokens for them unless three or more places share the value.
8. **Verify** (see below).

## Verification

Run both servers (`/start`), then use the Playwright MCP tools at `http://localhost:3000`:

- Visit every route (`/`, `/inventory`, `/orders`, `/restocking`, `/spending`, `/demand`, `/reports`) in light and dark, at 1440px and 800px wide. Take screenshots and look for clipped dropdowns, unreadable text in dark mode, content hidden behind the sidebar, and horizontal scroll.
- Collapse and expand the sidebar; reload and confirm the state persists.
- Change a filter and confirm data still updates; switch to Japanese and confirm labels fit in both expanded and collapsed states.
- Check the browser console for new errors (the existing `/tasks` 404s are not yours).
- `cd client && npm run build` must pass.

Report what changed, what you could not verify, and any views still using hardcoded colors.

## Things that go wrong

- Leaving `.main-content`'s `max-width: 1600px; margin: 0 auto` in place: with a sidebar it centers content in the remaining space and looks off. Let it fill the grid column with token padding.
- Fixing the shell but not the views: the page looks half redesigned and dark mode shows white cards. The grep in step 1 is the safeguard.
- Sticky table headers or modals using `z-index` values that now collide with the sidebar; keep a z-index scale in the tokens and use it.
