# Frontend Redesign Specification

## 1. Concept & Vision

A lightweight, professional API testing platform that feels clean and modern without being sterile. The interface should communicate competence and reliability — the kind of tool a senior QA engineer would trust. Visual clarity over visual richness; every pixel serves a purpose.

## 2. Design Language

### Aesthetic Direction
**"轻盈专业" (Light & Professional)** — Clean surfaces, generous whitespace, subtle depth through shadows rather than borders. The interface breathes without feeling empty.

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#6366f1` | Actions, active states, links |
| Primary Hover | `#4f46e5` | Hover states |
| Primary Light | `#e0e7ff` | Selected backgrounds, highlights |
| Success | `#10b981` | Pass status, success states |
| Success Light | `#d1fae5` | Success backgrounds |
| Warning | `#f59e0b` | Warning states |
| Warning Light | `#fef3c7` | Warning backgrounds |
| Danger | `#ef4444` | Fail status, errors, destructive |
| Danger Light | `#fee2e2` | Danger backgrounds |
| Background | `#f8fafc` | Page background (Slate-50) |
| Surface | `#ffffff` | Cards, panels |
| Border | `#e2e8f0` | Dividers, borders (Slate-200) |
| Text Primary | `#0f172a` | Headlines (Slate-900) |
| Text Secondary | `#64748b` | Secondary text (Slate-500) |
| Text Muted | `#94a3b8` | Placeholder, hints (Slate-400) |
| Sidebar BG | `#1e1e2d` | Sidebar background |
| Sidebar Text | `#e2e8f0` | Sidebar text |
| Sidebar Active | `#6366f1` | Active nav item accent |

### Typography

- **Font Family**: Inter, system-ui, sans-serif
- **Weights**: 400 (body), 500 (labels), 600 (headings), 700 (titles)
- **Scale**:
  - Page title: 24px / 700
  - Section title: 18px / 600
  - Body: 14px / 400
  - Small/Label: 12px / 500
  - Micro: 11px / 500

### Spatial System

- Base unit: 4px
- Component padding: 12px / 16px / 20px
- Card padding: 20px / 24px
- Page margin: 24px
- Gap between elements: 8px / 12px / 16px
- Border radius: 6px (inputs), 8px (buttons), 12px (cards), 16px (modals)

### Motion Philosophy

- **Fast transitions**: 150ms for hover states, micro-interactions
- **Normal transitions**: 200ms for panels, drawers
- **Page transitions**: 150ms fade
- Sidebar collapse: 200ms width animation
- All easing: `ease` or `ease-out` — never bounce or spring

### Visual Assets

- **Icons**: Element Plus built-in icons (consistent with Element UI ecosystem)
- **No decorative images** — functional only
- **HTTP Method badges**: Color-coded pills (GET=green, POST=blue, PUT=amber, DELETE=red, PATCH=violet)

## 3. Layout & Structure

### Shell Architecture
```
┌─────────────────────────────────────────────────────┐
│  Sidebar (64px collapsed / 220px expanded)  │ Header │
│  ┌─────┐                                         │  64px  │
│  │ Logo│  Navigation                             │────────│
│  ├─────┤  - 环境管理                              │        │
│  │ Nav │  - 接口管理                              │  Main  │
│  │Items│  - 测试用例                              │ Content│
│  │     │  - 系统管理 (admin)                       │        │
│  ├─────┤                                         │        │
│  │User │                                         │        │
│  │Card │                                         │        │
│  └─────┘                                         │        │
└─────────────────────────────────────────────────────┘
```

### Sidebar (Navigation)
- Dark background (`#1e1e2d`) for visual weight
- Logo at top: Icon + "AutoTest" text when expanded
- Navigation items: Icon + text, 44px height
- Active state: Left border accent (3px primary) + subtle bg tint
- Collapse toggle at bottom
- User info card at bottom (collapsed: avatar only, expanded: avatar + name)

### Header
- Height: 64px
- Left: Breadcrumb navigation
- Right: User dropdown (avatar, name, logout)
- Background: White with subtle bottom border

### Main Content Area
- Background: `#f8fafc`
- Content wrapped in white cards
- Consistent 24px padding

## 4. Page Layouts

### 4.1 Login / Register Pages
```
┌────────────────────────────────────────────────────┐
│                                                    │
│   ┌──────────────────┐  ┌───────────────────────┐  │
│   │                  │  │                       │  │
│   │   Brand Area     │  │     Form Area        │  │
│   │   - Logo         │  │     - Title          │  │
│   │   - Tagline      │  │     - Inputs         │  │
│   │   - Features     │  │     - Actions        │  │
│   │                  │  │     - Links          │  │
│   │   (Indigo grad)  │  │                       │  │
│   │                  │  │                       │  │
│   └──────────────────┘  └───────────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```
- Split layout: 50/50 on desktop, stacked on mobile
- Left: Indigo gradient background, white text, feature list
- Right: White card, centered form

### 4.2 API List Page (Three-Column)
```
┌──────────┬───────────────────────────┬───────────────┐
│ Module   │    Request Config         │   Response    │
│ Tree     │  ┌─────────────────────┐ │               │
│          │  │ Method │ Path      │ │  Status      │
│ ├ 用户   │  ├─────────────────────┤ │  Time         │
│ │  ├ GET │  │ Params  Headers   │ │  Size         │
│ │  └POST │  │ Body    Auth       │ │               │
│ └ 订单   │  │ Pre     Post       │ │  Body         │
│          │  └─────────────────────┘ │  Headers      │
│          │                          │  Assertions   │
│ [+ Module]│                         │               │
└──────────┴──────────────────────────┴───────────────┘
```
- Left sidebar (240px): Module tree, collapsible
- Center (flex): Request builder with tabs
- Right panel (400px min): Response viewer, collapsible

### 4.3 Environment / Test Case List Pages
```
┌──────────────────────────────────────────────────────┐
│  Header (title + actions)                            │
├──────────────────────────────────────────────────────┤
│  Toolbar (search + filters)                         │
├──────────────────────────────────────────────────────┤
│  Table                                              │
│  ┌────┬──────────┬──────┬───────┬────────┬──────┐ │
│  │ #  │ Name     │ Desc │ Status│ Updated│Action│ │
│  ├────┼──────────┼──────┼───────┼────────┼──────┤ │
│  │ 1  │ Env 1    │ ...  │ ●    │ 2h ago │ ••• │ │
│  │ 2  │ Env 2    │ ...  │ ○    │ 1d ago │ ••• │ │
│  └────┴──────────┴──────┴───────┴────────┴──────┘ │
├──────────────────────────────────────────────────────┤
│  Pagination                                         │
└──────────────────────────────────────────────────────┘
```
- Compact table with high information density
- Inline status indicators
- Row hover highlight
- Action dropdown on right

### 4.4 Test Case Detail Page
```
┌──────────────────────────────────────────────────────┐
│  Case Header (name, desc, variables, actions)         │
├─────────────────────┬────────────────────────────────┤
│  Steps Panel       │   Step Detail / Result         │
│  ┌───────────────┐ │                                │
│  │ 1. GET /user │ │  Request Config                 │
│  │ 2. POST /order│ │  - Method, URL                 │
│  │ 3. Assert     │ │  - Params, Headers, Body       │
│  │    └─ status  │ │                                │
│  │ + Add Step    │ │  Response (when executed)      │
│  └───────────────┘ │  - Status, Body, Assertions    │
└─────────────────────┴────────────────────────────────┘
```
- Left: Draggable step list (300px)
- Right: Step configuration or execution result

## 5. Component Specifications

### 5.1 Buttons

**Primary Button**
- Background: `#6366f1`
- Text: White
- Height: 36px (default), 32px (small), 40px (large)
- Padding: 0 16px
- Border radius: 8px
- Hover: `#4f46e5`
- Active: Scale 0.98

**Secondary Button**
- Background: White
- Border: 1px `#e2e8f0`
- Text: `#475569`
- Hover: Border `#6366f1`, text `#6366f1`

**Danger Button**
- Background: `#ef4444`
- Text: White
- Hover: `#dc2626`

**Ghost Button**
- Background: Transparent
- Text: `#64748b`
- Hover: Background `#f1f5f9`

### 5.2 Form Inputs
- Height: 36px
- Border: 1px `#e2e8f0`
- Border radius: 6px
- Focus: Border `#6366f1`, ring `rgba(99, 102, 241, 0.1)`
- Placeholder: `#94a3b8`

### 5.3 Tables
- Header: `#f8fafc` background, uppercase labels, 12px/500
- Row height: 52px
- Row hover: `#f8fafc` background
- Row border: 1px `#f1f5f9` bottom
- Cell padding: 16px vertical

### 5.4 Cards
- Background: White
- Border radius: 12px
- Shadow: `0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.04)`
- Padding: 20px / 24px

### 5.5 HTTP Method Badges
```
GET    → #d1fae5 bg, #065f46 text
POST   → #dbeafe bg, #1e40af text
PUT    → #fef3c7 bg, #92400e text
DELETE → #fee2e2 bg, #991b1b text
PATCH  → #ede9fe bg, #5b21b6 text
```
- Display: Uppercase, 11px, font-weight 600
- Padding: 4px 8px
- Border radius: 4px

### 5.6 Status Badges
```
Enabled  → #d1fae5 bg, #065f46 text
Disabled → #f1f5f9 bg, #64748b text
Passed   → #d1fae5 bg, #065f46 text
Failed   → #fee2e2 bg, #991b1b text
Pending  → #fef3c7 bg, #92400e text
```
- Pill shape (full radius)
- 12px font size

### 5.7 Navigation Items
- Height: 44px
- Icon: 20px, muted color
- Text: 14px, 500 weight
- Active: Primary color text, left border accent, subtle primary bg tint
- Hover: Slightly lighter background

### 5.8 Empty States
- Centered content
- Icon: 48px, muted color
- Title: 16px, 500 weight
- Description: 14px, muted
- Primary action button below

### 5.9 Modals / Dialogs
- Border radius: 16px
- Header: 20px padding, border bottom
- Body: 24px padding
- Footer: 20px padding, border top, right-aligned buttons

## 6. Technical Approach

### Stack (Unchanged)
- Vue 3 + Composition API
- TypeScript
- Element Plus (base components, customized)
- Tailwind CSS (utility classes)
- Pinia (state management)
- Vue Router

### Architecture Principles
- All pages in `src/views/`
- Reusable components in `src/components/`
- Global styles in `src/style.css` with CSS variables
- Element Plus components used as-is where possible
- Custom styles only where Element Plus doesn't support needed customization

### CSS Variable Usage
- All colors via CSS variables in `:root`
- Spacing tokens for consistent gaps
- Border radius tokens for consistent rounding
- Shadow tokens for consistent elevation

### Responsive Strategy
- Primary target: 1280px+
- Graceful degradation to 1024px
- Sidebar collapse below 1280px
- Below 1024px: hide optional panels, focus on core content
