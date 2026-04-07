# Dynatrace Strato Design System — HTML Reference

Single source of truth for color tokens, typography, component translation maps,
and custom components used in all Dynatrace-branded HTML presentations.

---

## 1. Color Tokens (Dark Mode Only)

All presentations use the Strato dark palette exclusively. There is no light mode.

### Core Palette

| Token | CSS Variable | Hex | Usage |
|---|---|---|---|
| **Navy** | `--dt-navy` | `#14191F` | All slide / page backgrounds |
| **Dark** | `--dt-dark` | `#1A1E26` | Secondary dark surface (app header) |
| **Card** | `--dt-card` | `#1E2330` | Container / card surface |
| **Blue** | `--dt-blue` | `#1496FF` | Primary accent, links, tags, active states |
| **Green** | `--dt-green` | `#73BE28` | Success, CTA, positive outcomes |
| **Teal** | `--dt-teal` | `#00BFB3` | Tertiary accent, infrastructure elements |
| **Purple** | `--dt-purple` | `#B4A0FF` | Fourth accent, security / policy |
| **Orange** | `--dt-orange` | `#F5841F` | Warning, attention |
| **Pink** | `--dt-pink` | `#EE79A2` | People / team elements |
| **Red** | `--dt-red` | `#EF4444` | Error, critical, blocked |

### Neutral / Text

| Token | CSS Variable | Hex | Usage |
|---|---|---|---|
| **White** | `--dt-white` | `#FFFFFF` | Headings, high-emphasis text |
| **Gray 100** | `--dt-gray-100` | `#F0F2F5` | — |
| **Gray 200** | `--dt-gray-200` | `#D1D5DB` | Sub-headings, resource items |
| **Gray 300** | `--dt-gray-300` | `#9CA3AF` | Body text, subtitles, descriptions |
| **Gray 400** | `--dt-gray-400` | `#6B7280` | Muted text, labels, counters |
| **Gray 500** | `--dt-gray-500` | `#374151` | Inactive dots, subtle borders |

### Semantic Status Colors

Map to Strato `HealthIndicator.status` and `Container.color`:

| Status | Dot/Border | Background Tint | Strato prop |
|---|---|---|---|
| Ideal | `#73BE28` (green) | `rgba(115,190,40,0.06)` | `ideal` |
| Good | `#1496FF` (blue) | `rgba(20,150,255,0.06)` | `good` |
| Neutral | `#6B7280` (gray-400) | `rgba(107,114,128,0.06)` | `neutral` |
| Warning | `#F5841F` (orange) | `rgba(245,132,31,0.06)` | `warning` |
| Critical | `#EF4444` (red) | `rgba(239,68,68,0.06)` | `critical` |

### Chart / Data-Visualisation Palette (ordered)

Use in sequence for multi-series charts:

| # | Color | Hex |
|---|---|---|
| 1 | Blue | `#1496FF` |
| 2 | Green | `#73BE28` |
| 3 | Teal | `#00BFB3` |
| 4 | Purple | `#B4A0FF` |
| 5 | Orange | `#F5841F` |
| 6 | Pink | `#EE79A2` |

---

## 2. Typography

### Font Stack

```
Primary:  'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif
Mono:     'DM Mono', monospace
```

**Google Fonts import** — always the first line inside `<style>`:

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Mono&display=swap');
```

### Type Scale

| Element | Font | Size | Weight | Color | Notes |
|---|---|---|---|---|---|
| Slide title `h1` | DM Sans | 48–52px | 700 | `linear-gradient(135deg, #FFF, #D1D5DB)` clip | Never below 48px |
| Section heading `h2` | DM Sans | 36–40px | 700 | White | Use `.accent` span for blue emphasis |
| Subtitle `h3` | DM Sans | 22px | 500 | Gray 300 | |
| Body / paragraph | DM Sans | 17–18px | 400 | Gray 300 | line-height 1.7 |
| Card title | DM Sans | 19px | 700 | White | Inside `dt-container` |
| Card description | DM Sans | 16px | 400 | Gray 300 | Inside `dt-container` |
| Label / caption | DM Sans | 13px | 500 | Gray 400 | uppercase, letter-spacing 1px |
| Chip / badge | DM Mono | 12–13px | 400 | Accent color | uppercase, letter-spacing 2px |
| Stat number | DM Sans | 42–46px | 700 | Accent color | Inside `dt-single-value` |
| Stat label | DM Sans | 13px | 400 | Gray 400 | uppercase |
| Code | DM Mono | 15px | 400 | Blue | `background: rgba(255,255,255,0.06)` |
| Slide counter | DM Mono | 13px | 400 | Gray 400 | |

---

## 3. Strato-to-HTML Translation Map

Strato is React-based. All output is pure HTML+CSS. These mappings are the authoritative
translation reference — verified against live Strato component patterns.

### Layout Components

| Strato Component | HTML Equivalent | Key CSS |
|---|---|---|
| `Page` | `<body>` + `<header>` + `<main>` | CSS Grid: `grid-template-rows: auto 1fr`, 100vh |
| `Page.Header` | `<header class="dt-app-header">` | Sticky top, flex row, 4px gradient `::before` |
| `Surface` | `<section class="dt-surface">` | Background layer, padding 16px, border-radius 8px |
| `Container` | `<div class="dt-container">` | bg `var(--dt-card)`, border `1px solid rgba(255,255,255,0.06)`, radius 12px, padding 28px |
| `Flex` | `<div class="dt-flex">` | `display: flex`, configurable via modifier classes |
| `Grid` | `<div class="dt-grid">` | `display: grid`, column utilities |
| `Divider` | `<hr class="dt-divider">` | `height: 1px; background: rgba(255,255,255,0.06)` |
| `TitleBar` | `<div class="dt-title-bar">` | flex row, space-between, optional 1px bottom border |

### Typography Components

| Strato Component | HTML Equivalent | Key CSS |
|---|---|---|
| `Heading` level 1 | `<h1>` | 48px+, 700, white→gray-200 gradient `background-clip: text` |
| `Heading` level 2 | `<h2>` | 36px+, 700, white |
| `Heading` level 3 | `<h3>` | 22px, 500, gray-300 |
| `Paragraph` | `<p class="dt-paragraph">` | 16px+, 400, gray-300, line-height 1.7 |
| `Text` | `<span>` | Inherits parent, configurable weight/color |
| `Strong` | `<strong>` | 700 weight |
| `Emphasis` | `<em>` | italic |
| `Code` | `<code>` | DM Mono, rgba bg, blue text, radius 4px |
| `List` | `<ul class="dt-list">` | Arrow prefix (`→`) in blue, 8px item spacing |
| `Blockquote` | `<blockquote class="dt-blockquote">` | Left border 3px blue, padded |

### Content Components

| Strato Component | Props / Variants | HTML Equivalent | Key CSS |
|---|---|---|---|
| `Chip` | `color`: neutral\|primary\|success\|warning\|critical; `variant`: accent\|emphasized; `size`: default\|condensed | `<span class="dt-chip">` | DM Mono 12px, pill radius 20px, colored border + text |
| `HealthIndicator` | `status`: ideal\|good\|neutral\|warning\|critical | `<span class="dt-health">` | 8px circle dot + label, semantic colors |
| `MessageContainer` | `variant`: neutral\|primary\|success\|warning\|critical | `<div class="dt-message" data-variant="...">` | Left border 3px, rgba bg tint |
| `SingleValue` | — | `<div class="dt-single-value">` | 42px+ 700 accent number + 13px gray-400 uppercase label |
| `ProgressBar` | determinate/indeterminate | `<div class="dt-progress-bar">` → `<div class="dt-progress-fill">` | 8px height, radius 4px |
| `CodeSnippet` | — | `<pre class="dt-code-snippet"><code>` | DM Mono, card bg, border, radius 12px, padding 24px |
| `Accordion` | — | `<details class="dt-accordion">` + `<summary>` | Native disclosure, `▸`/`▾` markers in blue |
| `Avatar` | — | `<div class="dt-avatar">` | Circle, colored bg, initials or image |

### Navigation & Structure

| Strato Component | HTML Equivalent | Key CSS |
|---|---|---|
| `AppHeader` | `<header class="dt-app-header">` | Flex row, sticky, 4px gradient top bar |
| `Tabs` | `<div class="dt-tabs">` + `<button class="dt-tab-btn">` | Flex row, active underline blue, toggled panels |
| `Breadcrumbs` | `<nav class="dt-breadcrumbs">` | Inline flex, `>` separator, gray-400 links |
| `Menu` | `<nav class="dt-menu">` | Dropdown, card bg, shadow, rounded |

### Data Display

| Strato Component | HTML Equivalent | Key CSS |
|---|---|---|
| `SimpleTable` / `DataTable` | `<table class="dt-table">` | Card bg, 12px uppercase headers gray-400, cell padding 12px 16px |
| `DonutChart` | `<svg class="dt-donut">` | SVG `<circle>` with `stroke-dasharray` segments |
| `CategoricalBarChart` | `<div class="dt-bar-chart">` | Horizontal CSS bars with labels |
| `MeterBarChart` | `<div class="dt-meter-bar">` | Horizontal fill bar with value label |

### Feedback & Overlays

| Strato Component | HTML Equivalent | Key CSS |
|---|---|---|
| `Tooltip` | CSS `[data-tooltip]::after` | Position absolute, card bg, small text, shadow |
| `Modal` | `<dialog class="dt-modal">` | Native `<dialog>`, backdrop blur, card bg |
| `Toast` | `<div class="dt-toast">` | Fixed bottom-right, card bg, colored left border |

---

## 4. Container Color Semantics

Strato `Container` supports `color` and `variant` props. HTML uses CSS modifier classes
and `::before` top-border strips.

### Semantic Colors (use when accent communicates meaning)

| Modifier class | Border | Usage |
|---|---|---|
| `dt-container--neutral` | Gray 400 | Default, no special meaning |
| `dt-container--primary` | Blue | Key information, primary focus |
| `dt-container--success` | Green | Positive outcomes, completed |
| `dt-container--warning` | Orange | Caution, at-risk items |
| `dt-container--critical` | Red | Errors, blocked, failures |

```html
<div class="dt-container dt-container--success">...</div>
<div class="dt-container dt-container--critical">...</div>
```

### Cycled Colors (use for peer cards with no semantic meaning)

```css
.dt-container:nth-child(1)::before { background: var(--dt-blue); }
.dt-container:nth-child(2)::before { background: var(--dt-green); }
.dt-container:nth-child(3)::before { background: var(--dt-teal); }
.dt-container:nth-child(4)::before { background: var(--dt-purple); }
.dt-container:nth-child(5)::before { background: var(--dt-orange); }
.dt-container:nth-child(6)::before { background: var(--dt-pink); }
```

---

## 5. Insight Block Component (`dt-insight`)

Mandatory on every content slide. Provides the narrative layer that transforms data
into actionable intelligence. Always place **before** tables, charts, or stat grids.

### Structure

| Part | CSS Class | Content |
|---|---|---|
| **Severity** | `.insight-severity` | Icon + level — e.g. `🟠 HIGH` or `▲ CONCENTRATION RISK` |
| **Finding** | `.insight-finding` | Bold one-line finding — the "what" |
| **Consequence** | `.insight-consequence` | Plain-language impact — the "so what" |
| **Action** | `.insight-action` | Recommended action or drill-down reference |
| **Dig Deeper** | `.dig-deeper` | _(optional)_ Link to slide, notebook, or data source |

### Variants

| Modifier class | Border | Background Tint | When to use |
|---|---|---|---|
| `dt-insight--critical` | `var(--dt-red)` | `rgba(239,68,68,0.06)` | Blocks success |
| `dt-insight--warning` | `var(--dt-orange)` | `rgba(245,132,31,0.06)` | Significant risk |
| `dt-insight--info` | `var(--dt-blue)` | `rgba(20,150,255,0.06)` | Informational, needs attention |
| `dt-insight--success` | `var(--dt-green)` | `rgba(115,190,40,0.06)` | Positive signal, on track |

### HTML Pattern

```html
<div class="dt-insight dt-insight--warning">
  <div class="insight-severity" style="color: var(--dt-orange)">▲ CONCENTRATION RISK</div>
  <div class="insight-finding">CLIN carries 40% of all DRS open items — more than ASDY + SRE combined.</div>
  <div class="insight-consequence">If CLIN teams hit capacity limits, rally delivery degrades disproportionately.</div>
  <div class="insight-action">→ CapLead rebalancing conversation needed this week.</div>
  <div class="dig-deeper">Dig deeper → <a href="#slide-2">Capability Health (Slide 2)</a></div>
</div>
```

### CSS

```css
.dt-insight {
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 10px;
  border-left: 4px solid;
  font-size: 14px;
  line-height: 1.55;
}
.dt-insight--critical { border-color: var(--dt-red); background: rgba(239,68,68,0.06); }
.dt-insight--warning  { border-color: var(--dt-orange); background: rgba(245,132,31,0.06); }
.dt-insight--info     { border-color: var(--dt-blue); background: rgba(20,150,255,0.06); }
.dt-insight--success  { border-color: var(--dt-green); background: rgba(115,190,40,0.06); }

.dt-insight .insight-severity {
  font-size: 13px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;
}
.dt-insight .insight-finding   { color: var(--dt-white); font-weight: 600; }
.dt-insight .insight-consequence { color: var(--dt-gray-300); margin-top: 2px; }
.dt-insight .insight-action    { color: var(--dt-blue); margin-top: 4px; font-size: 13px; }
.dt-insight .dig-deeper        { font-size: 12px; color: var(--dt-teal); margin-top: 4px; font-style: italic; }
.dt-insight .dig-deeper a      { color: var(--dt-teal); text-decoration: underline; }
```

### Density Rules

1. Every content slide opens with 1–2 insight blocks — before any data
2. Each insight must have a **finding** + **consequence** — severity and action are recommended
3. No table-only slides — if a slide has only tables, add an insight block
4. Dig-deeper links should reference other slides, Dynatrace notebooks, or data sources

---

## 6. Notebook Link Component (`dt-notebook-link`)

Provides drill-down from HTML slides into live DQL queries in the Dynatrace platform.

### HTML Pattern

```html
<a href="https://env.dev.apps.dynatracelabs.com/ui/document/abc123/"
   class="dt-notebook-link" target="_blank" rel="noopener">
  <span class="notebook-icon">📊</span>
  <span class="notebook-label">Open in Notebook</span>
  <span class="notebook-desc">Validate scope decomposition data</span>
</a>
```

### CSS

```css
.dt-notebook-link {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  background: rgba(20,150,255,0.08);
  border: 1px solid rgba(20,150,255,0.25);
  border-radius: 8px;
  color: var(--dt-blue); text-decoration: none; font-size: 13px;
  transition: background 0.2s, border-color 0.2s;
}
.dt-notebook-link:hover {
  background: rgba(20,150,255,0.15); border-color: var(--dt-blue);
}
.dt-notebook-link .notebook-icon  { font-size: 16px; }
.dt-notebook-link .notebook-label { font-weight: 600; color: var(--dt-white); }
.dt-notebook-link .notebook-desc  { color: var(--dt-gray-400); font-size: 12px; }
```

### Placement Rules

1. Every slide with quantitative claims should have at least one notebook link
2. Place at the bottom of the slide or inside the insight block's `dig-deeper` section
3. Group multiple links in a `dt-flex` container when a slide references multiple query sources
4. Notebook links are **supplementary** — the slide must be self-contained without clicking through

---

## 7. Mermaid Diagram Styling

When embedding Mermaid diagrams, prepend this directive to apply Strato dark-mode colors:

```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#1496FF',
  'primaryBorderColor': '#1496FF',
  'primaryTextColor': '#ffffff',
  'secondaryColor': '#1E2330',
  'tertiaryColor': '#14191F',
  'lineColor': '#9CA3AF',
  'textColor': '#9CA3AF',
  'fontSize': '14px',
  'fontFamily': 'DM Sans, -apple-system, BlinkMacSystemFont, sans-serif'
}}}%%
```

For Gantt charts, additionally set:

```
'critBorderColor': '#EF4444',
'critBkgColor': 'rgba(239,68,68,0.1)',
'activeTaskBkgColor': '#1496FF',
'activeTaskBorderColor': '#1496FF',
'doneTaskBkgColor': '#73BE28',
'doneTaskBorderColor': '#73BE28',
'taskBkgColor': '#1E2330',
'taskBorderColor': 'rgba(255,255,255,0.06)'
```
