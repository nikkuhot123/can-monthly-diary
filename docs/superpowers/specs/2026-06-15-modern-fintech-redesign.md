# Modern FinTech Redesign: Audit Diary System

> **Date:** 2026-06-15
> **Theme:** Modern FinTech — Premium, Contemporary Banking Aesthetic
> **Replaces:** 2026-05-31-frontend-redesign.md (Navy + Gold)

---

## 1. Overview & Goals

### Why This Redesign

The existing Navy + Gold theme, while professional, has begun to feel dated and heavy. Users report that the dark navbar dominates the viewport, the gold accent feels ornate rather than modern, and the overall experience lacks the crisp, airy confidence of contemporary banking and fintech applications. This redesign is a ground-up visual refresh that establishes a lighter, more sophisticated, and distinctly premium identity.

### Success Criteria

1. **Visual Freshness:** The app must feel like a modern 2026 SaaS product, not a legacy internal tool.
2. **Improved Hierarchy:** Information architecture must be instantly scannable. Users should know where they are and what matters within 2 seconds of landing on any page.
3. **Sidebar-First Navigation:** Moving navigation to a persistent left sidebar frees vertical space for content and aligns with modern dashboard patterns (Stripe, Notion, Linear).
4. **Typography Confidence:** Switching to Outfit for headings gives the app a unique, ownable typographic voice — distinctive without being decorative.
5. **Responsive Excellence:** The experience must be polished on desktop, tablet, and mobile, with the sidebar collapsing gracefully to a hamburger menu.
6. **Performance Preservation:** The redesign is purely CSS/template-level; no JavaScript framework is introduced. The current SSR + Jinja2 architecture remains intact.

---

## 2. Design Philosophy

### Modern FinTech

The guiding aesthetic is **"confident minimalism."** Think: the clean interface of a premium neobank, the data density of a Bloomberg terminal, and the approachability of a modern SaaS dashboard. Every element should feel intentional, every pixel should earn its place.

### Core Principles

- **Restraint over Ornamentation:** No gradients, no heavy shadows, no decorative flourishes. Elevation is achieved through subtle shadows, precise borders, and generous whitespace.
- **Content is King:** The background is nearly white. UI chrome (sidebar, borders) recedes. Data and actions pop forward.
- **Precision in Detail:** Borders are 1px and consistent. Border radii are systematic (4px, 8px, 12px, 16px). Spacing follows a 4px grid.
- **Motion with Purpose:** Animations are fast (0.15s–0.3s), subtle, and always directional. They guide attention, not distract.
- **Accessibility by Default:** All color combinations must meet WCAG AA contrast standards. Focus states are visible and elegant.

---

## 3. Color System

### Primary Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary-900` | `#0f172a` | Sidebar background, primary text, headings |
| `--primary-800` | `#1e293b` | Sidebar hover, secondary dark surfaces |
| `--primary-700` | `#334155` | Muted dark elements, borders on dark bg |
| `--primary-600` | `#475569` | Disabled text on dark backgrounds |

### Accent Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent-500` | `#f59e0b` | Primary buttons, active nav item, focus rings, key highlights |
| `--accent-400` | `#fbbf24` | Button hover glow, hover states |
| `--accent-300` | `#fcd34d` | Lighter highlights, backgrounds |
| `--accent-100` | `#fef3c7` | Badge backgrounds, subtle highlights |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--success-500` | `#10b981` | Success states, "Present" status |
| `--success-100` | `#d1fae5` | Success backgrounds |
| `--warning-500` | `#f59e0b` | Warning states, "Leave" status (shares accent) |
| `--warning-100` | `#fef3c7` | Warning backgrounds |
| `--danger-500` | `#ef4444` | Danger states, errors |
| `--danger-100` | `#fee2e2` | Danger backgrounds |
| `--info-500` | `#3b82f6` | Info states, "Holiday" status |
| `--info-100` | `#dbeafe` | Info backgrounds |
| `--holiday-500` | `#6366f1` | RBI holiday indicator |
| `--holiday-100` | `#e0e7ff` | Holiday backgrounds |

### Neutral / Surface Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-main` | `#f8fafc` | Main page background |
| `--bg-surface` | `#ffffff` | Cards, modals, content panels |
| `--bg-sidebar` | `#0f172a` | Sidebar background |
| `--text-primary` | `#0f172a` | Primary body text |
| `--text-secondary` | `#64748b` | Secondary/muted text, labels |
| `--text-tertiary` | `#94a3b8` | Placeholder text, disabled |
| `--text-inverse` | `#ffffff` | Text on dark backgrounds |
| `--border-light` | `#e2e8f0` | Card borders, dividers |
| `--border-medium` | `#cbd5e1` | Input borders, table borders |
| `--border-dark` | `#334155` | Borders on dark backgrounds |

### CSS Custom Properties

```css
:root {
  --primary-900: #0f172a;
  --primary-800: #1e293b;
  --primary-700: #334155;
  --primary-600: #475569;
  --accent-500: #f59e0b;
  --accent-400: #fbbf24;
  --accent-300: #fcd34d;
  --accent-100: #fef3c7;
  --success-500: #10b981;
  --success-100: #d1fae5;
  --warning-500: #f59e0b;
  --warning-100: #fef3c7;
  --danger-500: #ef4444;
  --danger-100: #fee2e2;
  --info-500: #3b82f6;
  --info-100: #dbeafe;
  --holiday-500: #6366f1;
  --holiday-100: #e0e7ff;
  --bg-main: #f8fafc;
  --bg-surface: #ffffff;
  --bg-sidebar: #0f172a;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --text-inverse: #ffffff;
  --border-light: #e2e8f0;
  --border-medium: #cbd5e1;
  --border-dark: #334155;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -1px rgba(15, 23, 42, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -2px rgba(15, 23, 42, 0.04);
  --shadow-xl: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 10px 10px -5px rgba(15, 23, 42, 0.04);
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

---

## 4. Typography

### Font Families

- **Headings:** `Outfit` (Google Fonts) — weights 500, 600, 700. A geometric sans-serif with excellent legibility and a modern, slightly warm character. It feels engineered but friendly.
- **Body Text:** `Inter` (Google Fonts) — weights 400, 500, 600. The industry standard for UI text. Highly legible at small sizes.

### Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Type Scale

| Element | Size | Weight | Font | Line Height | Letter Spacing |
|---------|------|--------|------|-------------|----------------|
| H1 (Page Title) | 1.5rem | 700 | Outfit | 1.2 | -0.02em |
| H2 (Section Title) | 1.25rem | 600 | Outfit | 1.3 | -0.01em |
| H3 (Card Title) | 1rem | 600 | Outfit | 1.4 | 0 |
| Body | 0.85rem | 400 | Inter | 1.5 | 0 |
| Body Strong | 0.85rem | 600 | Inter | 1.5 | 0 |
| Small / Label | 0.75rem | 500 | Inter | 1.4 | 0.01em |
| Micro | 0.7rem | 500 | Inter | 1.4 | 0.02em |
| Stat Value | 1.75rem | 700 | Outfit | 1.1 | -0.02em |
| Stat Label | 0.75rem | 500 | Inter | 1.4 | 0.01em |

### Text Colors

- Primary text: `var(--text-primary)` (#0f172a)
- Secondary text: `var(--text-secondary)` (#64748b)
- Tertiary text: `var(--text-tertiary)` (#94a3b8)
- Inverse text: `var(--text-inverse)` (#ffffff) — used on sidebar, dark badges

---

## 5. Layout Architecture

### Global Structure

The entire layout is rebuilt around a **sidebar-first** pattern:

```
+-------------------------------------------+
|  Sidebar (220px)  |  Main Content Area     |
|  Fixed, dark      |  scrollable, white bg  |
|                   |  max-width: 1200px     |
|  [Logo]           |  centered              |
|  [Nav Item]       |                        |
|  [Nav Item]       |  [Page Header]         |
|  [Nav Item]       |  [Content]             |
|  [Nav Item]       |  [Cards / Tables /     |
|  [User Card]      |   Forms]               |
|                   |                        |
+-------------------------------------------+
```

### Sidebar (Left Navigation)

- **Width:** 220px (fixed)
- **Background:** `var(--bg-sidebar)` (#0f172a)
- **Position:** Fixed left, full height (`100vh`), `z-index: 1000`
- **Shadow:** `box-shadow: 4px 0 24px rgba(0,0,0,0.08)` — subtle depth against the white content area
- **Logo Area:** Top of sidebar. App name in Outfit 700, 1.1rem, white text. A small amber dot or accent mark as a brand indicator.
- **Nav Items:**
  - Font: Inter 500, 0.85rem
  - Color: `var(--text-tertiary)` (#94a3b8) — inactive
  - Active: `var(--text-inverse)` with a 3px `var(--accent-500)` left border indicator
  - Hover: background `var(--primary-800)` (#1e293b), text transitions to white
  - Padding: 12px 20px
  - Icon + Label layout: 20px icon (inline SVG or unicode), 12px gap, label
  - Transition: `background var(--transition-fast)`
- **User Card (Bottom):** Collapsed user info — avatar circle (initials), name, role badge. Compact.
- **Mobile (<768px):** Sidebar is hidden by default. A hamburger button (top-left of main area) toggles the sidebar with a slide-in animation overlaying the content. A semi-transparent backdrop (`rgba(0,0,0,0.4)`) appears behind the sidebar.
- **Top Navbar is completely removed.** All navigation lives in the sidebar.

### Main Content Area

- **Margin-left:** 220px (to account for fixed sidebar)
- **Background:** `var(--bg-main)` (#f8fafc)
- **Min-height:** 100vh
- **Content Container:**
  - Max-width: 1200px
  - Margin: 0 auto
  - Padding: 24px 32px
- **Page Header:**
  - Contains: Page title (H1) + action buttons (right-aligned)
  - Margin-bottom: 24px
  - Border-bottom: 1px solid `var(--border-light)` on some pages (optional)

### Body Reset

```css
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: var(--text-primary);
  background: var(--bg-main);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* { box-sizing: border-box; }
```

---

## 6. Component Library

### 6.1 Elevated Cards

The card is the primary content container.

```css
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-xl); /* 16px */
  border: 1px solid var(--border-light);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
```

**Variants:**
- `.card-compact` — padding: 16px
- `.card-flat` — box-shadow: none; border: 1px solid var(--border-light)
- `.card-stat` — centered text, larger stat value, accent color for number

### 6.2 Buttons

All buttons are **pill-shaped** (border-radius: var(--radius-full)).

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
  text-decoration: none;
  line-height: 1;
}
.btn:hover {
  transform: scale(1.02);
}
.btn:active {
  transform: scale(0.98);
}

.btn-primary {
  background: var(--accent-500);
  color: var(--primary-900);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}
.btn-primary:hover {
  background: var(--accent-400);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.btn-secondary {
  background: var(--primary-900);
  color: var(--text-inverse);
}
.btn-secondary:hover {
  background: var(--primary-800);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-medium);
}
.btn-outline:hover {
  background: var(--bg-main);
  border-color: var(--text-secondary);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}
.btn-ghost:hover {
  background: var(--bg-main);
  color: var(--text-primary);
}

.btn-danger {
  background: var(--danger-100);
  color: var(--danger-500);
}
.btn-danger:hover {
  background: var(--danger-500);
  color: #fff;
}

.btn-sm { padding: 6px 14px; font-size: 0.75rem; }
.btn-lg { padding: 14px 28px; font-size: 1rem; }
```

### 6.3 Data Tables

Tables are used for admin pages and structured data. Clean, modern, scannable.

```css
.table-modern {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.85rem;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-light);
}
.table-modern thead {
  background: var(--bg-main);
}
.table-modern th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 10;
}
.table-modern td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-primary);
  vertical-align: middle;
}
.table-modern tbody tr:nth-child(even) {
  background: #fafbfc;
}
.table-modern tbody tr:hover {
  background: #f1f5f9;
  transition: background var(--transition-fast);
}
.table-modern tbody tr:last-child td {
  border-bottom: none;
}
```

### 6.4 Forms

```css
.form-group {
  margin-bottom: 20px;
}
.form-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 6px;
}
.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
}
.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: var(--accent-500);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}
.form-input::placeholder {
  color: var(--text-tertiary);
}
.form-input:disabled,
.form-select:disabled {
  background: var(--bg-main);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
```

### 6.5 Toggle Switches

```css
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--border-medium);
  border-radius: var(--radius-full);
  transition: background var(--transition-fast);
}
.toggle-slider::before {
  content: "";
  position: absolute;
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-switch input:checked + .toggle-slider {
  background: var(--accent-500);
}
.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(22px);
}
```

### 6.6 Status Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
}
.badge-success { background: var(--success-100); color: var(--success-500); }
.badge-warning { background: var(--warning-100); color: var(--warning-500); }
.badge-danger  { background: var(--danger-100); color: var(--danger-500); }
.badge-info    { background: var(--info-100); color: var(--info-500); }
.badge-holiday { background: var(--holiday-100); color: var(--holiday-500); }
.badge-draft   { background: #f1f5f9; color: var(--text-secondary); border: 1px solid var(--border-light); }
.badge-submitted { background: var(--success-100); color: var(--success-500); }
.badge-reviewed { background: var(--info-100); color: var(--info-500); }
.badge-admin { background: var(--accent-100); color: var(--accent-500); }
```

### 6.7 Empty States

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}
.empty-state-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}
.empty-state-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.empty-state-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  max-width: 400px;
}
```

---

## 7. Animation System

All animations use `ease` timing and `will-change` hints for performance.

### 7.1 Page Entrance

```css
@keyframes page-enter {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.page-enter {
  animation: page-enter 0.3s ease forwards;
}
```

Applied to the main content wrapper on every page load.

### 7.2 Card Hover Lift

```css
.card-hover {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

### 7.3 Button Interactions

```css
.btn {
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}
.btn:hover {
  transform: scale(1.02);
}
.btn-primary:hover {
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.35);
}
.btn:active {
  transform: scale(0.98);
}
```

### 7.4 Sidebar Slide-In (Mobile)

```css
@keyframes sidebar-slide-in {
  from { transform: translateX(-100%); }
  to   { transform: translateX(0); }
}
.sidebar-mobile-open {
  animation: sidebar-slide-in 0.25s ease forwards;
}
.sidebar-backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  animation: fade-in 0.2s ease;
}
```

### 7.5 Table Row Staggered Entrance

```css
@keyframes row-fade-in {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}
.table-row-animate {
  animation: row-fade-in 0.3s ease forwards;
  opacity: 0;
}
.table-row-animate:nth-child(1) { animation-delay: 0.05s; }
.table-row-animate:nth-child(2) { animation-delay: 0.10s; }
.table-row-animate:nth-child(3) { animation-delay: 0.15s; }
.table-row-animate:nth-child(4) { animation-delay: 0.20s; }
.table-row-animate:nth-child(5) { animation-delay: 0.25s; }
/* ... continues for up to 15 rows */
```

### 7.6 Modal / Overlay

```css
@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes modal-content-in {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
.modal-backdrop {
  animation: modal-backdrop-in 0.2s ease;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(6px);
}
.modal-content {
  animation: modal-content-in 0.25s ease;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}
```

### 7.7 Focus Ring Animation

```css
.form-input:focus {
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}
```

---

## 8. Page-by-Page Redesign

### 8.1 Dashboard (My Monthly Diaries)

- **Layout:** Page header with title + "+ New Month" primary button.
- **Content:** Card-based list (retained but styled with new cards). Each diary card uses `.card` with a left border accent indicating status:
  - Draft: `var(--border-light)` left border
  - Submitted: `var(--success-500)` left border
  - Reviewed: `var(--info-500)` left border
- **Card content:** Month/Year (Outfit 600), status badge (pill), grand total (right-aligned, Outfit 700, 1.1rem), action row (ghost buttons: Calendar, Preview, Excel, Edit, Delete).
- **Empty state:** `.empty-state` with a calendar icon.

### 8.2 Calendar View

- **Layout:** Page header with month title + bank state/GSTIN metadata + status badge.
- **Action bar:** Row of pill buttons. "Add Manually" and "Preview" always visible. Admin-only buttons (Upload WhatsApp, Compute Leaves, Travel, Hotel, Local, Other, Bills) grouped together with a subtle divider.
- **Legend:** Horizontal row of `.badge` elements showing color meanings.
- **Grid:** CSS Grid `repeat(7, 1fr)` with gap: 8px.
- **Day cells:** `.card` style, min-height: 85px, padding: 10px.
  - Present: `var(--success-100)` bg, `var(--success-500)` border
  - Leave: `var(--warning-100)` bg, `var(--warning-500)` border
  - Holiday: `var(--info-100)` bg, `var(--info-500)` border
  - Weekend: `var(--bg-main)` bg, `var(--text-tertiary)` text
  - Missing: white bg, dashed `var(--border-medium)` border
  - Review: `var(--accent-100)` bg, `var(--accent-500)` border
  - Cell content: day number (Outfit 700, 1.1rem), status label (micro badge), branch name (truncated, secondary text). Edit link as a small ghost button at bottom-right.
- **Hover:** Cell brightness(0.98), smooth transition.

### 8.3 Add / Edit Attendance

- **Layout:** `.card` container. `.form-row` (2-column grid on desktop, stacked on mobile).
- **Fields:** Date, Branch, Status, is_holiday toggle, is_leave toggle, remarks.
- **Toggles:** Styled as `.toggle-switch`.
- **Buttons:** "Save Record" (primary), "Cancel" (outline).
- **Errors:** Field border turns `var(--danger-500)`, red helper text below field.

### 8.4 Preview Diary

- **Layout:** Page header with diary title + "Download TA" / "Download HRMS" / "Submit" action buttons.
- **Staff Info Card:** Top card with staff details in a compact grid (4 columns desktop, 2 tablet, 1 mobile). Left border accent: `var(--accent-500)`.
- **Attendance Summary:** Mini calendar grid (7xN) using small colored squares (12px). Below it, a text summary.
- **Expense Sections:** Each section (Travel, Hotels, Local, Other, Bills) is a `.card` with a section header (H2).
- **Data Tables:** If data exists, use `.table-modern`. If empty, use inline `.empty-state` compact variant.
- **Grand Total Card:** Full-width card at bottom with `var(--primary-900)` background, white text, large stat value in Outfit 700.

### 8.5 List Pages — Travel, Hotels, Local, Other, Bills

- **Layout:** Page header with title + "Add New" primary button.
- **Content:** Card-based list (retained from current design but with new styling). Each expense is a `.card` with:
  - Travel: From → To arrow, mode badge, amount, date
  - Hotel: Hotel name, city, dates, amount, nights count
  - Local: From → To, mode, distance, amount
  - Other: Description, amount, date
  - Bills: Vendor, amount, date, status
- **Actions:** Edit and Delete as icon-only ghost buttons (or text "Edit" / "Delete" as small outline buttons) on the right side of the card.
- **Mobile:** Cards stack vertically, full-width, internal layout switches to vertical stack.

### 8.6 Add / Edit Forms — Travel, Hotel, Local, Other, Bills

- **Layout:** `.card` container. `.form-row` 2-column grid.
- **Fields:** All standard form inputs styled with `.form-input` / `.form-select`.
- **File Upload (Bills):** Styled as a drop-zone area: dashed border, centered upload icon + text, changes to solid border on hover/drag.
- **Buttons:** "Save" (primary), "Cancel" (outline). If editing, "Delete" (danger, right-aligned).
- **Validation:** Inline error messages below fields.

### 8.7 Admin — Users List

- **Layout:** Page header with "Users" title + search input (right-aligned).
- **Content:** `.table-modern` with columns: Staff No, Name, Designation, DP Code, Section, Zone, Role, Actions.
- **Actions:** Edit (outline btn-sm), Delete (danger btn-sm).
- **Role badges:** Admin = `.badge-admin`, User = `.badge-draft`.

### 8.8 Admin — User Edit

- **Layout:** `.card` with `.form-row` grid.
- **Fields:** All user profile fields editable.
- **Buttons:** "Save Changes" (primary), "Cancel" (outline).

### 8.9 Admin — All Diaries

- **Layout:** Page header with filters (month, year, status dropdowns) + "Filter" button.
- **Content:** `.table-modern` with sticky header. Columns: Staff, Month, Year, Status, Total, Actions.
- **Status:** `.badge` variants.

### 8.10 Admin — Linked Accounts

- **Layout:** Page header with "Google Linked Accounts" title.
- **Content:** `.table-modern`. Columns: Google UID, Name, Email, Staff No, Linked At, Actions.
- **Actions:** "Unlink" (danger btn-sm) with confirmation.

### 8.11 Admin — Holidays

- **Layout:** Page header with "Holiday Calendar" + "Add Holiday" primary button + "Refresh from RBI" secondary button.
- **Filter bar:** State dropdown + Year dropdown + "Apply" button.
- **Add form:** Expandable section (slide-down animation) below header with form fields in a `.form-row`.
- **Table:** `.table-modern`. Columns: Date, Day, Description, State, Type, Actions.
- **Type badge:** `.badge-holiday` for RBI holidays.
- **Empty state:** `.empty-state` with calendar icon.

### 8.12 Profile Page

- **Layout:** Single centered column, max-width: 600px.
- **Content:** `.card` with 2-column grid of read-only fields.
- **Fields:** Staff No, Name, Designation, DP Code, Section, Zone, Basic Pay, Home State, City Category, Email, Mobile, Role.
- **Role badge:** Large `.badge` at top of card.
- **Edit button:** "Edit Profile" primary button at bottom of card (links to profile edit).

### 8.13 Profile Edit

- **Layout:** Same as Profile but with editable `.form-input` fields.
- **Buttons:** "Save Changes" (primary), "Cancel" (outline).

### 8.14 Login Page

- **Layout:** Full-screen dark background (`var(--primary-900)`). No sidebar.
- **Content:** Centered `.card` (max-width: 420px) with subtle shadow.
- **Header:** App logo + "Welcome back" in Outfit 700.
- **Button:** Google sign-in as `.btn-secondary` (dark background, white text) with Google icon (inline SVG).
- **Footer:** "Secured with Firebase Authentication" in tertiary text.

### 8.15 Setup Account Page

- **Layout:** Same as Login — full-screen dark background, centered card.
- **Content:** Email (read-only), Staff Number, Mobile inputs.
- **Button:** "Link & Continue" (primary).

### 8.16 Upload WhatsApp Chat

- **Layout:** Page header with "Import WhatsApp Attendance" + back button.
- **Content:** `.card` with instructions text + file upload drop zone.
- **Drop zone:** Dashed border (`var(--border-medium)`), centered upload icon, text "Drag & drop or click to browse". On hover: border color changes to `var(--accent-500)`, background `var(--accent-100)`.
- **Button:** "Import Chat" (primary), disabled until file selected.
- **Results:** After upload, show parsed records in `.table-modern` with confirm/cancel actions.

### 8.17 Upload Bill (OCR)

- **Layout:** Similar to Upload WhatsApp but with bill-specific fields.
- **Content:** `.card` with drop zone + vendor/amount/date fields (auto-filled from OCR if available).
- **Button:** "Save Bill" (primary).

### 8.18 Edit Diary (Meta)

- **Layout:** Page header with "Edit Diary" title.
- **Content:** `.card` with form fields: Bank State, GSTIN, etc.
- **Buttons:** "Save Changes" (primary), "Cancel" (outline).

### 8.19 Register Page

- **Status:** Likely unused post-Google-auth. If retained, match Login styling.

---

## 9. Responsive Strategy

### Breakpoints

| Name | Range | Behavior |
|------|-------|----------|
| Mobile | < 576px | Single column, stacked forms, sidebar hidden (hamburger), cards full-width, calendar cells compact (min-height: 55px), table cards horizontal scroll |
| Tablet | 576px – 768px | 2-column grids where applicable, sidebar hidden (hamburger), calendar cells compact, cards full-width |
| Desktop | 768px – 1200px | Sidebar visible (220px), standard layout, 2-column forms, calendar standard size |
| Large Desktop | > 1200px | Sidebar visible, max-width container (1200px) centered, generous whitespace |

### Mobile Sidebar Behavior

- **Trigger:** Hamburger icon (three horizontal lines, 24px, `var(--text-primary)`) in top-left of page header.
- **Open:** Sidebar slides in from left (0.25s ease), backdrop fades in (`rgba(0,0,0,0.4)` with `backdrop-filter: blur(4px)`).
- **Close:** Click backdrop, click hamburger again, or click a nav link (optional).
- **Z-index:** Sidebar: 1000, Backdrop: 999.
- **Width:** 260px on mobile (slightly wider for touch).

### Form Responsive Behavior

- `.form-row` switches from `grid-template-columns: 1fr 1fr` to `1fr` at < 768px.
- Form inputs remain full-width within their grid cell.
- Buttons stack vertically: primary full-width, secondary full-width below it.

### Table Responsive Behavior

- At < 768px, `.table-modern` switches to a card-based view if possible, or gets a horizontal scroll container (`overflow-x: auto` on a wrapper div).
- Sticky header remains but may be less useful on very small screens.

### Calendar Responsive Behavior

- Grid always stays `repeat(7, 1fr)`.
- Cell min-height: 55px (mobile), 75px (tablet), 90px (desktop).
- Cell padding: 6px (mobile), 10px (tablet/desktop).
- Font sizes scale down slightly on mobile.

---

## 10. Files to Modify

### CSS Foundation

| File | Change |
|------|--------|
| `static/style.css` | **Complete rewrite.** Remove all Navy+Gold variables and classes. Implement new color system, typography, layout (sidebar offsets), component library, animations, and responsive breakpoints. |

### Base Template

| File | Change |
|------|--------|
| `templates/base.html` | **Restructure.** Remove top navbar. Implement sidebar (220px fixed left). Add Google Fonts (Outfit + Inter). Add mobile hamburger toggle. Update footer / meta. Ensure all `{% block content %}` areas are wrapped correctly. |

### Authentication Pages

| File | Change |
|------|--------|
| `templates/login.html` | Full-screen dark background (`var(--primary-900)`). Centered card with new styling. Google button styled as `.btn-secondary`. |
| `templates/setup_account.html` | Same layout as login. Centered card. Form fields with new input styling. |
| `templates/register.html` | Match login styling if still in use. |

### Core Application Pages

| File | Change |
|------|--------|
| `templates/dashboard.html` | Card-based diary list with new `.card` styling, status badges, action buttons. |
| `templates/calendar.html` | CSS Grid calendar with new cell colors, action bar with pill buttons, legend. |
| `templates/add_attendance.html` | `.card` wrapper, `.form-row` 2-column layout, `.form-input` styling, toggle switches. |
| `templates/edit_attendance.html` | Match add_attendance.html exactly. |
| `templates/preview_diary.html` | Card sections, mini calendar grid, `.table-modern` for data, grand total stat card. |
| `templates/edit_diary.html` | `.card` wrapper, form styling. |

### Expense List Pages

| File | Change |
|------|--------|
| `templates/list_travel.html` | `.card` for each expense item. New badge/button styling. |
| `templates/list_hotels.html` | Same as list_travel.html. |
| `templates/list_local.html` | Same as list_travel.html. |
| `templates/list_other.html` | Same as list_travel.html. |
| `templates/list_bills.html` | Same as list_travel.html. |

### Expense Form Pages

| File | Change |
|------|--------|
| `templates/add_travel.html` | `.card` wrapper, `.form-row` layout, `.form-input` styling. |
| `templates/edit_travel.html` | Match add_travel.html. |
| `templates/add_hotel.html` | Same structure. |
| `templates/edit_hotel.html` | Match add_hotel.html. |
| `templates/add_local.html` | Same structure. |
| `templates/edit_local.html` | Match add_local.html. |
| `templates/add_other.html` | Same structure. |
| `templates/edit_other.html` | Match add_other.html. |

### Admin Pages

| File | Change |
|------|--------|
| `templates/admin_users.html` | `.table-modern` styling, search bar, new badge/button styling. |
| `templates/admin_user_edit.html` | `.card` wrapper, `.form-row` layout. |
| `templates/admin_diaries.html` | `.table-modern` styling, filter bar. |
| `templates/admin_links.html` | `.table-modern` styling. |
| `templates/admin_holidays.html` | `.table-modern` styling, expandable add form, filter bar. |

### Utility Pages

| File | Change |
|------|--------|
| `templates/profile.html` | `.card` with 2-column info grid, large role badge. |
| `templates/profile_edit.html` | `.card` with editable `.form-input` fields. |
| `templates/upload_whatsapp.html` | `.card` with drop zone, `.table-modern` for results. |
| `templates/upload_bill.html` | Same as upload_whatsapp.html with bill fields. |

---

## 11. Implementation Order

This order is designed to minimize rework and allow incremental visual validation.

### Phase 1: CSS Foundation + Base Template (The Skeleton)

1. Rewrite `static/style.css` with the new color system, typography, layout, components, and animations.
2. Restructure `templates/base.html` with the sidebar layout, font loading, and mobile hamburger.
3. **Validation:** Load any page. It should have the sidebar, correct fonts, and no broken layout.

### Phase 2: Login + Setup (First Impressions)

4. Update `templates/login.html` with dark background and centered card.
5. Update `templates/setup_account.html` to match login styling.
6. **Validation:** Visit `/auth/login`. It should look like a modern SaaS login.

### Phase 3: Dashboard (The Home Page)

7. Update `templates/dashboard.html` with new card styling, badges, and buttons.
8. **Validation:** Log in. Dashboard should feel like a premium dashboard.

### Phase 4: Calendar + Attendance Forms (Core Workflows)

9. Update `templates/calendar.html` with new grid, cell colors, action bar, and legend.
10. Update `templates/add_attendance.html` and `templates/edit_attendance.html` with new form layout.
11. **Validation:** Navigate to a diary calendar. Add/edit attendance. Forms should be clean and responsive.

### Phase 5: Preview + Expense Lists (Data Presentation)

12. Update `templates/preview_diary.html` with cards, tables, and mini calendar.
13. Update all list pages: `list_travel.html`, `list_hotels.html`, `list_local.html`, `list_other.html`, `list_bills.html`.
14. **Validation:** Preview a diary. View expense lists. Data should be scannable and clean.

### Phase 6: Expense Forms (Data Entry)

15. Update all add/edit forms: `add_travel.html`, `edit_travel.html`, `add_hotel.html`, `edit_hotel.html`, `add_local.html`, `edit_local.html`, `add_other.html`, `edit_other.html`.
16. **Validation:** Add/edit each expense type. Forms should be consistent and responsive.

### Phase 7: Admin Pages (Control Panel)

17. Update `templates/admin_users.html`, `templates/admin_user_edit.html`, `templates/admin_diaries.html`, `templates/admin_links.html`, `templates/admin_holidays.html`.
18. **Validation:** As admin, visit all admin pages. Tables should look professional and be filterable.

### Phase 8: Profile + Upload Pages (Remaining)

19. Update `templates/profile.html`, `templates/profile_edit.html`.
20. Update `templates/upload_whatsapp.html`, `templates/upload_bill.html`.
21. Update `templates/edit_diary.html`.
22. **Validation:** All remaining pages should match the new design system.

### Phase 9: Final Polish

23. **Responsive testing:** Test at 320px, 768px, 1024px, 1440px.
24. **Animation consistency:** Verify all hover states, transitions, and page entrances are smooth.
25. **Accessibility check:** Verify all text meets contrast ratios. Verify focus rings are visible.
26. **Cross-browser check:** Verify fonts and flexbox/grid layouts in modern browsers.
27. **Dark mode evaluation (optional):** Consider if a dark mode toggle is desired (not in scope, but the `--primary-*` palette supports it).

---

## Appendix A: Quick Reference — Color Migrations

| Old Token (Navy+Gold) | New Token (Modern FinTech) |
|-----------------------|---------------------------|
| `--color-navy-900` (#0a1628) | `--primary-900` (#0f172a) |
| `--color-gold` (#d4a843) | `--accent-500` (#f59e0b) |
| `--color-bg` (#f0f2f5) | `--bg-main` (#f8fafc) |
| `--color-surface` (#ffffff) | `--bg-surface` (#ffffff) |
| `--color-text` (#0a1628) | `--text-primary` (#0f172a) |
| `--color-muted` (#6b7280) | `--text-secondary` (#64748b) |
| `--color-border` (#e5e7eb) | `--border-light` (#e2e8f0) |
| `--color-success` (#16a34a) | `--success-500` (#10b981) |
| `--color-danger` (#dc2626) | `--danger-500` (#ef4444) |
| `--color-info` (#4338ca) | `--info-500` (#3b82f6) |

## Appendix B: Icon Strategy

- **No external icon library.** Use inline SVG for critical icons (Google logo, hamburger, upload, etc.).
- **Unicode emoji:** Use sparingly for empty states and decorative elements only (e.g., 📎, 📤, 📋). Do not use emoji for functional UI actions.
- **Toggle switch:** Pure CSS (no icon needed).
- **Status indicators:** Color + text only. No checkmark/X icons needed.

---

*End of Spec*
