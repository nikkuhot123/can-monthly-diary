---
status: in-progress
phase: 1
updated: 2026-05-31
---

# Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Complete visual overhaul of the Audit Diary System — navy/gold theme, card-based layouts, CSS Grid calendar, consistent component library across 30+ templates.

**Architecture:** One CSS file (`static/style.css`) is the design system foundation; all templates consume it. No JS framework — pure Bootstrap 5.3 + custom CSS. Templates extend `base.html` for the shared chrome.

**Tech Stack:** Bootstrap 5.3, Inter (Google Fonts), CSS Grid, Jinja2 templating, HTMX (existing, kept)

---

## Color System
- Navy: `#0a1628` → `#253a5c` (4 levels)
- Gold accent: `#d4a843`
- Semantic: green (success), yellow (warning), red (danger), blue (info), blue (holiday)
- Neutrals: bg `#f0f2f5`, surface white, text `#0a1628`, muted `#6b7280`

## Components
- **Cards**: white, border-radius 12px, subtle shadow, color-coded left border (gold=draft, green=submitted, blue=reviewed)
- **Pill buttons**: rounded (20px), colored backgrounds, 0.8rem font
- **Status badges**: pill style with semantic colors
- **Calendar Grid**: CSS Grid 7 columns, color-coded cells with day number + status + branch
- **Forms**: rounded inputs (8px), gold focus ring, toggle switches for checkboxes
- **Page header**: flex row, title left + actions right

## Phase 1: CSS Foundation + Base Template [IN PROGRESS]
Files: `static/style.css` (rewrite), `templates/base.html` (rewrite)

## Phase 2: Login + Setup Account [PENDING]
Files: `templates/login.html`, `templates/setup_account.html`

## Phase 3: Dashboard [PENDING]
Files: `templates/dashboard.html`

## Phase 4: Calendar + Attendance Forms [PENDING]
Files: `templates/calendar.html`, `templates/add_attendance.html`, `templates/edit_attendance.html`

## Phase 5: Preview Diary [PENDING]
Files: `templates/preview_diary.html`

## Phase 6: List Pages [PENDING]
Files: `templates/list_travel.html`, `templates/list_hotels.html`, `templates/list_local.html`, `templates/list_other.html`, `templates/list_bills.html`

## Phase 7: Form Pages [PENDING]
Files: `templates/add_travel.html`, `templates/edit_travel.html`, `templates/add_hotel.html`, `templates/edit_hotel.html`, `templates/add_local.html`, `templates/edit_local.html`, `templates/add_other.html`, `templates/edit_other.html`, `templates/upload_whatsapp.html`, `templates/upload_bill.html`, `templates/edit_diary.html`

## Phase 8: Admin Pages + Holidays [PENDING]
Files: `templates/admin_users.html`, `templates/admin_diaries.html`, `templates/admin_links.html`, `templates/holidays.html`

## Phase 9: Profile [PENDING]
Files: `templates/profile.html`

## Phase 10: Final Polish [PENDING]
All templates — consistency pass, verify all btn/table/form classes updated

---

## Key Implementation Details

### CSS Variables (in style.css)
```css
:root {
  --color-navy-900: #0a1628;
  --color-navy-800: #0f1b2d;
  --color-navy-700: #1a2a44;
  --color-navy-600: #253a5c;
  --color-gold: #d4a843;
  --color-gold-light: #f0dfb0;
  --color-success: #16a34a;
  --color-success-bg: #dcfce7;
  --color-warning: #d97706;
  --color-warning-bg: #fef9c3;
  --color-danger: #dc2626;
  --color-danger-bg: #fef2f2;
  --color-info: #4338ca;
  --color-info-bg: #eef2ff;
  --color-holiday: #1e40af;
  --color-holiday-bg: #dbeafe;
  --color-bg: #f0f2f5;
  --color-surface: #ffffff;
  --color-text: #0a1628;
  --color-muted: #6b7280;
  --color-border: #e5e7eb;
}
```

### Base Template Changes
- Add Inter font from Google Fonts CDN
- Dark navy navbar with `navbar-audit` class, brand text in gold
- Replace `bg-light` → `var(--color-bg)`
- Replace Bootstrap nav with custom `pill-btn pill-outline` for Profile/Logout
- Add `.fade-in` animation class to content container

### Button Class Migration
- `btn btn-primary` → `pill-btn pill-primary`
- `btn btn-outline-primary` → `pill-btn pill-outline`
- `btn btn-success` → `pill-btn pill-success`
- `btn btn-warning` → `pill-btn pill-warning`
- `btn btn-danger` → `pill-btn pill-danger`
- `btn btn-info` → `pill-btn pill-info`
- Gold call-to-action → `pill-btn pill-gold`

### Card/Table Migration
- `<table class="table table-hover">` → card-based list (dashboard), or `.table-audit` class (admin tables)
- Card wrapper: `<div class="card-audit">`
- Empty state: `<div class="empty-state">` with icon + text
- Page header: `<div class="page-header">` with h2 + actions

### Login/Setup Pages
- Standalone HTML (no base.html extend — user not logged in)
- Full-screen dark gradient background (`.auth-page`)
- Centered white card (`.auth-card`)
- Google button: `.google-btn` with inline SVG icon
- Setup page: email read-only, staff_no + mobile fields, temp_token from sessionStorage

### Attendance Forms
- Two-column grid with `.row` + `.col-md-6`
- `.form-audit` class on `<form>` tag
- Toggle switches for is_holiday/is_leave checkboxes
- Pill buttons for Save/Cancel

### Calendar Grid
- `.calendar-grid` (CSS Grid, 7 columns)
- Day cells: `.calendar-cell .cell-present|.cell-leave|.cell-holiday|.cell-weekend|.cell-missing|.cell-review`
- Legend: `.legend` with `.legend-item` + `.legend-swatch`
- Header labels: `.calendar-header-cell`

### Preview Diary
- Staff info card with gold left border
- 2x2 stat card grid (Travel, Lodging, Local+Other, Grand Total)
- Grand Total card: navy background + gold text
- Mini calendar: `.mini-calendar` grid with status dots
- Expense sections as cards with colored left borders

### List Pages (Travel, Hotel, etc.)
- Each record as `.expense-card` with title, detail, amount, actions
- Empty state with relevant icon + message
- Page header with title + "Add New" button

### Forms (Add/Edit expense types)
- Wrapped in `.card-audit`
- `.form-audit` styling on inputs/selects
- Pill buttons for save/cancel
- Gold focus ring on inputs

### Profile
- Two-column info layout in `.card-audit`
- Label rows: muted label above, value below
- Role badge: gold (admin) / green (user)
