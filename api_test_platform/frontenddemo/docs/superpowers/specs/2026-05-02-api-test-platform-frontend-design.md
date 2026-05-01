# API Test Platform Frontend Design Spec

## Overview

A modern, lightweight API testing platform frontend with warm, approachable aesthetics. The design emphasizes clarity, ease of use, and a relaxed visual feel while maintaining professional functionality.

## Tech Stack

- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Element Plus (customized theme)
- **State Management**: Pinia
- **Router**: Vue Router
- **HTTP Client**: Axios

## Design Tokens

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| primary | #4A90A4 | Main actions, highlights |
| primary-light | #5BA3B8 | Hover states |
| primary-dark | #3A7A8A | Active states |
| bg-page | #F8FAFC | Page background |
| bg-sidebar | #FFFFFF | Sidebar background |
| bg-card | #FFFFFF | Card/container background |
| border | #E8ECF0 | Borders, dividers |
| text-primary | #2C3E50 | Headings, important text |
| text-secondary | #7F8C9A | Body text, labels |
| text-muted | #A0A8B0 | Placeholder, disabled |
| success | #52C41A | Success states, GET method |
| warning | #FFB84D | Warnings, PUT method |
| error | #FF6B6B | Errors, DELETE method |
| info | #4A90A4 | Info, POST method |

### Typography

- **Font Family**: "Inter", "PingFang SC", "-apple-system", sans-serif
- **Code Font**: "JetBrains Mono", "Fira Code", monospace
- **Heading**: 18-20px, weight 600
- **Body**: 14px, weight 400
- **Small**: 12-13px, weight 400

### Spacing & Radius

- **Base unit**: 8px
- **Card radius**: 12px
- **Button radius**: 8px
- **Input radius**: 6px

## Layout Structure

### Overall Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo + Global Search + User Menu          height:56px│
├────────┬────────────────────────────────────────────────────┤
│        │                                                     │
│ Sidebar│  Main Content Area                                 │
│        │                                                     │
│ 64px   │                                                     │
│(collapsed)│                                                  │
│        │                                                     │
│ 240px  │                                                     │
│(expanded)│                                                  │
│        │                                                     │
└────────┴────────────────────────────────────────────────────┘
```

### Sidebar Navigation

- **Collapsed width**: 64px (icon only)
- **Expanded width**: 240px (icon + text)
- **Toggle**: Click collapse button or hover reveal
- **Items**:
  - 环境管理 (Environment)
  - 接口管理 (API)
  - 测试用例 (Test Cases)
  - 分隔线
  - 设置 (Settings)

## Page Designs

### 1. 环境管理页面

**Layout**: Card grid layout
**Path**: `/environments`

**Components**:
- Header with "新建环境" button
- Card grid (3-4 columns responsive)
- Each card shows:
  - 环境名称
  - 默认/激活 badge
  - 变量数量
  - 服务数量
  - 创建时间
  - 操作按钮 (编辑/删除)

**Dialog**: 环境编辑弹窗
- 基本信息 (名称、描述)
- 服务列表 (可添加多个服务)
- 变量列表 (key-value with type)
- 服务器配置 (protocol, host, port, base_path)

### 2. 接口管理页面

**Layout**: Left tree + Right table
**Path**: `/apis`

**Components**:
- Left panel (240px): 模块树
  - 可展开/收起
  - 显示模块名称 + API数量
  - 支持右键菜单 (新建模块/API)
- Right panel: API表格
  - 列: 名称、方法、路径、状态、更新时间、操作
  - Method badges: GET(绿), POST(蓝), PUT(橙), DELETE(红)
  - Row actions: 调试、编辑、删除

**API详情/编辑**: 右侧滑出面板 (600px width)
- 基本信息 (名称、方法、路径、描述)
- 参数配置 (Path/Query/Header/Cookie)
- 请求体配置 (类型 + JSON编辑器)
- 前置/后置操作
- 断言配置
- 调试结果展示

### 3. 测试用例管理页面

**Layout**: Left tree + Right list + Slide panel
**Path**: `/testcases`

**Components**:
- Left panel (240px): 用例模块树
- Right panel: 用例列表 (卡片形式)
  - 用例名称
  - 优先级 (P0/P1/P2/P3)
  - 状态 (启用/禁用)
  - 步骤数量
  - 更新时间
- Edit panel: 从右侧滑出 (80% width)
  - 用例基本信息
  - 步骤列表 (拖拽排序)
  - 每个步骤: API选择、参数覆盖、断言、提取器
  - 支持条件步骤 (IF/FOR/WHILE)
  - 执行按钮

**执行结果**: 底部抽屉展示
- 执行进度
- 步骤结果列表
- 失败断言详情
- 提取变量快照

## Component Inventory

### Navigation Components

| Component | States | Behavior |
|-----------|--------|----------|
| SidebarItem | default, hover, active, collapsed | Click to navigate, tooltip when collapsed |
| CollapseToggle | expanded, collapsed | Toggle sidebar width |

### Data Display

| Component | States | Behavior |
|-----------|--------|----------|
| ApiMethodBadge | GET, POST, PUT, DELETE, PATCH | Color-coded method label |
| StatusBadge | enabled, disabled, draft | Colored status indicator |
| PriorityBadge | P0, P1, P2, P3 | Color-coded priority |
| DataTable | loading, empty, populated, error | Sortable, selectable rows |
| TreeNode | expanded, collapsed, selected | Click to expand/select |

### Form Components

| Component | States | Behavior |
|-----------|--------|----------|
| Input | default, focus, error, disabled | Validation feedback |
| Select | default, open, selected, disabled | Searchable dropdown |
| JsonEditor | default, error, readonly | Syntax highlighting |
| KeyValueEditor | default | Add/remove rows |

### Feedback Components

| Component | States | Behavior |
|-----------|--------|----------|
| Toast | success, error, warning, info | Auto-dismiss after 3s |
| Modal | open, closing | Click outside to close |
| Drawer | open, closing | Slide from right |
| Loading | spinner, skeleton | Show during async ops |

## State Management

### Stores

1. **useEnvironmentStore**
   - environments: Environment[]
   - currentEnvironment: Environment | null
   - actions: fetchEnvironments, createEnvironment, updateEnvironment, deleteEnvironment

2. **useApiStore**
   - apis: ApiDefinition[]
   - modules: ApiModule[]
   - currentApi: ApiDefinition | null
   - actions: fetchApis, fetchModules, createApi, updateApi, deleteApi, debugApi

3. **useTestCaseStore**
   - testCases: TestCase[]
   - modules: TestCaseModule[]
   - currentTestCase: TestCase | null
   - executionRecords: ExecutionRecord[]
   - actions: fetchTestCases, createTestCase, updateTestCase, deleteTestCase, executeTestCase

## API Integration

All API calls go through `/api/v1/*` endpoints:

- `GET /environments` - 获取环境列表
- `POST /environments` - 创建环境
- `PUT /environments/:id` - 更新环境
- `DELETE /environments/:id` - 删除环境
- `GET /api-management/apis` - 获取API列表
- `POST /api-management/apis` - 创建API
- `PUT /api-management/apis/:id` - 更新API
- `DELETE /api-management/apis/:id` - 删除API
- `POST /api-management/apis/:id/debug` - 调试API
- `GET /test-cases` - 获取测试用例列表
- `POST /test-cases` - 创建测试用例
- `PUT /test-cases/:id` - 更新测试用例
- `DELETE /test-cases/:id` - 删除测试用例
- `POST /test-cases/:id/execute` - 执行测试用例
- `GET /execution-records` - 获取执行记录

## File Structure

```
frontenddemo/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   ├── stores/
│   │   ├── environment.ts
│   │   ├── api.ts
│   │   └── testcase.ts
│   ├── api/
│   │   └── client.ts
│   ├── views/
│   │   ├── layout/
│   │   │   ├── MainLayout.vue
│   │   │   └── Sidebar.vue
│   │   ├── environment/
│   │   │   ├── EnvironmentList.vue
│   │   │   └── EnvironmentEdit.vue
│   │   ├── api/
│   │   │   ├── ApiList.vue
│   │   │   ├── ApiTree.vue
│   │   │   └── ApiEdit.vue
│   │   └── testcase/
│   │       ├── TestCaseList.vue
│   │       ├── TestCaseTree.vue
│   │       ├── TestCaseEdit.vue
│   │       └── TestCaseExecute.vue
│   ├── components/
│   │   ├── common/
│   │   │   ├── MethodBadge.vue
│   │   │   ├── StatusBadge.vue
│   │   │   └── PriorityBadge.vue
│   │   ├── layout/
│   │   │   ├── AppHeader.vue
│   │   │   └── AppSidebar.vue
│   │   └── forms/
│   │       ├── JsonEditor.vue
│   │       └── KeyValueEditor.vue
│   └── styles/
│       ├── variables.css
│       └── global.css
└── public/
```