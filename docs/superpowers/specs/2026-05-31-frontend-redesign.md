# Frontend Redesign: Audit Diary System

> **Theme:** Professional & Trustworthy (Navy + Gold)
> **Design Philosophy:** The 5 Pillars of Intentional UI (frontend-philosophy)

## Design Direction

**Theme:** Deep navy (`#0a1628`) + gold (`#d4a843`) — authoritative, clean, banking-grade feel. The app handles financial audit data (TA bills, GST, reimbursements), so the visual language should convey trust, precision, and professionalism.

### Color System

```css
/* Primary palette */
--color-navy-900: #0a1628;
--color-navy-800: #0f1b2d;
--color-navy-700: #1a2a44;
--color-navy-600: #253a5c;

/* Accent */
--color-gold:     #d4a843;
--color-gold-light: #f0dfb0;

/* Semantic */
--color-success:  #16a34a;
--color-success-bg: #dcfce7;
--color-warning:  #d97706;
--color-warning-bg: #fef9c3;
--color-danger:   #dc2626;
--color-danger-bg: #fef2f2;
--color-info:     #4338ca;
--color-info-bg:  #eef2ff;
--color-holiday:  #1e40af;
--color-holiday-bg: #dbeafe;

/* Neutrals */
--color-bg:      #f0f2f5;
--color-surface: #ffffff;
--color-text:    #0a1628;
--color-muted:   #6b7280;
--color-border:  #e5e7eb;
```

### Typography

- **Headings**: 'Inter' (Google Font) — weights 600, 700
- **Body**: 'Inter' (regular 400)
- **Small text**: 0.7rem–0.8rem for metadata, labels, stats
- **Scale**: 0.6rem (labels) / 0.75rem (table content) / 0.85rem (body) / 1.2rem (page titles)

Avoid system-ui fallback. Load Inter from Google Fonts CDN.

## Layout Architecture

### Base Template (`base.html`)

- **Navbar**: Dark navy (`#0a1628`), brand text in gold (`#d4a843`), user info on right
- **Mobile**: Hamburger collapse on small screens
- **Container**: Max-width 1200px, centered
- **Background**: `#f0f2f5` (light gray — reduces eye strain vs pure white)
- **Cards**: White surface with `border-radius: 12px`, subtle shadow (`0 2px 12px rgba(0,0,0,0.06)`)
- **Status badges**: Pill-style with colored backgrounds (not Bootstrap badges)

### Navigation Items

| Item | Access |
|------|--------|
| Dashboard, Holidays | All users |
| Users, All Diaries, Linked Accounts | Admin only (gated) |

## Page-by-Page Redesign

### 1. Login Page

- Centered card (max-width 400px) on dark gradient background (`linear-gradient(135deg, #0a1628, #1a2a44)`)
- Google sign-in button: navy background, white text, Google icon
- Subtle footer text: "Secured with Firebase Authentication"
- No navbar shown (user not logged in)

### 2. Dashboard (My Monthly Diaries)

**Current:** HTML table with action buttons in every row
**New:** Card-based list with visual status indicators

- Each diary is a **card** with:
  - Left border color-coded: gold=Draft, green=Submitted, blue=Reviewed
  - Month/Year + status badge
  - Grand total prominently displayed
  - Action buttons as **pill-style links** (not crowded buttons): Calendar, Excel, Preview, Edit, Delete
- "+ New Month" button: gold background on navy, or navy on white
- Empty state: friendly info card with illustration

### 3. Calendar View

**Current:** HTML `<table>` with fixed cell sizes
**New:** CSS Grid layout (7 columns) — responsive by nature

- Month header: large title + bank state/GSTIN/status info
- Action bar: "Add Manually" + "Preview" (always visible); Upload WhatsApp, Compute Leaves, Travel, Hotel, Local, Other, Bills (admin only — shown as pill buttons)
- Legend: color swatches with labels
- Day cells:
  - **Present**: green background (`#dcfce7`), green border (`#86efac`)
  - **Leave**: yellow background (`#fef9c3`), yellow border (`#fde047`)
  - **Holiday**: blue background (`#dbeafe`), blue border (`#93c5fd`)
  - **Weekend**: gray background (`#f1f5f9`), gray text
  - **Missing**: no background, dashed border
  - **Review**: orange background (`#fed7aa`)
  - Each cell shows: day number (bold), status label, branch name (truncated), Edit link
- Edit button inside cell: small pill, outlined

### 4. Add/Edit Attendance Form

- Two-column grid layout (single column on mobile)
- Inputs: rounded borders (`8px`), subtle focus ring (gold)
- Checkboxes for is_holiday/is_leave styled as toggle switches
- Save: navy button; Cancel: outline button
- Error state: red border on invalid fields

### 5. Preview Diary

- Staff info bar: white card with gold left border
- Sections as cards: Attendance, Travel, Hotels, Local & Other
- **Attendance** shown as mini calendar dots (colored squares arranged in a grid — one per day)
- Summary as 4 stat cards in a 2x2 grid (Travel, Lodging, Local+Other, Grand Total)
- Grand Total card: navy background with gold text
- Action buttons: Download TA Excel, Download HRMS Excel, Submit Diary

### 6. List Pages (Travel, Hotel, Local, Other, Bills)

- Page title + "Add New" button
- Data in cards (not tables) with key info displayed:
  - Travel: From → To, Mode, Amount, Date
  - Hotel: Hotel name, City, Check-in → Check-out, Amount
  - Local: From → To, Mode, Distance, Amount
- Edit/Delete as icon buttons on each card
- Mobile: cards stack vertically, full-width

### 7. Admin Pages (Users, All Diaries, Linked Accounts)

- Data tables with `border-radius: 8px`, striped rows, sticky headers
- Buttons: consistent pill style
- Filter/search at top where applicable
- Confirmation dialogs for destructive actions (unlink, delete)

### 8. Holiday Calendar

- Filter bar: State + Year dropdowns
- "Add Holiday" button triggers expandable form section
- Refresh from RBI button
- Table: Date, Day, Description, State, Type badge, Delete button
- Empty state: centered message

### 9. Profile Page

- Card with two-column info layout
- Fields: Staff No, Name, Designation, DP Code, Section, Zone, Basic Pay, Home State, City Category, Email, Mobile, Role
- Role badge: Admin (gold) / User (gray)

### 10. Setup Account Page

- Centered card on dark gradient background (matches login)
- Email shown (read-only)
- Staff Number + Mobile fields
- "Link & Continue" button

## Component Library

All reusable UI components should be defined as CSS classes in `static/style.css`:

### Buttons
```css
.btn-primary   { background: #0a1628; color: white; border-radius: 8px; padding: 8px 18px; }
.btn-outline   { background: white; color: #0a1628; border: 1px solid #0a1628; border-radius: 8px; }
.btn-success   { background: #dcfce7; color: #166534; border-radius: 8px; }
.btn-warning   { background: #fef9c3; color: #92400e; border-radius: 8px; }
.btn-danger    { background: #fef2f2; color: #991b1b; border-radius: 8px; }
.btn-info      { background: #eef2ff; color: #4338ca; border-radius: 8px; }
```

### Cards
```css
.card {
  background: white; border-radius: 12px; padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
```

### Status Badges
```css
.badge-draft     { background: #fef3c7; color: #92400e; }
.badge-submitted { background: #dcfce7; color: #166534; }
.badge-reviewed  { background: #eef2ff; color: #4338ca; }
```

### Status Borders (for card left border)
```css
.border-draft     { border-left: 4px solid #d4a843; }
.border-submitted { border-left: 4px solid #16a34a; }
.border-reviewed  { border-left: 4px solid #4338ca; }
```

### Calendar Grid
- Use CSS Grid: `grid-template-columns: repeat(7, 1fr)`
- Day cell: `border-radius: 8px; min-height: 65px; padding: 6px;`
- Responsive: on mobile, cells shrink but grid stays 7 columns

## Responsive Breakpoints

| Breakpoint | Layout Changes |
|------------|---------------|
| < 576px (phone) | Single column, stacked cards, smaller cells |
| 576–768px (tablet) | 2-column grids collapse, calendar cells compact |
| 768–992px (small desktop) | Standard layout |
| > 992px (large desktop) | Max-width 1200px container |

## Global Style Changes

1. **Google Fonts**: Add Inter via CDN in base.html
2. **CSS Reset/Base**: In style.css
   - `body { background: #f0f2f5; font-family: 'Inter', sans-serif; }`
   - All existing Bootstrap overrides removed or updated
3. **Animations**: 
   - Page entrance: subtle fade-in (`opacity 0 → 1` over 200ms)
   - Card hover: slight lift (`transform: translateY(-1px)`)
   - Calendar cell hover: `brightness(0.97)`
   - Button hover: `opacity: 0.9`
4. **Icons**: Use emoji/unicode instead of Bootstrap Icons (no CDN dependency). Or use inline SVG for key icons (Google, etc.)
5. **Shadows**: Consistent `box-shadow` values across all elevated elements

## Files to Modify

| File | Changes |
|------|---------|
| `static/style.css` | Complete rewrite — new color system, components, calendar grid |
| `templates/base.html` | Restructured navbar, Inter font, new color scheme |
| `templates/login.html` | Dark gradient background, refined card |
| `templates/dashboard.html` | Card-based diary list instead of table |
| `templates/calendar.html` | CSS Grid calendar, pill admin tools |
| `templates/add_attendance.html` | Two-column grid, modern inputs |
| `templates/edit_attendance.html` | Match add form styling |
| `templates/preview_diary.html` | Card sections, mini attendance grid, summary cards |
| `templates/list_travel.html` | Card-based list |
| `templates/list_hotels.html` | Card-based list |
| `templates/list_local.html` | Card-based list |
| `templates/list_other.html` | Card-based list |
| `templates/list_bills.html` | Card-based list |
| `templates/holidays.html` | Refined table + filter |
| `templates/profile.html` | Two-column layout |
| `templates/setup_account.html` | Dark gradient background, match login |
| `templates/admin_users.html` | Styled table |
| `templates/admin_diaries.html` | Styled table |
| `templates/add_travel.html` | Clean form styling |
| `templates/add_hotel.html` | Clean form styling |
| `templates/add_local.html` | Clean form styling |
| `templates/add_other.html` | Clean form styling |
| `templates/edit_travel.html` | Clean form styling |
| `templates/edit_hotel.html` | Clean form styling |
| `templates/edit_local.html` | Clean form styling |
| `templates/edit_other.html` | Clean form styling |
| `templates/upload_whatsapp.html` | Clean file upload |
| `templates/upload_bill.html` | Clean file upload |
| `templates/edit_diary.html` | Clean form styling |
| `templates/admin_links.html` | Styled table |
| `templates/register.html` | (may be unused after Google auth) |

## Implementation Order

1. **Phase 1**: CSS foundation (`style.css`) + base template (`base.html`) — establishes the design system
2. **Phase 2**: Login + Setup Account pages (first user-facing)
3. **Phase 3**: Dashboard (most visited page) + New Month modal
4. **Phase 4**: Calendar (core functionality) + Add/Edit Attendance
5. **Phase 5**: Preview + Generate pages (downloading, submission)
6. **Phase 6**: List pages (Travel, Hotel, Local, Other, Bills)
7. **Phase 7**: Form pages (Add/Edit for all expense types)
8. **Phase 8**: Admin pages (Users, Diaries, Links) + Holidays
9. **Phase 9**: Profile + remaining templates
10. **Phase 10**: Final polish — responsive testing, animations, consistency pass
