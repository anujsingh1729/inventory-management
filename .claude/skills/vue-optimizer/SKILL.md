---
name: vue-optimizer
description: Analyze Vue 3 component(s) for performance issues and code-reuse opportunities, then produce a prioritized list of actionable recommendations. Use this skill whenever the user asks to optimize, audit, or improve Vue components, reduce re-renders, extract composables, split large components, or improve reactivity. Triggers on phrases like "optimize vue", "vue performance", "analyze component", "extract composable", "component too big", "refactor vue", "vue best practices", or any request to review a .vue file for quality.
---

# Vue component optimizer

Analyze one or more Vue 3 components and produce a prioritized set of findings across two categories: **Performance** (things that cause unnecessary work at runtime) and **Code Reuse** (things that duplicate logic or structure that should be shared). End with a concrete action plan the developer can execute immediately.

## Scope

- If the user names specific files, analyze those.
- If the user says "this component" or "all components", glob `client/src/**/*.vue` and scan every file.
- Always check the composables in `client/src/composables/` for patterns the components could use but don't.

## Step 1 — Inventory

Run these greps to gather raw signal before reading any file:

```bash
# Reactivity anti-patterns
grep -rn "\.value\s*=\s*" client/src --include="*.vue"          # direct .value mutation in template
grep -rn "watch(" client/src --include="*.vue"                   # all watchers (review for computed candidates)
grep -rn "deep:\s*true" client/src --include="*.vue"            # deep watchers (expensive)
grep -rn ":key=\"index\"" client/src --include="*.vue"          # index as v-for key
grep -rn "v-for" client/src --include="*.vue" | grep -v ":key"  # v-for missing key entirely

# Template complexity
grep -rn "v-if.*v-for\|v-for.*v-if" client/src --include="*.vue"  # v-if + v-for on same element
grep -rn "methods:" client/src --include="*.vue"                    # Options API methods (may belong in computed)
grep -rn "\$emit(" client/src --include="*.vue"                     # emits (count per file = coupling signal)

# Code duplication
grep -rn "const.*=.*ref(\|const.*=.*reactive(" client/src --include="*.vue"   # repeated state shapes
grep -rn "onMounted\|onUnmounted" client/src --include="*.vue"                 # lifecycle hooks (composable candidates)
grep -rn "localStorage\." client/src --include="*.vue"             # storage access outside composables
grep -rn "fetch(\|axios\." client/src --include="*.vue"            # direct API calls (should go through api.js)
```

Read every file that has hits. Also read any file over 200 lines (a size signal for splitting):

```bash
wc -l client/src/views/*.vue client/src/components/*.vue | sort -rn | head -20
```

## Step 2 — Classify findings

For each finding assign a **priority**:

| Priority | Meaning                                                                          |
| -------- | -------------------------------------------------------------------------------- |
| P1       | Causes visible jank, unnecessary network requests, or incorrect behavior         |
| P2       | Causes silent waste (extra renders, oversized watchers) with no user-visible bug |
| P3       | Code smell: duplication, missing abstraction, harder to maintain but not slow    |

### Performance checklist

Check each component you read against these items. Only report items that actually apply.

**Reactivity**

- [ ] `watch()` used where a `computed()` would suffice (computed is lazy + cached; a watcher re-runs on every dependency change)
- [ ] `watch()` with `deep: true` on a large object or array — suggest `watchEffect` on specific fields instead
- [ ] `ref()` or `reactive()` wrapping data that never changes (config, static lookup tables) — suggest plain `const` or `Object.freeze`
- [ ] Missing `shallowRef` / `shallowReactive` for large objects whose inner properties the template doesn't observe individually
- [ ] `computed()` with a side effect (network call, mutation) — computed must be pure

**Template**

- [ ] `v-if` and `v-for` on the same element — `v-if` cannot access the loop variable; wrap in a `<template v-for>` with the `v-if` inside
- [ ] `:key="index"` in a `v-for` over a list that can be reordered or filtered — use a stable id (SKU, order number, etc.)
- [ ] Missing `:key` in `v-for` entirely
- [ ] Method called inside a template expression (`{{ formatDate(x) }}`) where the result is pure and the input is reactive — suggest a `computed`
- [ ] Heavy child component rendered unconditionally when it is only visible sometimes — suggest `v-if` + `defineAsyncComponent`
- [ ] `v-show` used for a component with an expensive `setup()` that only needs to render once — `v-show` keeps it mounted; `v-if` tears it down

**Event handling**

- [ ] Inline arrow function in `@click="() => fn(arg)"` inside `v-for` — creates a new function reference per render; extract to a method that receives the argument
- [ ] Missing `.stop` / `.prevent` modifiers where the handler calls `event.stopPropagation()` / `event.preventDefault()` manually

### Code-reuse checklist

**Composable extraction**

- [ ] `onMounted` + `onUnmounted` pair for the same concern (scroll, resize, WebSocket, timer) repeated in two or more components — extract to a `useX` composable in `client/src/composables/`
- [ ] `localStorage` read/write not going through a composable — the project already has `useTheme`; other persistent state should follow the same pattern
- [ ] Identical or near-identical reactive state shape (e.g. `{ loading, error, data }`) declared in multiple components — extract to a `useAsyncState` or domain-specific composable
- [ ] Direct `fetch` / `api.js` call duplicated across components for the same endpoint — the call belongs in a composable that the components import

**Component splitting**

- [ ] Component over ~250 lines: identify logical sections (header, table, modal trigger) as split candidates
- [ ] Template contains a repeated block (same structure rendered 2+ times with different data) — extract as a child component
- [ ] Prop drilling deeper than two levels (parent → child → grandchild) — suggest `provide` / `inject` or a shared composable

**Locale**

- [ ] Hardcoded English string in the template — must be moved to `client/src/locales/en.js` and `ja.js`

## Step 3 — Report

Present findings as a prioritized table, then a narrative action plan.

```
## Vue Component Analysis

### Findings

| Priority | File | Line | Category | Finding |
|----------|------|------|----------|---------|
| P1 | ... | ... | Performance | `watch(orders, ..., { deep: true })` re-runs on every keystroke in the search box. Replace with a computed that filters `allOrders`. |
| P2 | ... | ... | Reactivity | `STATIC_CATEGORIES` wrapped in `ref()` — it never changes. Use a plain `const`. |
| P3 | ... | ... | Code Reuse | `onMounted`/`onUnmounted` scroll listener duplicated in Dashboard.vue and Orders.vue. Extract to `useScrollLock` composable. |
...

### Action plan

**Fix now (P1)**
1. ...

**Fix soon (P2)**
1. ...

**Tidy up (P3)**
1. ...

### Composables to create
- `useX` — what it encapsulates, which files would import it
...

### Components to split
- `Foo.vue` (320 lines) → `FooHeader.vue` + `FooTable.vue` + keep `Foo.vue` as the shell
...
```

If there are no findings in a category, say so — don't invent problems.

## Step 4 — Apply (only if the user asks)

If the user asks you to fix the findings:

- Delegate every `.vue` file change to the **vue-expert** subagent (CLAUDE.md rule: any significant `.vue` edit must go through vue-expert).
- You may directly create or edit files in `client/src/composables/` and `client/src/locales/`.
- After changes, run `cd client && npm run build` to confirm no type or import errors.
- Run the backend tests if any `.vue` changes touch data-fetching logic: `cd tests && uv run --project ../server pytest`.

## Constraints

- Do not suggest adding new npm packages — `client/.npmrc` pins the public registry and the repo is public.
- Do not change the filter system (`useFilters` singleton) or the API client (`api.js`) without understanding the downstream impact on all views.
- Every new user-visible string needs an entry in both `en.js` and `ja.js`.
- No emojis in the UI.
