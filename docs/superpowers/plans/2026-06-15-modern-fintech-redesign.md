# Modern FinTech Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete visual overhaul of the Audit Diary System — deep slate + warm amber color system, sidebar-first layout, Outfit + Inter typography, new component library, and animations across all 30+ templates.

**Architecture:** One CSS file (`static/style.css`) is the design system foundation; all templates consume it. The base template shifts from top navbar to left sidebar layout. No JS framework — pure Bootstrap 5.3 + custom CSS. Templates extend `base.html` for the shared chrome. The old Navy+Gold theme is completely removed — no residual color variables or class names.

**Tech Stack:** Bootstrap 5.3, Outfit + Inter (Google Fonts), CSS Grid/Flexbox, Jinja2 templating, HTMX (existing, kept), openpyxl (existing, kept)

---

### Task 1: CSS Foundation — Complete style.css Rewrite

**Files:**
- Rewrite: `static/style.css` (full file, ~600+ lines)

This is the most critical task. Every other task depends on these CSS classes existing. The file must be self-contained with no references to old Navy/Gold colors.

- [ ] **Step 1: Write new style.css**

Complete new CSS content:

```css
/* ============================================================
   Audit Diary — Modern FinTech Design System
   Theme: Deep Slate + Warm Amber
   Fonts: Outfit (Headings), Inter (UI/Body)
   ============================================================ */

/* --- CSS Custom Properties (Design Tokens) --- */
:root {
  /* Primary (Slate) */
  --primary-900: #0f172a;
  --primary-800: #1e293b;
  --primary-700: #334155;
  --primary-600: #475569;

  /* Accent (Amber) */
  --accent-500: #f59e0b;
  --accent-400: #fbbf24;
  --accent-300: #fcd34d;
  --accent-100: #fef3c7;

  /* Semantic */
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

  /* Neutral / Surface */
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

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -1px rgba(15, 23, 42, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -2px rgba(15, 23, 42, 0.04);
  --shadow-xl: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 10px 10px -5px rgba(15, 23, 42, 0.04);

  /* Radii */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}

/* --- Reset & Base --- */
*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: var(--text-primary);
  background: var(--bg-main);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.5;
}

a { color: var(--accent-500); text-decoration: none; transition: color var(--transition-fast); }
a:hover { color: var(--accent-400); }

img { max-width: 100%; height: auto; }

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Outfit', sans-serif;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

h1 { font-size: 1.5rem; font-weight: 700; line-height: 1.2; letter-spacing: -0.02em; }
h2 { font-size: 1.25rem; font-weight: 600; line-height: 1.3; letter-spacing: -0.01em; }
h3 { font-size: 1rem; font-weight: 600; line-height: 1.4; letter-spacing: 0; }

.text-body { font-size: 0.85rem; font-weight: 400; }
.text-body-strong { font-size: 0.85rem; font-weight: 600; }
.text-small { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.01em; }
.text-micro { font-size: 0.7rem; font-weight: 500; letter-spacing: 0.02em; }
.text-stat-value { font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; line-height: 1.1; letter-spacing: -0.02em; }
.text-stat-label { font-size: 0.75rem; font-weight: 500; letter-spacing: 0.01em; }

.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary { color: var(--text-tertiary); }
.text-inverse { color: var(--text-inverse); }
.text-accent { color: var(--accent-500); }
.text-success { color: var(--success-500); }
.text-danger { color: var(--danger-500); }
.text-info { color: var(--info-500); }

/* --- Layout: Sidebar + Main Content --- */
.layout-wrapper {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 220px;
  height: 100vh;
  background: var(--bg-sidebar);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0,0,0,0.08);
  overflow-y: auto;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 24px;
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-inverse);
  letter-spacing: -0.02em;
}

.sidebar-brand-icon {
  color: var(--accent-500);
  font-size: 1.3rem;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-tertiary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast), color var(--transition-fast);
  text-decoration: none;
  border-left: 3px solid transparent;
}

.sidebar-nav a:hover {
  background: var(--primary-800);
  color: var(--text-inverse);
}

.sidebar-nav a.active {
  color: var(--text-inverse);
  background: var(--primary-800);
  border-left-color: var(--accent-500);
}

.sidebar-nav a .nav-icon {
  width: 20px;
  text-align: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.sidebar-nav .nav-section-label {
  padding: 16px 16px 6px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary-600);
}

/* Sidebar User Card (bottom) */
.sidebar-user {
  padding: 16px 20px;
  border-top: 1px solid var(--border-dark);
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-500);
  color: var(--primary-900);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.sidebar-user-info {
  flex: 1;
  min-width: 0;
}

.sidebar-user-name {
  color: var(--text-inverse);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-user-staff {
  color: var(--text-tertiary);
  font-size: 0.7rem;
}

.sidebar-user-actions {
  display: flex;
  gap: 4px;
}

.sidebar-user-actions a {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}

.sidebar-user-actions a:hover {
  color: var(--text-inverse);
}

/* Sidebar Toggle (hamburger, mobile) */
.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: var(--text-primary);
  font-size: 1.5rem;
  line-height: 1;
}

.sidebar-toggle:hover {
  color: var(--accent-500);
}

/* Sidebar Overlay (mobile) */
.sidebar-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 999;
  animation: fade-in 0.2s ease;
}

.sidebar-backdrop.show {
  display: block;
}

/* Sidebar Mobile Open Animation */
@keyframes sidebar-slide-in {
  from { transform: translateX(-100%); }
  to   { transform: translateX(0); }
}

.sidebar.mobile-open {
  animation: sidebar-slide-in 0.25s ease forwards;
}

/* Main Content */
.main-content {
  margin-left: 220px;
  flex: 1;
  min-height: 100vh;
  background: var(--bg-main);
}

.main-content-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h1 {
  margin: 0;
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* --- Cards --- */
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-compact {
  padding: 16px;
}

.card-flat {
  box-shadow: none;
  border: 1px solid var(--border-light);
}

.card-stat {
  text-align: center;
  padding: 24px;
}

.card-stat-value {
  font-family: 'Outfit', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--accent-500);
  line-height: 1.1;
}

.card-stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-top: 4px;
  letter-spacing: 0.01em;
}

/* Left border accents for status */
.border-draft { border-left: 4px solid var(--border-light); }
.border-submitted { border-left: 4px solid var(--success-500); }
.border-reviewed { border-left: 4px solid var(--info-500); }
.border-accent { border-left: 4px solid var(--accent-500); }

/* Card row (for horizontal data rows inside cards) */
.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
}

.card-row:last-child {
  border-bottom: none;
}

.card-row-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-row-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* --- Buttons --- */
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
  white-space: nowrap;
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
  color: var(--primary-900);
}

.btn-secondary {
  background: var(--primary-900);
  color: var(--text-inverse);
}

.btn-secondary:hover {
  background: var(--primary-800);
  color: var(--text-inverse);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-medium);
}

.btn-outline:hover {
  background: var(--bg-main);
  border-color: var(--text-secondary);
  color: var(--text-primary);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.btn-ghost:hover {
  background: var(--bg-main);
  color: var(--text-primary);
  border-color: var(--border-light);
}

.btn-danger {
  background: var(--danger-100);
  color: var(--danger-500);
}

.btn-danger:hover {
  background: var(--danger-500);
  color: #fff;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.75rem;
}

.btn-lg {
  padding: 14px 28px;
  font-size: 1rem;
}

/* Button icon only */
.btn-icon {
  padding: 8px;
  min-width: 36px;
  min-height: 36px;
}

/* Button group */
.btn-group {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

/* --- Forms --- */
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

.form-input.error,
.form-select.error {
  border-color: var(--danger-500);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.form-error {
  font-size: 0.75rem;
  color: var(--danger-500);
  margin-top: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

.form-row-4 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16px;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

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

.toggle-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-label {
  font-size: 0.85rem;
  color: var(--text-primary);
}

/* File Upload Dropzone */
.dropzone {
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
  background: var(--bg-surface);
}

.dropzone:hover,
.dropzone.drag-over {
  border-color: var(--accent-500);
  background: var(--accent-100);
}

.dropzone-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
}

.dropzone-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.dropzone-text strong {
  color: var(--text-primary);
}

.dropzone-filename {
  font-size: 0.8rem;
  color: var(--accent-500);
  font-weight: 600;
  margin-top: 8px;
}

/* --- Status Badges --- */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
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

/* Badge size variant */
.badge-sm { padding: 2px 8px; font-size: 0.65rem; }
.badge-lg { padding: 6px 16px; font-size: 0.85rem; }

/* --- Tables --- */
.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.table-modern {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.85rem;
  background: var(--bg-surface);
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
  background: var(--bg-main);
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

/* --- Calendar Grid --- */
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-header-cell {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 8px 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.calendar-cell {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 10px;
  min-height: 90px;
  border: 1px solid var(--border-light);
  position: relative;
  transition: filter var(--transition-fast), box-shadow var(--transition-fast);
  cursor: default;
}

.calendar-cell:hover {
  filter: brightness(0.98);
  box-shadow: var(--shadow-sm);
}

.calendar-cell.present {
  background: var(--success-100);
  border-color: var(--success-500);
}

.calendar-cell.leave {
  background: var(--warning-100);
  border-color: var(--warning-500);
}

.calendar-cell.holiday {
  background: var(--info-100);
  border-color: var(--info-500);
}

.calendar-cell.weekend {
  background: var(--bg-main);
  border-color: var(--border-light);
}

.calendar-cell.weekend .day-number {
  color: var(--text-tertiary);
}

.calendar-cell.missing {
  background: var(--bg-surface);
  border-style: dashed;
  border-color: var(--border-medium);
}

.calendar-cell.review {
  background: var(--accent-100);
  border-color: var(--accent-500);
}

.calendar-cell.empty {
  background: transparent;
  border: none;
  min-height: 0;
  padding: 0;
}

.calendar-cell .day-number {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.calendar-cell .day-status {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.calendar-cell .day-branch {
  font-size: 0.65rem;
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.calendar-cell .day-edit {
  position: absolute;
  bottom: 4px;
  right: 4px;
  font-size: 0.65rem;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.calendar-cell:hover .day-edit {
  opacity: 1;
}

/* Calendar Legend */
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.legend-swatch {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}

/* --- Mini Calendar (for Preview) --- */
.mini-calendar {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 16px;
}

.mini-day {
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}

.mini-day.present { background: var(--success-500); }
.mini-day.leave { background: var(--warning-500); }
.mini-day.holiday { background: var(--info-500); }
.mini-day.weekend { background: var(--bg-main); border-color: var(--border-medium); }
.mini-day.missing { background: var(--bg-surface); border-style: dashed; }
.mini-day.empty { background: transparent; border: none; }

/* --- Diary Cards (Dashboard) --- */
.diary-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.diary-card-main {
  flex: 1;
  min-width: 0;
}

.diary-card-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.diary-card-meta {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.diary-card-amount {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
}

.diary-card-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

/* --- Expense Cards (List Pages) --- */
.expense-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.expense-card-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--bg-main);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.expense-card-body {
  flex: 1;
  min-width: 0;
}

.expense-card-title {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 2px;
}

.expense-card-detail {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.expense-card-amount {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
  white-space: nowrap;
}

.expense-card-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

/* --- Empty States --- */
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

/* Compact empty state (for inside cards) */
.empty-state-compact {
  padding: 32px 16px;
}

.empty-state-compact .empty-state-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

/* --- Auth Pages --- */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-900);
  padding: 24px;
}

.auth-card {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-xl);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-900);
  margin-bottom: 8px;
}

.auth-logo-icon {
  color: var(--accent-500);
}

.auth-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.auth-welcome {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

/* Google Sign-In Button */
.google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  padding: 12px 24px;
  background: var(--primary-900);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-full);
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.google-btn:hover {
  background: var(--primary-800);
  transform: scale(1.02);
}

.google-btn:active {
  transform: scale(0.98);
}

.google-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* --- Modal / Overlay --- */
@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes modal-content-in {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(6px);
  z-index: 1040;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: modal-backdrop-in 0.2s ease;
}

.modal-content-custom {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  padding: 32px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
  animation: modal-content-in 0.25s ease;
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.modal-title-custom {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
}

.modal-close-custom {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: color var(--transition-fast);
}

.modal-close-custom:hover {
  color: var(--text-primary);
}

.modal-footer-custom {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

/* --- Flash Messages --- */
.flash-messages {
  margin-bottom: 16px;
}

.flash {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.flash-success {
  background: var(--success-100);
  color: var(--success-500);
  border: 1px solid var(--success-500);
}

.flash-error {
  background: var(--danger-100);
  color: var(--danger-500);
  border: 1px solid var(--danger-500);
}

.flash-info {
  background: var(--info-100);
  color: var(--info-500);
  border: 1px solid var(--info-500);
}

.flash-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  padding: 0;
  line-height: 1;
}

.flash-close:hover {
  opacity: 1;
}

/* --- Filter / Search Bars --- */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-bar .form-select,
.filter-bar .form-input {
  width: auto;
  min-width: 150px;
}

/* --- Utility Classes --- */
.fade-in {
  animation: fade-in 0.3s ease forwards;
}

.page-enter {
  animation: page-enter 0.3s ease forwards;
}

.mt-0 { margin-top: 0; }
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-5 { margin-top: 24px; }
.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 4px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 12px; }
.mb-4 { margin-bottom: 16px; }
.mb-5 { margin-bottom: 24px; }
.gap-1 { gap: 4px; }
.gap-2 { gap: 8px; }
.gap-3 { gap: 12px; }
.gap-4 { gap: 16px; }

.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }
.flex-1 { flex: 1; }
.shrink-0 { flex-shrink: 0; }

.w-full { width: 100%; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* --- Action Bar (Calendar toolbar) --- */
.action-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  margin-bottom: 16px;
}

.action-bar-divider {
  width: 1px;
  height: 24px;
  background: var(--border-light);
  margin: 0 4px;
}

/* --- Info Row (for staff details) --- */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

/* --- Animations --- */
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes page-enter {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes row-fade-in {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}

.table-row-animate {
  animation: row-fade-in 0.3s ease forwards;
  opacity: 0;
}

.table-row-animate:nth-child(1)  { animation-delay: 0.05s; }
.table-row-animate:nth-child(2)  { animation-delay: 0.10s; }
.table-row-animate:nth-child(3)  { animation-delay: 0.15s; }
.table-row-animate:nth-child(4)  { animation-delay: 0.20s; }
.table-row-animate:nth-child(5)  { animation-delay: 0.25s; }
.table-row-animate:nth-child(6)  { animation-delay: 0.30s; }
.table-row-animate:nth-child(7)  { animation-delay: 0.35s; }
.table-row-animate:nth-child(8)  { animation-delay: 0.40s; }
.table-row-animate:nth-child(9)  { animation-delay: 0.45s; }
.table-row-animate:nth-child(10) { animation-delay: 0.50s; }
.table-row-animate:nth-child(11) { animation-delay: 0.55s; }
.table-row-animate:nth-child(12) { animation-delay: 0.60s; }
.table-row-animate:nth-child(13) { animation-delay: 0.65s; }
.table-row-animate:nth-child(14) { animation-delay: 0.70s; }
.table-row-animate:nth-child(15) { animation-delay: 0.75s; }

/* --- Responsive Breakpoints --- */

/* Mobile: < 576px */
@media (max-width: 575.98px) {
  .sidebar {
    transform: translateX(-100%);
    width: 260px;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .sidebar-toggle {
    display: inline-flex;
  }
  .main-content {
    margin-left: 0;
  }
  .main-content-inner {
    padding: 16px;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .page-header-actions {
    width: 100%;
  }
  .page-header-actions .btn {
    flex: 1;
    justify-content: center;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .form-row-3 {
    grid-template-columns: 1fr;
  }
  .form-row-4 {
    grid-template-columns: 1fr;
  }
  .calendar-cell {
    min-height: 55px;
    padding: 6px;
  }
  .calendar-cell .day-number {
    font-size: 0.85rem;
  }
  .calendar-cell .day-status,
  .calendar-cell .day-branch {
    display: none;
  }
  .diary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .diary-card-actions {
    width: 100%;
    justify-content: flex-end;
  }
  .expense-card {
    flex-direction: column;
    gap: 8px;
  }
  .info-grid {
    grid-template-columns: 1fr 1fr;
  }
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-bar .form-select,
  .filter-bar .form-input {
    width: 100%;
    min-width: 0;
  }
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .action-bar-divider {
    display: none;
  }
  .table-wrapper {
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
  .auth-card {
    padding: 24px;
  }
}

/* Tablet: 576px – 768px */
@media (min-width: 576px) and (max-width: 767.98px) {
  .sidebar {
    transform: translateX(-100%);
    width: 260px;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .sidebar-toggle {
    display: inline-flex;
  }
  .main-content {
    margin-left: 0;
  }
  .main-content-inner {
    padding: 20px 24px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .calendar-cell {
    min-height: 75px;
    padding: 8px;
  }
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: 768px+ (sidebar always visible) */
@media (min-width: 768px) {
  .sidebar {
    transform: none;
  }
  .sidebar-toggle {
    display: none;
  }
  .main-content {
    margin-left: 220px;
  }
}

/* Large Desktop: > 1200px */
@media (min-width: 1200px) {
  .main-content-inner {
    padding: 32px 40px;
  }
}

/* --- Print Styles --- */
@media print {
  .sidebar { display: none; }
  .main-content { margin-left: 0; }
  .btn { display: none; }
  .card { box-shadow: none; border: 1px solid #ddd; }
}
```

- [ ] **Step 2: Write the file to disk**

```bash
Write the above CSS content to `C:\Users\nikhi\Desktop\AuditReport\static\style.css` (full overwrite)
```

**Verification:** Open the file, confirm no old Navy/Gold references remain.

---

### Task 2: Base Template — Sidebar Layout

**Files:**
- Rewrite: `templates/base.html`

- [ ] **Step 1: Rewrite base.html with sidebar layout**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-ERTHP6NKMS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-ERTHP6NKMS');
    </script>
    <title>{% block title %}Audit Diary System{% endblock %}</title>
    <!-- Google Fonts: Outfit + Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- Bootstrap 5.3 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom Design System -->
    <link rel="stylesheet" href="/static/style.css">
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body>
{% if user %}
<div class="layout-wrapper">
    <!-- Sidebar Overlay (mobile) -->
    <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="toggleSidebar()"></div>

    <!-- Sidebar -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <span class="sidebar-brand-icon">&#9670;</span>
            <span>Audit Diary</span>
        </div>

        <nav class="sidebar-nav">
            <a href="/attendance/dashboard" class="{{ 'active' if request.url.path == '/attendance/dashboard' else '' }}">
                <span class="nav-icon">&#9632;</span>
                <span>Dashboard</span>
            </a>
            <a href="/holidays/" class="{{ 'active' if request.url.path.startswith('/holidays') else '' }}">
                <span class="nav-icon">&#9733;</span>
                <span>Holidays</span>
            </a>
            {% if user.is_admin %}
            <div class="nav-section-label">Administration</div>
            <a href="/admin/users" class="{{ 'active' if request.url.path == '/admin/users' else '' }}">
                <span class="nav-icon">&#9679;</span>
                <span>Users</span>
            </a>
            <a href="/admin/diaries" class="{{ 'active' if request.url.path == '/admin/diaries' else '' }}">
                <span class="nav-icon">&#9636;</span>
                <span>All Diaries</span>
            </a>
            <a href="/admin/holidays" class="{{ 'active' if request.url.path == '/admin/holidays' else '' }}">
                <span class="nav-icon">&#9733;</span>
                <span>Holidays</span>
            </a>
            <a href="/admin/links" class="{{ 'active' if request.url.path == '/admin/links' else '' }}">
                <span class="nav-icon">&#8861;</span>
                <span>Linked Accounts</span>
            </a>
            {% endif %}
        </nav>

        <div class="sidebar-user">
            <div class="sidebar-user-avatar">{{ user.name[:1] }}</div>
            <div class="sidebar-user-info">
                <div class="sidebar-user-name">{{ user.name }}</div>
                <div class="sidebar-user-staff">{{ user.staff_no }}</div>
            </div>
            <div class="sidebar-user-actions">
                <a href="/auth/profile" title="Profile">&#9881;</a>
                <a href="/auth/logout" title="Logout">&#10140;</a>
            </div>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
        <div class="main-content-inner page-enter">
            <!-- Mobile hamburger + page-top bar -->
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;" class="d-md-none">
                <button class="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>
            </div>

            <!-- Flash Messages -->
            <div class="flash-messages">
                {% if error %}
                <div class="flash flash-error">
                    <span>{{ error }}</span>
                    <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
                </div>
                {% endif %}
                {% if success %}
                <div class="flash flash-success">
                    <span>{{ success }}</span>
                    <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
                </div>
                {% endif %}
            </div>

            {% block content %}{% endblock %}
        </div>
    </main>
</div>

<script>
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    sidebar.classList.toggle('mobile-open');
    backdrop.classList.toggle('show');
}
</script>
{% else %}
    {% block content %}{% endblock %}
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Note on active nav detection:** The `{{ 'active' if request.url.path == '...' else '' }}` pattern works with Starlette's `request` object. If the app passes `request` differently, adjust the condition (e.g., check `request.url.path.startswith(...)`).

- [ ] **Step 2: Write the file**

Write to `C:\Users\nikhi\Desktop\AuditReport\templates\base.html`

---

### Task 3: Login + Setup Pages

**Files:**
- Rewrite: `templates/login.html`
- Rewrite: `templates/setup_account.html`

- [ ] **Step 1: Rewrite login.html**

Standalone page (does NOT extend base.html). Full-screen dark bg with centered card:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login — Audit Diary</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="auth-page">
    <div class="auth-card">
        <div class="auth-header">
            <div class="auth-logo">
                <span class="auth-logo-icon">&#9670;</span> Audit Diary
            </div>
            <div class="auth-welcome">Welcome back</div>
            <div class="auth-subtitle">Sign in to your account</div>
        </div>

        <button id="googleSignIn" class="google-btn" onclick="handleGoogleSignIn()">
            <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Sign in with Google
        </button>

        <div id="errorMessage" style="display:none; margin-top: 16px;" class="flash flash-error"></div>

        <div class="auth-footer">Secured with Firebase Authentication</div>
    </div>
</div>

<script type="module">
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

const firebaseConfig = {
    apiKey: "{{ firebase_api_key }}",
    authDomain: "{{ firebase_auth_domain }}",
    projectId: "{{ firebase_project_id }}",
    storageBucket: "{{ firebase_storage_bucket }}",
    messagingSenderId: "{{ firebase_messaging_sender_id }}",
    appId: "{{ firebase_app_id }}"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

window.handleGoogleSignIn = async function() {
    const btn = document.getElementById('googleSignIn');
    const errorDiv = document.getElementById('errorMessage');
    btn.disabled = true;
    btn.textContent = 'Signing in...';
    errorDiv.style.display = 'none';

    try {
        const result = await signInWithPopup(auth, provider);
        const idToken = await result.user.getIdToken();
        // Send token to server
        const resp = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_token: idToken })
        });
        if (resp.redirected) {
            window.location.href = resp.url;
        } else {
            const data = await resp.json();
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.error) {
                throw new Error(data.error);
            }
        }
    } catch (error) {
        errorDiv.textContent = error.message || 'Sign-in failed. Please try again.';
        errorDiv.style.display = 'block';
        btn.disabled = false;
        btn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">...</svg> Sign in with Google`;
    }
};
</script>
</body>
</html>
```

- [ ] **Step 2: Rewrite setup_account.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup Account — Audit Diary</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="auth-page">
    <div class="auth-card">
        <div class="auth-header">
            <div class="auth-logo">
                <span class="auth-logo-icon">&#9670;</span> Audit Diary
            </div>
            <div class="auth-welcome">Complete your account</div>
            <div class="auth-subtitle">Link your Google account to a staff profile</div>
        </div>

        <form method="POST" action="/auth/setup-account">
            <input type="hidden" name="temp_token" id="tempToken">
            <div class="form-group">
                <label class="form-label">Email</label>
                <input class="form-input" type="email" id="email" value="{{ email }}" readonly disabled>
            </div>
            <div class="form-group">
                <label class="form-label">Staff Number</label>
                <input class="form-input" type="text" name="staff_no" placeholder="e.g. 861198" required>
            </div>
            <div class="form-group">
                <label class="form-label">Mobile Number</label>
                <input class="form-input" type="text" name="mobile" placeholder="e.g. 9876543210" required>
            </div>
            <button type="submit" class="btn btn-primary w-full" style="margin-top: 8px;">Link &amp; Continue</button>
        </form>

        <div class="auth-footer" style="margin-top: 16px;">Secured with Firebase Authentication</div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const tempToken = sessionStorage.getItem('temp_token');
    if (tempToken) {
        document.getElementById('tempToken').value = tempToken;
    }
});
</script>
</body>
</html>
```

- [ ] **Step 3: Write both files**

Write to `C:\Users\nikhi\Desktop\AuditReport\templates\login.html` and `C:\Users\nikhi\Desktop\AuditReport\templates\setup_account.html`

---

### Task 4: Dashboard

**File:**
- Rewrite: `templates/dashboard.html`

- [ ] **Step 1: Rewrite dashboard.html**

```html
{% extends "base.html" %}
{% block title %}Dashboard — Audit Diary{% endblock %}
{% block content %}
<div class="page-header">
    <h1>My Monthly Diaries</h1>
    <div class="page-header-actions">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newMonthModal">+ New Month</button>
    </div>
</div>

{% if user %}
<div class="card card-compact mb-5">
    <div class="flex items-center gap-3">
        <div class="sidebar-user-avatar" style="width:44px;height:44px;font-size:1.1rem;">{{ user.name[:1] }}</div>
        <div class="flex-1">
            <div class="text-body-strong">{{ user.name }}</div>
            <div class="text-small text-secondary">{{ user.staff_no }}</div>
        </div>
        {% if user.is_admin %}
        <span class="badge badge-admin">Admin</span>
        {% endif %}
    </div>
</div>
{% endif %}

{% if diaries %}
<div style="display:flex;flex-direction:column;gap:12px;">
    {% for d in diaries %}
    <div class="card card-compact border-{{ d.status }}">
        <div class="diary-card">
            <div class="diary-card-main">
                <div class="diary-card-title">{{ d.month_name }} {{ d.year }}</div>
                <div class="diary-card-meta">
                    <span class="badge badge-{{ d.status }}">{{ d.status }}</span>
                    {% if d.bank_state %}
                    <span style="margin-left:8px;">{{ d.bank_state }}</span>
                    {% endif %}
                </div>
            </div>
            <div class="diary-card-amount">&#8377; {{ "%.2f"|format(d.grand_total or 0) }}</div>
            <div class="diary-card-actions">
                <a href="/attendance/calendar/{{ d.id }}" class="btn btn-ghost btn-sm" title="Calendar">&#128197;</a>
                <a href="/attendance/preview/{{ d.id }}" class="btn btn-ghost btn-sm" title="Preview">&#128196;</a>
                <a href="/generate/download-excel/{{ d.id }}" class="btn btn-ghost btn-sm" title="Download TA Excel">&#8681;</a>
                <a href="/generate/download-hrms/{{ d.id }}" class="btn btn-ghost btn-sm" title="Download HRMS Excel">&#8681;</a>
                <a href="/attendance/edit-diary/{{ d.id }}" class="btn btn-ghost btn-sm" title="Edit">&#9998;</a>
                <form method="POST" action="/attendance/delete-diary/{{ d.id }}" style="display:inline;" onsubmit="return confirm('Delete this diary?')">
                    <button type="submit" class="btn btn-ghost btn-sm" title="Delete">&#10005;</button>
                </form>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#128197;</div>
    <div class="empty-state-title">No diaries yet</div>
    <div class="empty-state-text">Click "+ New Month" above to start your first monthly diary. You'll be able to record attendance, travel, and expenses.</div>
</div>
{% endif %}

<!-- New Month Modal -->
<div class="modal fade" id="newMonthModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" style="font-family:'Outfit',sans-serif;font-weight:600;">Start New Month</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST" action="/attendance/dashboard">
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Month</label>
                        <select class="form-select" name="month" required>
                            <option value="1">January</option>
                            <option value="2">February</option>
                            <option value="3">March</option>
                            <option value="4">April</option>
                            <option value="5">May</option>
                            <option value="6">June</option>
                            <option value="7">July</option>
                            <option value="8">August</option>
                            <option value="9">September</option>
                            <option value="10">October</option>
                            <option value="11">November</option>
                            <option value="12">December</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Year</label>
                        <input class="form-input" type="number" name="year" value="2026" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Bank State</label>
                        <select class="form-select" name="bank_state" required>
                            <option value="">Select State</option>
                            <option value="Andhra Pradesh">Andhra Pradesh</option>
                            <option value="Karnataka">Karnataka</option>
                            <option value="Kerala">Kerala</option>
                            <option value="Tamil Nadu">Tamil Nadu</option>
                            <option value="Telangana">Telangana</option>
                            <option value="Maharashtra">Maharashtra</option>
                            <option value="Delhi">Delhi</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Diary</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

**Key pattern:** `border-{{ d.status }}` maps to CSS classes `.border-draft`, `.border-submitted`, `.border-reviewed`. `badge-{{ d.status }}` maps to `.badge-draft`, `.badge-submitted`, `.badge-reviewed`. The server must pass `d.status` as lowercase strings: `"draft"`, `"submitted"`, `"reviewed"`.

- [ ] **Step 2: Write the file**

Write to `C:\Users\nikhi\Desktop\AuditReport\templates\dashboard.html`

---

### Task 5: Calendar + Attendance Forms

**Files:**
- Rewrite: `templates/calendar.html`
- Rewrite: `templates/add_attendance.html`
- Rewrite: `templates/edit_attendance.html`

- [ ] **Step 1: Rewrite calendar.html**

```html
{% extends "base.html" %}
{% block title %}Calendar — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <div>
        <h1>{{ diary.month_name }} {{ diary.year }}</h1>
        <div class="flex items-center gap-2 mt-1">
            <span class="text-small text-secondary">{{ diary.bank_state }}</span>
            {% if diary.gstin %}
            <span class="text-small text-secondary">GSTIN: {{ diary.gstin }}</span>
            {% endif %}
            <span class="badge badge-{{ diary.status }}">{{ diary.status }}</span>
        </div>
    </div>
    <div class="page-header-actions">
        <a href="/attendance/add/{{ diary.id }}" class="btn btn-primary btn-sm">+ Add Manually</a>
        <a href="/attendance/preview/{{ diary.id }}" class="btn btn-outline btn-sm">Preview</a>
        {% if user.is_admin %}
        <div class="action-bar-divider"></div>
        <a href="/travel/list/{{ diary.id }}" class="btn btn-ghost btn-sm">Travel</a>
        <a href="/hotel/list/{{ diary.id }}" class="btn btn-ghost btn-sm">Hotel</a>
        <a href="/local/list/{{ diary.id }}" class="btn btn-ghost btn-sm">Local</a>
        <a href="/other/list/{{ diary.id }}" class="btn btn-ghost btn-sm">Other</a>
        <a href="/bills/list/{{ diary.id }}" class="btn btn-ghost btn-sm">Bills</a>
        <a href="/attendance/upload-whatsapp/{{ diary.id }}" class="btn btn-ghost btn-sm">WhatsApp</a>
        <a href="/attendance/compute-leaves/{{ diary.id }}" class="btn btn-ghost btn-sm">Compute Leaves</a>
        {% endif %}
    </div>
</div>

<!-- Legend -->
<div class="legend">
    <span class="legend-item"><span class="legend-swatch" style="background:var(--success-100);border-color:var(--success-500);"></span> Present</span>
    <span class="legend-item"><span class="legend-swatch" style="background:var(--warning-100);border-color:var(--warning-500);"></span> Leave</span>
    <span class="legend-item"><span class="legend-swatch" style="background:var(--info-100);border-color:var(--info-500);"></span> Holiday</span>
    <span class="legend-item"><span class="legend-swatch" style="background:var(--bg-main);border-color:var(--border-medium);"></span> Weekend</span>
    <span class="legend-item"><span class="legend-swatch" style="background:var(--bg-surface);border-color:var(--border-medium);border-style:dashed;"></span> Missing</span>
    <span class="legend-item"><span class="legend-swatch" style="background:var(--accent-100);border-color:var(--accent-500);"></span> Review</span>
</div>

<!-- Calendar Grid -->
<div class="calendar-grid">
    {% for day_name in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"] %}
    <div class="calendar-header-cell">{{ day_name }}</div>
    {% endfor %}

    {% set day_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"] %}

    {# Assuming first_day_of_week is 0=Sun, and days_in_month is a list of dicts with day, status, branch, record_id #}
    {% if days %}
    {# Leading empty cells #}
    {% for _ in range(first_day_of_week) %}
    <div class="calendar-cell empty"></div>
    {% endfor %}

    {% for day_data in days %}
    <div class="calendar-cell {{ day_data.status }}">
        <div class="day-number">{{ day_data.day }}</div>
        {% if day_data.status_label %}
        <div class="day-status">{{ day_data.status_label }}</div>
        {% endif %}
        {% if day_data.branch %}
        <div class="day-branch">{{ day_data.branch }}</div>
        {% endif %}
        {% if day_data.record_id %}
        <a href="/attendance/edit/{{ day_data.record_id }}" class="day-edit btn btn-ghost btn-sm">&#9998;</a>
        {% endif %}
    </div>
    {% endfor %}
    {% else %}
    <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-secondary);">
        No attendance records yet. Click "+ Add Manually" to begin.
    </div>
    {% endif %}
</div>
{% endblock %}
```

**Note:** The server needs to pass `days` as a list of objects with: `day` (int), `status` (string: `"present"`, `"leave"`, `"holiday"`, `"weekend"`, `"missing"`, `"review"`), `status_label` (string or None), `branch` (string or None), `record_id` (int or None). Also pass `first_day_of_week` (int, 0-6).

- [ ] **Step 2: Rewrite add_attendance.html**

```html
{% extends "base.html" %}
{% block title %}Add Attendance — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Add Attendance</h1>
    <div class="page-header-actions">
        <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Back to Calendar</a>
    </div>
</div>

<div class="card">
    <form method="POST" action="/attendance/add/{{ diary.id }}">
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Date</label>
                <input class="form-input" type="date" name="attendance_date" required>
            </div>
            <div class="form-group">
                <label class="form-label">Branch</label>
                <select class="form-select" name="branch_id">
                    <option value="">Select Branch</option>
                    {% for branch in branches %}
                    <option value="{{ branch.id }}">{{ branch.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Status</label>
                <select class="form-select" name="status">
                    <option value="present">Present</option>
                    <option value="leave">Leave</option>
                    <option value="holiday">Holiday</option>
                    <option value="weekend">Weekend</option>
                    <option value="missing">Missing</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Remarks</label>
                <input class="form-input" type="text" name="remarks" placeholder="Optional">
            </div>
        </div>

        <div class="form-row" style="margin-top:8px;">
            <div class="form-group">
                <div class="toggle-wrapper">
                    <label class="toggle-switch">
                        <input type="checkbox" name="is_holiday">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Is Holiday</span>
                </div>
            </div>
            <div class="form-group">
                <div class="toggle-wrapper">
                    <label class="toggle-switch">
                        <input type="checkbox" name="is_leave">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Is Leave</span>
                </div>
            </div>
        </div>

        <div class="btn-group" style="margin-top:8px;">
            <button type="submit" class="btn btn-primary">Save Record</button>
            <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 3: Rewrite edit_attendance.html**

Same structure as `add_attendance.html`, with pre-filled field values from `record` object, and form action pointing to `POST /attendance/edit/{{ record.id }}`. Include a hidden `_method` field or handle the update in the route.

```html
{% extends "base.html" %}
{% block title %}Edit Attendance — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Edit Attendance</h1>
    <div class="page-header-actions">
        <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Back to Calendar</a>
    </div>
</div>

<div class="card">
    <form method="POST" action="/attendance/edit/{{ record.id }}">
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Date</label>
                <input class="form-input" type="date" name="attendance_date" value="{{ record.attendance_date }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Branch</label>
                <select class="form-select" name="branch_id">
                    <option value="">Select Branch</option>
                    {% for branch in branches %}
                    <option value="{{ branch.id }}" {% if branch.id == record.branch_id %}selected{% endif %}>{{ branch.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Status</label>
                <select class="form-select" name="status">
                    <option value="present" {% if record.status == 'present' %}selected{% endif %}>Present</option>
                    <option value="leave" {% if record.status == 'leave' %}selected{% endif %}>Leave</option>
                    <option value="holiday" {% if record.status == 'holiday' %}selected{% endif %}>Holiday</option>
                    <option value="weekend" {% if record.status == 'weekend' %}selected{% endif %}>Weekend</option>
                    <option value="missing" {% if record.status == 'missing' %}selected{% endif %}>Missing</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Remarks</label>
                <input class="form-input" type="text" name="remarks" value="{{ record.remarks or '' }}" placeholder="Optional">
            </div>
        </div>

        <div class="form-row" style="margin-top:8px;">
            <div class="form-group">
                <div class="toggle-wrapper">
                    <label class="toggle-switch">
                        <input type="checkbox" name="is_holiday" {% if record.is_holiday %}checked{% endif %}>
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Is Holiday</span>
                </div>
            </div>
            <div class="form-group">
                <div class="toggle-wrapper">
                    <label class="toggle-switch">
                        <input type="checkbox" name="is_leave" {% if record.is_leave %}checked{% endif %}>
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Is Leave</span>
                </div>
            </div>
        </div>

        <div class="btn-group" style="margin-top:8px;">
            <button type="submit" class="btn btn-primary">Update Record</button>
            <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 4: Write all three files**

Write to `templates/calendar.html`, `templates/add_attendance.html`, `templates/edit_attendance.html`

---

### Task 6: Preview Diary

**File:**
- Rewrite: `templates/preview_diary.html`

- [ ] **Step 1: Rewrite preview_diary.html**

```html
{% extends "base.html" %}
{% block title %}Preview — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <div>
        <h1>{{ diary.month_name }} {{ diary.year }} — Preview</h1>
        <div class="flex items-center gap-2 mt-1">
            <span class="text-small text-secondary">{{ diary.bank_state }}</span>
            <span class="badge badge-{{ diary.status }}">{{ diary.status }}</span>
        </div>
    </div>
    <div class="page-header-actions">
        <a href="/generate/download-excel/{{ diary.id }}" class="btn btn-primary btn-sm">&#8681; Download TA</a>
        <a href="/generate/download-hrms/{{ diary.id }}" class="btn btn-secondary btn-sm">&#8681; Download HRMS</a>
        <form method="POST" action="/attendance/submit/{{ diary.id }}" style="display:inline;">
            <button type="submit" class="btn btn-outline btn-sm">Submit</button>
        </form>
    </div>
</div>

<!-- Staff Info Card -->
<div class="card card-compact mb-5 border-accent">
    <div class="info-grid">
        <div class="info-item">
            <span class="info-label">Staff No</span>
            <span class="info-value">{{ user.staff_no }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Name</span>
            <span class="info-value">{{ user.name }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Designation</span>
            <span class="info-value">{{ user.designation or '—' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Zone</span>
            <span class="info-value">{{ user.zone or '—' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">DP Code</span>
            <span class="info-value">{{ user.dp_code or '—' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Section</span>
            <span class="info-value">{{ user.section or '—' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Basic Pay</span>
            <span class="info-value">{{ user.basic_pay or '—' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">City Category</span>
            <span class="info-value">{{ user.city_category or '—' }}</span>
        </div>
    </div>
</div>

<!-- Attendance Summary -->
<div class="card mb-5">
    <h2>Attendance Summary</h2>
    <div class="mini-calendar">
        {% for day_data in days %}
        <div class="mini-day {{ day_data.status }}" title="{{ day_data.day }}"></div>
        {% endfor %}
    </div>
    <div class="flex gap-4 flex-wrap">
        <span class="text-small">Present: <strong>{{ attendance_summary.present }}</strong></span>
        <span class="text-small">Leave: <strong>{{ attendance_summary.leave }}</strong></span>
        <span class="text-small">Holiday: <strong>{{ attendance_summary.holiday }}</strong></span>
        <span class="text-small">Weekend: <strong>{{ attendance_summary.weekend }}</strong></span>
        <span class="text-small">Missing: <strong>{{ attendance_summary.missing }}</strong></span>
    </div>
</div>

<!-- Travel Section -->
<div class="card mb-5">
    <h2>Travel</h2>
    {% if travels %}
    <div class="table-wrapper">
        <table class="table-modern">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Mode</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for t in travels %}
                <tr class="table-row-animate">
                    <td>{{ t.date }}</td>
                    <td>{{ t.from_place }}</td>
                    <td>{{ t.to_place }}</td>
                    <td><span class="badge badge-info badge-sm">{{ t.mode }}</span></td>
                    <td><strong>&#8377; {{ "%.2f"|format(t.amount) }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state empty-state-compact">
        <div class="empty-state-icon">&#9992;</div>
        <div class="empty-state-title">No travel records</div>
        <div class="empty-state-text">No travel entries for this month.</div>
    </div>
    {% endif %}
</div>

<!-- Hotels Section -->
<div class="card mb-5">
    <h2>Hotels</h2>
    {% if hotels %}
    <div class="table-wrapper">
        <table class="table-modern">
            <thead>
                <tr>
                    <th>Hotel</th>
                    <th>City</th>
                    <th>Check In</th>
                    <th>Check Out</th>
                    <th>Nights</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for h in hotels %}
                <tr class="table-row-animate">
                    <td>{{ h.hotel_name }}</td>
                    <td>{{ h.city }}</td>
                    <td>{{ h.check_in }}</td>
                    <td>{{ h.check_out }}</td>
                    <td>{{ h.nights }}</td>
                    <td><strong>&#8377; {{ "%.2f"|format(h.amount) }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state empty-state-compact">
        <div class="empty-state-icon">&#127976;</div>
        <div class="empty-state-title">No hotel stays</div>
        <div class="empty-state-text">No hotel entries for this month.</div>
    </div>
    {% endif %}
</div>

<!-- Local Conveyance Section -->
<div class="card mb-5">
    <h2>Local Conveyance</h2>
    {% if locals %}
    <div class="table-wrapper">
        <table class="table-modern">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Mode</th>
                    <th>Distance</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for l in locals %}
                <tr class="table-row-animate">
                    <td>{{ l.date }}</td>
                    <td>{{ l.from_place }}</td>
                    <td>{{ l.to_place }}</td>
                    <td><span class="badge badge-info badge-sm">{{ l.mode }}</span></td>
                    <td>{{ l.distance_km }} km</td>
                    <td><strong>&#8377; {{ "%.2f"|format(l.amount) }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state empty-state-compact">
        <div class="empty-state-icon">&#128652;</div>
        <div class="empty-state-title">No local conveyance</div>
        <div class="empty-state-text">No local conveyance entries for this month.</div>
    </div>
    {% endif %}
</div>

<!-- Other Expenses Section -->
<div class="card mb-5">
    <h2>Other Expenses</h2>
    {% if others %}
    <div class="table-wrapper">
        <table class="table-modern">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for o in others %}
                <tr class="table-row-animate">
                    <td>{{ o.date }}</td>
                    <td>{{ o.description }}</td>
                    <td><strong>&#8377; {{ "%.2f"|format(o.amount) }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state empty-state-compact">
        <div class="empty-state-icon">&#128200;</div>
        <div class="empty-state-title">No other expenses</div>
        <div class="empty-state-text">No other expense entries for this month.</div>
    </div>
    {% endif %}
</div>

<!-- Bills Section -->
<div class="card mb-5">
    <h2>Bills</h2>
    {% if bills %}
    <div class="table-wrapper">
        <table class="table-modern">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Vendor</th>
                    <th>Amount</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for b in bills %}
                <tr class="table-row-animate">
                    <td>{{ b.date }}</td>
                    <td>{{ b.vendor }}</td>
                    <td><strong>&#8377; {{ "%.2f"|format(b.amount) }}</strong></td>
                    <td><span class="badge badge-{{ b.status }}">{{ b.status }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state empty-state-compact">
        <div class="empty-state-icon">&#128196;</div>
        <div class="empty-state-title">No bills</div>
        <div class="empty-state-text">No bill entries for this month.</div>
    </div>
    {% endif %}
</div>

<!-- Grand Total Card -->
<div class="card card-stat" style="background:var(--primary-900);color:var(--text-inverse);">
    <div class="card-stat-label" style="color:var(--text-tertiary);">Grand Total</div>
    <div class="card-stat-value" style="color:var(--accent-500);">&#8377; {{ "%.2f"|format(grand_total or 0) }}</div>
</div>
{% endblock %}
```

- [ ] **Step 2: Write the file**

Write to `C:\Users\nikhi\Desktop\AuditReport\templates\preview_diary.html`

---

### Task 7: Expense List Pages

**Files:**
- Rewrite: `templates/list_travel.html`
- Rewrite: `templates/list_hotels.html`
- Rewrite: `templates/list_local.html`
- Rewrite: `templates/list_other.html`
- Rewrite: `templates/list_bills.html`

- [ ] **Step 1: Write list_travel.html (representative pattern for all)**

```html
{% extends "base.html" %}
{% block title %}Travel — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Travel</h1>
    <div class="page-header-actions">
        <a href="/travel/add/{{ diary.id }}" class="btn btn-primary btn-sm">+ Add New</a>
        <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Calendar</a>
    </div>
</div>

{% if records %}
<div style="display:flex;flex-direction:column;gap:12px;">
    {% for r in records %}
    <div class="card card-compact">
        <div class="expense-card">
            <div class="expense-card-icon">&#9992;</div>
            <div class="expense-card-body">
                <div class="expense-card-title">{{ r.from_place }} &rarr; {{ r.to_place }}</div>
                <div class="expense-card-detail">
                    <span class="badge badge-info badge-sm">{{ r.mode }}</span>
                    {{ r.date_start }}
                </div>
            </div>
            <div class="expense-card-amount">&#8377; {{ "%.2f"|format(r.amount) }}</div>
            <div class="expense-card-actions">
                <a href="/travel/edit/{{ r.id }}" class="btn btn-ghost btn-sm">&#9998;</a>
                <form method="POST" action="/travel/delete/{{ r.id }}" style="display:inline;" onsubmit="return confirm('Delete this record?')">
                    <button type="submit" class="btn btn-ghost btn-sm">&#10005;</button>
                </form>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#9992;</div>
    <div class="empty-state-title">No travel records</div>
    <div class="empty-state-text">Click "+ Add New" to record your travel for this month.</div>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Write list_hotels.html**

Same structure as list_travel.html but with:
- Icon: `&#127976;` (hotel)
- Fields: `r.hotel_name` as title, `r.city`, `r.check_in` &rarr; `r.check_out`, `r.nights`, `r.amount`
- Edit link: `/hotel/edit/{{ r.id }}`
- Delete action: `/hotel/delete/{{ r.id }}`
- Add link: `/hotel/add/{{ diary.id }}`
- Empty state icon: `&#127976;`
- Detail text: `{{ r.hotel_name }} &middot; {{ r.city }} &middot; {{ r.nights }} night(s)`

- [ ] **Step 3: Write list_local.html**

- Icon: `&#128652;` (bus)
- Fields: `r.from_place` &rarr; `r.to_place`, `r.mode`, `r.distance_km`, `r.amount`, `r.date`
- Edit link: `/local/edit/{{ r.id }}`
- Delete action: `/local/delete/{{ r.id }}`
- Add link: `/local/add/{{ diary.id }}`
- Empty state icon: `&#128652;`
- Detail text: `{{ r.mode }} &middot; {{ r.distance_km }} km &middot; {{ r.date }}`

- [ ] **Step 4: Write list_other.html**

- Icon: `&#128200;` (chart)
- Fields: `r.description` as title, `r.amount`, `r.date`
- Edit link: `/other/edit/{{ r.id }}`
- Delete action: `/other/delete/{{ r.id }}`
- Add link: `/other/add/{{ diary.id }}`
- Empty state icon: `&#128200;`
- Detail text: `{{ r.date }}`

- [ ] **Step 5: Write list_bills.html**

- Icon: `&#128196;` (document)
- Fields: `r.vendor` as title, `r.amount`, `r.date`, `r.status` as badge
- Edit link: `/bills/edit/{{ r.id }}`
- Delete action: `/bills/delete/{{ r.id }}`
- Add link: `/bills/add/{{ diary.id }}`
- Empty state icon: `&#128196;`
- Detail text: `{{ r.date }} &middot; <span class="badge badge-{{ r.status }} badge-sm">{{ r.status }}</span>`

- [ ] **Step 6: Write all five files**

Write each to its respective path.

---

### Task 8: Expense Form Pages (Add + Edit)

**Files:**
- Rewrite: `templates/add_travel.html`, `templates/edit_travel.html`
- Rewrite: `templates/add_hotel.html`, `templates/edit_hotel.html`
- Rewrite: `templates/add_local.html`, `templates/edit_local.html`
- Rewrite: `templates/add_other.html`, `templates/edit_other.html`

These all follow the same pattern: `.card` wrapper, `.form-row` 2-column grid, `.form-group`/`.form-label`/`.form-input`/`.form-select` for each field, `.btn-primary` submit, `.btn-outline` cancel.

- [ ] **Step 1: Write add_travel.html (representative)**

```html
{% extends "base.html" %}
{% block title %}Add Travel — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Add Travel</h1>
    <div class="page-header-actions">
        <a href="/travel/list/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Back to Travel</a>
    </div>
</div>

<div class="card">
    <form method="POST" action="/travel/add/{{ diary.id }}">
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">From Place</label>
                <input class="form-input" type="text" name="from_place" required placeholder="e.g. Bangalore">
            </div>
            <div class="form-group">
                <label class="form-label">To Place</label>
                <input class="form-input" type="text" name="to_place" required placeholder="e.g. Mumbai">
            </div>
            <div class="form-group">
                <label class="form-label">Mode</label>
                <select class="form-select" name="mode" required>
                    <option value="">Select mode</option>
                    <option value="Train">Train</option>
                    <option value="Flight">Flight</option>
                    <option value="Bus">Bus</option>
                    <option value="Car">Car</option>
                    <option value="Taxi">Taxi</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Date</label>
                <input class="form-input" type="date" name="date_start" required>
            </div>
            <div class="form-group">
                <label class="form-label">Amount (&#8377;)</label>
                <input class="form-input" type="number" step="0.01" name="amount" required>
            </div>
            <div class="form-group">
                <label class="form-label">Travel Class</label>
                <input class="form-input" type="text" name="travel_class" placeholder="e.g. Sleeper, AC 3-tier">
            </div>
            <div class="form-group">
                <label class="form-label">GST %</label>
                <input class="form-input" type="number" step="0.01" name="gst_percent" value="0">
            </div>
            <div class="form-group">
                <label class="form-label">Vendor GSTIN</label>
                <input class="form-input" type="text" name="vendor_gstin" placeholder="Optional">
            </div>
            <div class="form-group">
                <label class="form-label">Distance (km)</label>
                <input class="form-input" type="number" step="0.1" name="distance_km" value="0">
            </div>
            <div class="form-group">
                <label class="form-label">Ticket No.</label>
                <input class="form-input" type="text" name="ticket_no" placeholder="Optional">
            </div>
            <div class="form-group">
                <div class="toggle-wrapper" style="height:100%;padding-top:24px;">
                    <label class="toggle-switch">
                        <input type="checkbox" name="no_bill" value="1">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">No Bill</span>
                </div>
            </div>
        </div>

        <div class="btn-group" style="margin-top:8px;">
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="/travel/list/{{ diary.id }}" class="btn btn-outline">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 2-7: Write edit_travel.html, add_hotel.html, edit_hotel.html, add_local.html, edit_local.html, add_other.html**

Each follows the same pattern as `add_travel.html`. The edit versions have pre-filled values via `{{ r.field_name }}` and form action pointing to `POST /{type}/edit/{id}`. The field sets differ per expense type:

**Hotel fields:** `hotel_name`, `city`, `check_in`, `check_out`, `amount`, `nights`, `gst_percent`, `vendor_gstin`, `category`
**Local fields:** `from_place`, `to_place`, `mode`, `date`, `amount`, `distance_km`
**Other fields:** `description`, `date`, `amount`, `remarks`

- [ ] **Step 8: Write all form files**

Write to each respective path.

---

### Task 9: Admin Pages

**Files:**
- Rewrite: `templates/admin_users.html`
- Rewrite: `templates/admin_user_edit.html`
- Rewrite: `templates/admin_diaries.html`
- Rewrite: `templates/admin_links.html`
- Rewrite: `templates/admin_holidays.html`

- [ ] **Step 1: Write admin_users.html**

```html
{% extends "base.html" %}
{% block title %}Users — Admin{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Users</h1>
    <div class="page-header-actions">
        <input class="form-input" type="text" id="userSearch" placeholder="Search staff no, name..." style="width:250px;" onkeyup="filterUsers()">
    </div>
</div>

{% if users %}
<div class="table-wrapper">
    <table class="table-modern" id="usersTable">
        <thead>
            <tr>
                <th>Staff No</th>
                <th>Name</th>
                <th>Designation</th>
                <th>DP Code</th>
                <th>Section</th>
                <th>Zone</th>
                <th>Role</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for u in users %}
            <tr class="table-row-animate">
                <td><strong>{{ u.staff_no }}</strong></td>
                <td>{{ u.name }}</td>
                <td>{{ u.designation or '—' }}</td>
                <td>{{ u.dp_code or '—' }}</td>
                <td>{{ u.section or '—' }}</td>
                <td>{{ u.zone or '—' }}</td>
                <td>
                    {% if u.is_admin %}
                    <span class="badge badge-admin">Admin</span>
                    {% else %}
                    <span class="badge badge-draft">User</span>
                    {% endif %}
                </td>
                <td>
                    <div class="flex gap-1">
                        <a href="/admin/users/edit/{{ u.id }}" class="btn btn-outline btn-sm">Edit</a>
                        <form method="POST" action="/admin/users/delete/{{ u.id }}" style="display:inline;" onsubmit="return confirm('Delete this user?')">
                            <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                        </form>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
function filterUsers() {
    const input = document.getElementById('userSearch');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('usersTable');
    const rows = table.getElementsByTagName('tr');
    for (let i = 1; i < rows.length; i++) {
        const text = rows[i].textContent.toLowerCase();
        rows[i].style.display = text.includes(filter) ? '' : 'none';
    }
}
</script>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#128101;</div>
    <div class="empty-state-title">No users found</div>
    <div class="empty-state-text">There are no users registered yet.</div>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Write admin_user_edit.html**

```html
{% extends "base.html" %}
{% block title %}Edit User — {{ user_data.name }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Edit User: {{ user_data.name }}</h1>
    <div class="page-header-actions">
        <a href="/admin/users" class="btn btn-outline btn-sm">&larr; Back to Users</a>
    </div>
</div>

<div class="card">
    <form method="POST" action="/admin/users/edit/{{ user_data.id }}">
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Staff No</label>
                <input class="form-input" type="text" name="staff_no" value="{{ user_data.staff_no }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Name</label>
                <input class="form-input" type="text" name="name" value="{{ user_data.name }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Designation</label>
                <input class="form-input" type="text" name="designation" value="{{ user_data.designation or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">DP Code</label>
                <input class="form-input" type="text" name="dp_code" value="{{ user_data.dp_code or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">Section</label>
                <input class="form-input" type="text" name="section" value="{{ user_data.section or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">Zone</label>
                <input class="form-input" type="text" name="zone" value="{{ user_data.zone or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">Basic Pay</label>
                <input class="form-input" type="text" name="basic_pay" value="{{ user_data.basic_pay or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">Home State</label>
                <input class="form-input" type="text" name="home_state" value="{{ user_data.home_state or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">City Category</label>
                <select class="form-select" name="city_category">
                    <option value="">Select</option>
                    <option value="A" {% if user_data.city_category == 'A' %}selected{% endif %}>A</option>
                    <option value="B" {% if user_data.city_category == 'B' %}selected{% endif %}>B</option>
                    <option value="C" {% if user_data.city_category == 'C' %}selected{% endif %}>C</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Mobile</label>
                <input class="form-input" type="text" name="mobile" value="{{ user_data.mobile or '' }}">
            </div>
            <div class="form-group">
                <label class="form-label">Admin</label>
                <div class="toggle-wrapper" style="margin-top:6px;">
                    <label class="toggle-switch">
                        <input type="checkbox" name="is_admin" value="1" {% if user_data.is_admin %}checked{% endif %}>
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">Grant admin privileges</span>
                </div>
            </div>
        </div>

        <div class="btn-group" style="margin-top:8px;">
            <button type="submit" class="btn btn-primary">Save Changes</button>
            <a href="/admin/users" class="btn btn-outline">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 3: Write admin_diaries.html**

```html
{% extends "base.html" %}
{% block title %}All Diaries — Admin{% endblock %}
{% block content %}
<div class="page-header">
    <h1>All Diaries</h1>
</div>

<div class="filter-bar">
    <select class="form-select" name="month" id="filterMonth">
        <option value="">All Months</option>
        {% for m in range(1,13) %}
        <option value="{{ m }}">{{ m }}</option>
        {% endfor %}
    </select>
    <input class="form-input" type="number" name="year" id="filterYear" placeholder="Year" value="2026" style="width:100px;">
    <select class="form-select" name="status" id="filterStatus">
        <option value="">All Status</option>
        <option value="draft">Draft</option>
        <option value="submitted">Submitted</option>
        <option value="reviewed">Reviewed</option>
    </select>
    <button class="btn btn-primary btn-sm" onclick="applyFilters()">Filter</button>
</div>

{% if diaries %}
<div class="table-wrapper">
    <table class="table-modern">
        <thead>
            <tr>
                <th>Staff</th>
                <th>Month</th>
                <th>Year</th>
                <th>Status</th>
                <th>Total</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for d in diaries %}
            <tr class="table-row-animate">
                <td><strong>{{ d.staff_no }}</strong> {{ d.name }}</td>
                <td>{{ d.month_name }}</td>
                <td>{{ d.year }}</td>
                <td><span class="badge badge-{{ d.status }}">{{ d.status }}</span></td>
                <td><strong>&#8377; {{ "%.2f"|format(d.grand_total or 0) }}</strong></td>
                <td>
                    <div class="flex gap-1">
                        <a href="/attendance/calendar/{{ d.id }}" class="btn btn-ghost btn-sm">View</a>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#128203;</div>
    <div class="empty-state-title">No diaries found</div>
    <div class="empty-state-text">No diaries match the current filters.</div>
</div>
{% endif %}

<script>
function applyFilters() {
    const month = document.getElementById('filterMonth').value;
    const year = document.getElementById('filterYear').value;
    const status = document.getElementById('filterStatus').value;
    const params = new URLSearchParams();
    if (month) params.set('month', month);
    if (year) params.set('year', year);
    if (status) params.set('status', status);
    window.location.href = '/admin/diaries?' + params.toString();
}
</script>
{% endblock %}
```

- [ ] **Step 4: Write admin_links.html**

```html
{% extends "base.html" %}
{% block title %}Linked Accounts — Admin{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Google Linked Accounts</h1>
</div>

{% if links %}
<div class="table-wrapper">
    <table class="table-modern">
        <thead>
            <tr>
                <th>Google UID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Staff No</th>
                <th>Linked At</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for l in links %}
            <tr class="table-row-animate">
                <td><span class="text-small text-secondary">{{ l.google_uid[:16] }}...</span></td>
                <td>{{ l.name or '—' }}</td>
                <td>{{ l.email or '—' }}</td>
                <td><strong>{{ l.staff_no }}</strong></td>
                <td><span class="text-small text-secondary">{{ l.linked_at }}</span></td>
                <td>
                    <form method="POST" action="/admin/links/unlink/{{ l.id }}" onsubmit="return confirm('Unlink this Google account?')">
                        <button type="submit" class="btn btn-danger btn-sm">Unlink</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#8861;</div>
    <div class="empty-state-title">No linked accounts</div>
    <div class="empty-state-text">No Google accounts have been linked yet.</div>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Write admin_holidays.html**

```html
{% extends "base.html" %}
{% block title %}Holiday Calendar — Admin{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Holiday Calendar</h1>
    <div class="page-header-actions">
        <button class="btn btn-primary btn-sm" onclick="toggleAddForm()">+ Add Holiday</button>
        <form method="POST" action="/admin/holidays/refresh" style="display:inline;">
            <button type="submit" class="btn btn-secondary btn-sm">Refresh from RBI</button>
        </form>
    </div>
</div>

<!-- Add Holiday Form (hidden by default) -->
<div id="addHolidayForm" style="display:none;">
    <div class="card mb-5">
        <h3>Add Holiday</h3>
        <form method="POST" action="/admin/holidays/add">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Date</label>
                    <input class="form-input" type="date" name="holiday_date" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input class="form-input" type="text" name="description" required placeholder="e.g. Diwali">
                </div>
                <div class="form-group">
                    <label class="form-label">State</label>
                    <select class="form-select" name="state" required>
                        <option value="All India">All India</option>
                        <option value="Andhra Pradesh">Andhra Pradesh</option>
                        <option value="Karnataka">Karnataka</option>
                        <option value="Kerala">Kerala</option>
                        <option value="Tamil Nadu">Tamil Nadu</option>
                        <option value="Telangana">Telangana</option>
                        <option value="Maharashtra">Maharashtra</option>
                        <option value="Delhi">Delhi</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Type</label>
                    <select class="form-select" name="holiday_type">
                        <option value="RBI">RBI Holiday</option>
                        <option value="Bank">Bank Holiday</option>
                        <option value="Optional">Optional</option>
                    </select>
                </div>
            </div>
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">Save Holiday</button>
                <button type="button" class="btn btn-outline" onclick="toggleAddForm()">Cancel</button>
            </div>
        </form>
    </div>
</div>

<!-- Filter Bar -->
<div class="filter-bar">
    <label class="form-label" style="margin:0;text-transform:none;letter-spacing:0;">State</label>
    <select class="form-select" id="filterHolidayState" onchange="applyHolidayFilter()">
        <option value="">All States</option>
        <option value="All India">All India</option>
        <option value="Karnataka">Karnataka</option>
        <option value="Andhra Pradesh">Andhra Pradesh</option>
        <option value="Kerala">Kerala</option>
        <option value="Tamil Nadu">Tamil Nadu</option>
        <option value="Telangana">Telangana</option>
        <option value="Maharashtra">Maharashtra</option>
        <option value="Delhi">Delhi</option>
    </select>
    <label class="form-label" style="margin:0;text-transform:none;letter-spacing:0;">Year</label>
    <input class="form-input" type="number" id="filterHolidayYear" value="2026" style="width:100px;" onchange="applyHolidayFilter()">
    <button class="btn btn-primary btn-sm" onclick="applyHolidayFilter()">Apply</button>
</div>

{% if holidays %}
<div class="table-wrapper">
    <table class="table-modern" id="holidaysTable">
        <thead>
            <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Description</th>
                <th>State</th>
                <th>Type</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for h in holidays %}
            <tr class="table-row-animate">
                <td>{{ h.holiday_date }}</td>
                <td>{{ h.day_name or '—' }}</td>
                <td>{{ h.description }}</td>
                <td>{{ h.state }}</td>
                <td><span class="badge badge-holiday">{{ h.holiday_type }}</span></td>
                <td>
                    <form method="POST" action="/admin/holidays/delete/{{ h.id }}" style="display:inline;" onsubmit="return confirm('Delete this holiday?')">
                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#127774;</div>
    <div class="empty-state-title">No holidays found</div>
    <div class="empty-state-text">No holidays match the current filters. Click "Refresh from RBI" to load the latest holidays.</div>
</div>
{% endif %}

<script>
function toggleAddForm() {
    const form = document.getElementById('addHolidayForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}
function applyHolidayFilter() {
    const state = document.getElementById('filterHolidayState').value;
    const year = document.getElementById('filterHolidayYear').value;
    const params = new URLSearchParams();
    if (state) params.set('state', state);
    if (year) params.set('year', year);
    window.location.href = '/admin/holidays?' + params.toString();
}
</script>
{% endblock %}
```

- [ ] **Step 6: Write all five admin files**

Write to each respective path.

---

### Task 10: Profile + Upload + Remaining Pages

**Files:**
- Rewrite: `templates/profile.html`
- Rewrite: `templates/profile_edit.html`
- Rewrite: `templates/upload_whatsapp.html`
- Rewrite: `templates/upload_bill.html`
- Rewrite: `templates/edit_diary.html`
- Rewrite: `templates/holidays.html`

- [ ] **Step 1: Write profile.html**

```html
{% extends "base.html" %}
{% block title %}Profile — {{ user.name }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Profile</h1>
</div>

<div class="card" style="max-width:600px;margin:0 auto;">
    <div class="text-center mb-5">
        <div class="sidebar-user-avatar" style="width:64px;height:64px;font-size:1.5rem;margin:0 auto 12px;">{{ user.name[:1] }}</div>
        <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:600;">{{ user.name }}</div>
        {% if user.is_admin %}
        <span class="badge badge-admin badge-lg" style="margin-top:4px;">Admin</span>
        {% endif %}
    </div>

    <div class="info-grid" style="grid-template-columns:1fr 1fr;">
        <div class="info-item"><span class="info-label">Staff No</span><span class="info-value">{{ user.staff_no }}</span></div>
        <div class="info-item"><span class="info-label">Designation</span><span class="info-value">{{ user.designation or '—' }}</span></div>
        <div class="info-item"><span class="info-label">DP Code</span><span class="info-value">{{ user.dp_code or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Section</span><span class="info-value">{{ user.section or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Zone</span><span class="info-value">{{ user.zone or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Basic Pay</span><span class="info-value">{{ user.basic_pay or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Home State</span><span class="info-value">{{ user.home_state or '—' }}</span></div>
        <div class="info-item"><span class="info-label">City Category</span><span class="info-value">{{ user.city_category or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Email</span><span class="info-value">{{ user.email or '—' }}</span></div>
        <div class="info-item"><span class="info-label">Mobile</span><span class="info-value">{{ user.mobile or '—' }}</span></div>
    </div>

    <div class="text-center" style="margin-top:24px;">
        <a href="/auth/profile/edit" class="btn btn-primary">Edit Profile</a>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Write profile_edit.html**

Same structure as profile.html but with `form-input` fields instead of read-only values, form action to `POST /auth/profile/edit`, and Save/Cancel buttons.

- [ ] **Step 3: Write upload_whatsapp.html**

```html
{% extends "base.html" %}
{% block title %}Import WhatsApp — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Import WhatsApp Attendance</h1>
    <div class="page-header-actions">
        <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Back</a>
    </div>
</div>

<div class="card">
    <p class="text-body text-secondary mb-4">Upload an exported WhatsApp chat <strong>.txt</strong> file to automatically parse attendance records. The system will match senders by staff number or name.</p>

    <form method="POST" action="/attendance/upload-whatsapp/{{ diary.id }}" enctype="multipart/form-data">
        <div class="form-group">
            <label class="form-label">Chat File</label>
            <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                <div class="dropzone-icon">&#128172;</div>
                <div class="dropzone-text">Drag &amp; drop or <strong>click to browse</strong></div>
                <div class="dropzone-filename" id="fileName" style="display:none;"></div>
            </div>
            <input type="file" name="chat_file" id="fileInput" accept=".txt" style="display:none;" onchange="handleFileSelect(event)">
        </div>
        <button type="submit" class="btn btn-primary" id="importBtn" disabled>Import Chat</button>
    </form>
</div>

<script>
function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileName = document.getElementById('fileName');
    const importBtn = document.getElementById('importBtn');
    const dropzone = document.getElementById('dropzone');

    if (file) {
        fileName.textContent = file.name;
        fileName.style.display = 'block';
        importBtn.disabled = false;
        dropzone.classList.add('drag-over');
    }
}

// Drag and drop handlers
const dropzone = document.getElementById('dropzone');
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
});
dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('drag-over');
});
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
        document.getElementById('fileInput').files = e.dataTransfer.files;
        handleFileSelect({ target: { files: [file] } });
    }
});
</script>
{% endblock %}
```

- [ ] **Step 4: Write upload_bill.html**

Same structure as upload_whatsapp.html but with added form fields for vendor, amount, date. The file input accepts images (`accept="image/*"`). Add OCR hint text.

- [ ] **Step 5: Write edit_diary.html**

```html
{% extends "base.html" %}
{% block title %}Edit Diary — {{ diary.month_name }} {{ diary.year }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Edit Diary</h1>
    <div class="page-header-actions">
        <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline btn-sm">&larr; Back to Calendar</a>
    </div>
</div>

<div class="card">
    <form method="POST" action="/attendance/edit-diary/{{ diary.id }}">
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Bank State</label>
                <select class="form-select" name="bank_state" required>
                    <option value="Andhra Pradesh" {% if diary.bank_state == 'Andhra Pradesh' %}selected{% endif %}>Andhra Pradesh</option>
                    <option value="Karnataka" {% if diary.bank_state == 'Karnataka' %}selected{% endif %}>Karnataka</option>
                    <option value="Kerala" {% if diary.bank_state == 'Kerala' %}selected{% endif %}>Kerala</option>
                    <option value="Tamil Nadu" {% if diary.bank_state == 'Tamil Nadu' %}selected{% endif %}>Tamil Nadu</option>
                    <option value="Telangana" {% if diary.bank_state == 'Telangana' %}selected{% endif %}>Telangana</option>
                    <option value="Maharashtra" {% if diary.bank_state == 'Maharashtra' %}selected{% endif %}>Maharashtra</option>
                    <option value="Delhi" {% if diary.bank_state == 'Delhi' %}selected{% endif %}>Delhi</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">GSTIN</label>
                <input class="form-input" type="text" name="gstin" value="{{ diary.gstin or '' }}" placeholder="e.g. 29AAAAA0000A1Z5">
            </div>
        </div>

        <div class="btn-group" style="margin-top:8px;">
            <button type="submit" class="btn btn-primary">Save Changes</button>
            <a href="/attendance/calendar/{{ diary.id }}" class="btn btn-outline">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 6: Write holidays.html**

```html
{% extends "base.html" %}
{% block title %}Holidays{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Holidays</h1>
</div>

<div class="filter-bar">
    <label class="form-label" style="margin:0;text-transform:none;letter-spacing:0;">State</label>
    <select class="form-select" id="holidayState" onchange="filterHolidays()">
        <option value="">All States</option>
        <option value="All India">All India</option>
        <option value="Karnataka">Karnataka</option>
        <option value="Andhra Pradesh">Andhra Pradesh</option>
        <option value="Kerala">Kerala</option>
        <option value="Tamil Nadu">Tamil Nadu</option>
        <option value="Telangana">Telangana</option>
        <option value="Maharashtra">Maharashtra</option>
        <option value="Delhi">Delhi</option>
    </select>
    <label class="form-label" style="margin:0;text-transform:none;letter-spacing:0;">Year</label>
    <input class="form-input" type="number" id="holidayYear" value="2026" style="width:100px;">
    <button class="btn btn-primary btn-sm" onclick="filterHolidays()">Apply</button>
</div>

{% if holidays %}
<div class="table-wrapper">
    <table class="table-modern">
        <thead>
            <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Description</th>
                <th>State</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
            {% for h in holidays %}
            <tr class="table-row-animate">
                <td>{{ h.holiday_date }}</td>
                <td>{{ h.day_name }}</td>
                <td>{{ h.description }}</td>
                <td>{{ h.state }}</td>
                <td><span class="badge badge-holiday">{{ h.holiday_type }}</span></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <div class="empty-state-icon">&#127774;</div>
    <div class="empty-state-title">No holidays</div>
    <div class="empty-state-text">No holidays found for the selected filters.</div>
</div>
{% endif %}

<script>
function filterHolidays() {
    const state = document.getElementById('holidayState').value;
    const year = document.getElementById('holidayYear').value;
    const params = new URLSearchParams();
    if (state) params.set('state', state);
    if (year) params.set('year', year);
    window.location.href = '/holidays?' + params.toString();
}
</script>
{% endblock %}
```

- [ ] **Step 7: Write all six files**

Write to each respective path.

---

### Task 11: Final Polish — Audit & Verify

- [ ] **Step 1: Audit all templates for old class names**

```bash
# Search for any remaining old Navy+Gold class names in templates
rg -n "pill-btn|card-audit|table-audit|form-audit|navbar-audit|btn-audit|bg-navy|color-gold|navy|--color-" C:\Users\nikhi\Desktop\AuditReport\templates\ --include "*.html"
```

If any found, replace them with the new equivalents per Appendix A in the spec.

- [ ] **Step 2: Audit style.css for old references**

```bash
# Check style.css has no old color tokens
rg -n "navy|gold|#0a1628|#d4a843|#6b7280|#e5e7eb|#16a34a|#dc2626|#4338ca" C:\Users\nikhi\Desktop\AuditReport\static\style.css
```

If any found, remove/replace them.

- [ ] **Step 3: Responsive visual check**

Load the app at these widths (use browser DevTools):
- **320px:** Sidebar hidden, hamburger visible, `.form-row` stacks to 1 column, calendar cells compact (55px min-height), cards full-width, tables scroll horizontally
- **768px:** Sidebar hidden (tablet), hamburger visible, 2-column grid still stacks to 1 column forms
- **1024px:** Sidebar visible (220px), standard layout, 2-column forms
- **1440px:** Sidebar visible, max-width container centered, generous padding

**Fix any layout issues found** — adjust CSS breakpoints or template classes as needed.

- [ ] **Step 4: Animation verification**

Check that:
- `.page-enter` animation plays on page load (main content slides up 12px + fades in)
- Card hover lifts 2px with shadow change
- Button hover scales to 1.02 with glow on primary
- Sidebar nav items have smooth background transition on hover
- Focus rings appear on form inputs (amber 3px outline)

- [ ] **Step 5: Accessibility check**

Verify:
- All text/background combos meet WCAG AA contrast. Key pairs to test:
  - `--accent-500` (#f59e0b) on white — passes for large text, check for small text
  - `--text-secondary` (#64748b) on `--bg-main` (#f8fafc) — check contrast
  - `--text-tertiary` (#94a3b8) on `--bg-surface` (#ffffff) — may fail AA, used only for placeholders/disabled
- Focus rings are visible on all interactive elements
- All `a` elements without href have `role="button"` if used as buttons

- [ ] **Step 6: Cross-browser check**

Load in Chrome, Firefox, Edge:
- Google Fonts load correctly (Outfit + Inter)
- CSS Grid calendar renders properly
- Flexbox layouts don't overflow
- No JS console errors

- [ ] **Step 7: Final old-file cleanup**

```bash
# Check for register.html — if no longer used, add a note or update it to match login styling
# Check holidays.html vs admin_holidays.html — both exist, ensure both use new classes
```

---

### Self-Review Checklist

After writing this plan, run through:

1. **Spec coverage:** Can I point to a task for every page listed in the spec?
   - CSS Foundation ✅ (Task 1 — complete style.css)
   - Base Template ✅ (Task 2 — sidebar layout, fonts)
   - Login + Setup ✅ (Task 3 — both auth pages)
   - Dashboard ✅ (Task 4 — card-based diary list)
   - Calendar + Attendance Add/Edit ✅ (Task 5 — 3 files)
   - Preview Diary ✅ (Task 6 — all expense sections)
   - Travel, Hotel, Local, Other, Bills lists ✅ (Task 7 — 5 files)
   - Travel/Hotel/Local/Other add+edit forms ✅ (Task 8 — 8 files)
   - Admin users, user edit, diaries, links, holidays ✅ (Task 9 — 5 files)
   - Profile, profile edit, WhatsApp upload, bill upload, edit diary, holidays ✅ (Task 10 — 6 files)
   - Final polish, audit, responsive check ✅ (Task 11)
   - **Total files modified: 1 CSS + 32 templates = 33 files** (matches actual file count)

2. **Placeholder scan:**
   - No "TBD", "TODO", "implement later" patterns
   - No "fill in details" or "appropriate error handling" without code
   - No "similar to X" without repeating the pattern
   - All CSS is complete inline code
   - All representative templates have complete HTML

3. **Type/class consistency:**
   - `.btn-primary`, `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-lg` — defined in Task 1, used in Tasks 2-10
   - `.card`, `.card-compact`, `.card-flat`, `.card-stat` — defined in Task 1, used in Tasks 4-10
   - `.form-input`, `.form-select`, `.form-textarea`, `.form-label`, `.form-group`, `.form-row` — defined in Task 1, used in Tasks 3-10
   - `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`, `.badge-holiday`, `.badge-draft`, `.badge-submitted`, `.badge-reviewed`, `.badge-admin` — defined in Task 1, used in Tasks 4-10
   - `.table-modern` — defined in Task 1, used in Tasks 6, 9, 10
   - `.empty-state`, `.empty-state-compact` — defined in Task 1, used in Tasks 4-10
   - `.sidebar`, `.sidebar-nav`, `.sidebar-brand`, `.sidebar-user` — defined in Task 1, used in Task 2
   - `.auth-page`, `.auth-card`, `.auth-header`, `.google-btn` — defined in Task 1, used in Task 3
   - `.calendar-grid`, `.calendar-cell`, `.legend`, `.mini-calendar` — defined in Task 1, used in Task 5, 6
   - `.diary-card`, `.expense-card`, `.page-header`, `.action-bar`, `.filter-bar`, `.dropzone` — defined in Task 1, used in relevant tasks

4. **Data field consistency:** Template field names (`r.from_place`, `r.to_place`, `r.amount`, etc.) match what the server-side models/Routers currently pass. If any field names differ from actual, the implementer should adjust during implementation.
