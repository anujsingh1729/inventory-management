# Design tokens

Put these in the global `<style>` block of `client/src/App.vue`. Values continue the app's existing slate palette (`#0f172a`, `#64748b`, `#e2e8f0`) with blue as the accent, so the redesign reads as an evolution rather than a different product.

```css
:root {
  /* Surfaces */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;

  /* Text */
  --color-text: #0f172a;
  --color-text-muted: #64748b;
  --color-text-inverse: #ffffff;

  /* Accent and status */
  --color-accent: #2563eb;
  --color-accent-soft: #eff6ff;
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-danger: #dc2626;

  /* Sidebar */
  --sidebar-bg: #0f172a;
  --sidebar-text: #cbd5e1;
  --sidebar-text-active: #ffffff;
  --sidebar-hover: rgba(255, 255, 255, 0.06);
  --sidebar-active: rgba(37, 99, 235, 0.22);
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;

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

  /* Type */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.9375rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;

  /* Layers */
  --z-sidebar: 100;
  --z-topbar: 90;
  --z-dropdown: 200;
  --z-modal: 300;

  --transition: 160ms ease;
}

[data-theme="dark"] {
  --color-bg: #0b1120;
  --color-surface: #111a2e;
  --color-surface-muted: #172238;
  --color-border: #243049;
  --color-text: #e2e8f0;
  --color-text-muted: #94a3b8;
  --color-accent: #60a5fa;
  --color-accent-soft: rgba(96, 165, 250, 0.14);
  --sidebar-bg: #0a0f1c;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
}
```

## Mapping hardcoded colors

When sweeping views, map by role rather than by exact hex:

| Found | Role | Token |
|---|---|---|
| `#fff`, `#ffffff` backgrounds | card or panel | `--color-surface` |
| `#f8fafc` | page background | `--color-bg` |
| `#f1f5f9` | hover, table header, muted fill | `--color-surface-muted` |
| `#e2e8f0` borders | divider | `--color-border` |
| `#0f172a`, `#1e293b` text | primary text | `--color-text` |
| `#64748b`, `#94a3b8` text | secondary text | `--color-text-muted` |
| `#2563eb`, `#3b82f6` | accent, links, active | `--color-accent` |
| `#eff6ff`, `#dbeafe` | accent tint | `--color-accent-soft` |

Status badge colors (green/blue/yellow/red) keep their hue in both themes; in dark mode lower the tint background opacity rather than inventing new hues. If a color has no clear role, leave it and list it in the report instead of guessing.

## Layout notes

- Sidebar: `position: sticky; top: 0; height: 100vh`, brand 64px tall, nav items 40px tall with `--space-3` horizontal padding and `--space-1` vertical gap, 20px icons, active item uses `--sidebar-active` with a 3px accent bar on the left edge.
- Top bar: 64px tall, `--color-surface` with a bottom `--color-border`, holds the hamburger (mobile), the filter controls and the page-level actions.
- Content: `padding: var(--space-5) var(--space-6)`; cards `padding: var(--space-5)`, `border-radius: var(--radius-md)`, `box-shadow: var(--shadow-sm)`; grids use `gap: var(--space-4)` or `--space-5`.
