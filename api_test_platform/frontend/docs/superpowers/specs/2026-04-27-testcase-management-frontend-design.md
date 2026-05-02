# 测试用例管理系统前端设计方案

> **注意：数据驱动功能已从系统中移除。** 文档中涉及数据驱动（DataSource、数据源配置、数据驱动执行）的内容已不再适用，功能由步骤级条件控制(if/for/while)替代。

## 文档信息
- **创建日期**: 2026-04-27
- **作者**: Frontend Architect
- **版本**: 1.0
- **状态**: 待审查

## 1. 项目概述

### 1.1 项目背景
测试用例管理系统是API测试平台的核心模块，用于管理测试用例的创建、编辑、执行和结果查看。前端需要与后端API集成，提供完整的用户界面和交互体验。

### 1.2 技术栈
- **前端框架**: Vue 3 + TypeScript + Composition API
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP请求**: Axios
- **构建工具**: Vite

### 1.3 开发策略
采用**渐进式开发**策略，分四个阶段交付：
1. **第一阶段**: 基础架构（API封装、Mock数据、路由配置）
2. **第二阶段**: 核心功能（列表页、详情页、CRUD操作）
3. **第三阶段**: 执行功能（执行对话框、执行记录）
4. **第四阶段**: 高级功能（数据驱动、定时执行、报告导出）

## 2. 整体架构设计

### 2.1 目录结构
```
frontend/src/
├── api/
│   ├── testcase.ts          # 测试用例API封装
│   ├── datasource.ts        # 数据源API封装
│   └── execution.ts         # 执行记录API封装
├── mock/
│   ├── testcase.ts          # 测试用例Mock数据
│   ├── datasource.ts        # 数据源Mock数据
│   └── execution.ts         # 执行记录Mock数据
├── stores/
│   └── testcase.ts          # 测试用例状态管理
├── types/
│   └── testcase.ts          # 类型定义（已存在，需补充）
├── views/
│   └── testcase/
│       ├── TestCaseList.vue          # 列表页
│       ├── TestCaseDetail.vue        # 详情页
│       └── components/
│           ├── TestCaseTree.vue      # 模块树组件
│           ├── StepEditor.vue        # 步骤编辑器
│           ├── DataSourceConfig.vue  # 数据源配置
│           ├── ExecutionDialog.vue   # 执行对话框
│           └── ExecutionReport.vue   # 执行记录组件
└── router/
    └── index.ts             # 路由配置（需更新）
```

### 2.2 技术架构

**前端技术栈：**
- Vue 3 + TypeScript + Composition API
- Element Plus UI组件库
- Pinia状态管理
- Vue Router路由管理
- Axios HTTP请求

**Mock数据方案：**
- 创建独立的Mock模块，模拟API响应
- 在API封装层添加Mock开关（`USE_MOCK`），便于切换
- Mock数据格式与后端API响应格式保持一致

**状态管理策略：**
- 使用Pinia管理测试用例列表、当前编辑的测试用例
- 执行记录使用独立的状态管理
- 数据源配置作为测试用例的一部分管理

### 2.3 开发阶段划分

**第一阶段：基础架构（预计1-2天）**
- API封装模块（testcase.ts、datasource.ts、execution.ts）
- Mock数据模块
- 基础类型定义补充
- 路由配置

**第二阶段：核心功能（预计3-4天）**
- 测试用例列表页（左右分栏布局）
- 测试用例详情页（标签页形式）
- 步骤编辑器（关联已有API）
- 基本的CRUD操作

**第三阶段：执行功能（预计2-3天）**
- 详情页执行功能
- 列表页批量执行
- 执行对话框（环境选择、参数配置）
- 执行记录查看

**第四阶段：高级功能（预计2-3天）**
- 数据源配置（CSV/JSON/数据库）
- 数据驱动执行
- 定时执行配置
- 执行报告导出

## 3. API封装和Mock数据设计

### 3.1 API封装设计

**文件：`frontend/src/api/testcase.ts`**

```typescript
import { http } from '@/utils/request'
import type { TestCase, TestCaseStep, TestCaseCreate, TestCaseUpdate, PaginatedResponse } from '@/types/testcase'

const TEAM_ID = 1
const USE_MOCK = true // Mock开关，生产环境设为false

// Mock数据导入
import { mockTestCases, mockTestCase } from '@/mock/testcase'

export const testCaseApi = {
  // 获取测试用例列表
  list(params?: {
    page?: number
    page_size?: number
    keyword?: string
    status?: string
    priority?: string
    module_id?: number
  }): Promise<PaginatedResponse<TestCase>> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCases.list(params))
    }
    return http.get(`/teams/${TEAM_ID}/test-cases`, { params })
  },

  // 获取测试用例详情
  get(id: number): Promise<TestCase> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.get(id))
    }
    return http.get(`/test-cases/${id}`)
  },

  // 创建测试用例
  create(data: TestCaseCreate): Promise<TestCase> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.create(data))
    }
    return http.post(`/teams/${TEAM_ID}/test-cases`, data)
  },

  // 更新测试用例
  update(id: number, data: TestCaseUpdate): Promise<TestCase> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.update(id, data))
    }
    return http.put(`/test-cases/${id}`, data)
  },

  // 删除测试用例
  delete(id: number): Promise<void> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.delete(id))
    }
    return http.delete(`/test-cases/${id}`)
  },

  // 复制测试用例
  copy(id: number): Promise<TestCase> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.copy(id))
    }
    return http.post(`/test-cases/${id}/copy`)
  },

  // 执行测试用例
  execute(id: number, data: ExecuteRequest): Promise<ExecutionRecord> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.execute(id, data))
    }
    return http.post(`/test-cases/${id}/execute`, data)
  },

  // 批量执行测试用例
  batchExecute(ids: number[], data: ExecuteRequest): Promise<ExecutionRecord[]> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.batchExecute(ids, data))
    }
    return http.post('/test-cases/batch-execute', { test_case_ids: ids, ...data })
  },

  // 跨团队复制检查
  checkCrossTeamCopy(id: number, targetTeamId: number): Promise<CrossTeamCopyCheck> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.checkCrossTeamCopy(id, targetTeamId))
    }
    return http.post(`/test-cases/${id}/check-copy`, null, { params: { target_team_id: targetTeamId } })
  },

  // 执行跨团队复制
  copyToTeam(id: number, targetTeamId: number, options?: any): Promise<{ success: boolean; message: string }> {
    if (USE_MOCK) {
      return Promise.resolve(mockTestCase.copyToTeam(id, targetTeamId, options))
    }
    return http.post(`/test-cases/${id}/copy-to-team`, { target_team_id: targetTeamId, copy_options: options })
  }
}
```

**文件：`frontend/src/api/datasource.ts`**

```typescript
import { http } from '@/utils/request'
import type { DataSource, DataSourceCreate, DataSourceUpdate } from '@/types/testcase'

const USE_MOCK = true

export const dataSourceApi = {
  // 获取数据源列表
  list(testCaseId: number): Promise<DataSource[]> {
    if (USE_MOCK) {
      return Promise.resolve(mockDataSource.list(testCaseId))
    }
    return http.get(`/test-cases/${testCaseId}/data-sources`)
  },

  // 创建数据源
  create(testCaseId: number, data: DataSourceCreate): Promise<DataSource> {
    if (USE_MOCK) {
      return Promise.resolve(mockDataSource.create(testCaseId, data))
    }
    return http.post(`/test-cases/${testCaseId}/data-sources`, data)
  },

  // 更新数据源
  update(id: number, data: DataSourceUpdate): Promise<DataSource> {
    if (USE_MOCK) {
      return Promise.resolve(mockDataSource.update(id, data))
    }
    return http.put(`/data-sources/${id}`, data)
  },

  // 删除数据源
  delete(id: number): Promise<void> {
    if (USE_MOCK) {
      return Promise.resolve(mockDataSource.delete(id))
    }
    return http.delete(`/data-sources/${id}`)
  },

  // 预览数据源
  preview(id: number): Promise<{ total_rows: number; columns: string[]; preview_data: any[] }> {
    if (USE_MOCK) {
      return Promise.resolve(mockDataSource.preview(id))
    }
    return http.get(`/data-sources/${id}/preview`)
  }
}
```

**文件：`frontend/src/api/execution.ts`**

```typescript
import { http } from '@/utils/request'
import type { ExecutionRecord, StepExecutionRecord, PaginatedResponse } from '@/types/testcase'

const USE_MOCK = true

export const executionApi = {
  // 获取测试用例的执行记录列表
  list(testCaseId: number, params?: {
    page?: number
    page_size?: number
    status?: string
    executor_id?: number
    start_date?: string
    end_date?: string
  }): Promise<PaginatedResponse<ExecutionRecord>> {
    if (USE_MOCK) {
      return Promise.resolve(mockExecution.list(testCaseId, params))
    }
    return http.get(`/test-cases/${testCaseId}/executions`, { params })
  },

  // 获取执行记录详情
  getDetail(executionId: number): Promise<ExecutionRecord & { steps: StepExecutionRecord[] }> {
    if (USE_MOCK) {
      return Promise.resolve(mockExecution.getDetail(executionId))
    }
    return http.get(`/executions/${executionId}`)
  },

  // 导出执行报告
  exportReport(executionId: number, format: 'html' | 'excel' = 'html'): Promise<Blob> {
    if (USE_MOCK) {
      return Promise.resolve(mockExecution.exportReport(executionId, format))
    }
    return http.get(`/executions/${executionId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // 获取团队的执行记录列表
  listTeamExecutions(teamId: number, params?: {
    page?: number
    page_size?: number
    test_case_id?: number
    status?: string
    executor_id?: number
    start_date?: string
    end_date?: string
  }): Promise<PaginatedResponse<ExecutionRecord>> {
    if (USE_MOCK) {
      return Promise.resolve(mockExecution.listTeamExecutions(teamId, params))
    }
    return http.get(`/teams/${teamId}/executions`, { params })
  }
}
```

### 3.2 Mock数据设计

**文件：`frontend/src/mock/testcase.ts`**

Mock数据模块提供完整的测试数据，包括：
- 测试用例列表数据
- 测试用例详情数据
- 测试步骤数据
- 执行记录数据
- 跨团队复制检查数据

Mock数据格式与后端API响应格式完全一致，确保前端代码无需修改即可切换到真实API。

### 3.3 Mock数据优势

- **独立开发**：前端可以独立开发，不依赖后端API
- **快速验证**：可以快速验证UI和交互逻辑
- **易于切换**：通过`USE_MOCK`开关，轻松切换到真实API
- **数据一致**：Mock数据格式与后端API保持一致

## 4. 核心组件设计

### 4.1 测试用例列表页（TestCaseList.vue）

**页面布局：**
- 左侧面板（220px）：模块树导航、最近访问
- 右侧面板（flex: 1）：页面标题、工具栏、批量操作栏、测试用例表格、分页

**核心功能：**
- 左侧模块树导航
- 最近访问快速入口
- 列表展示（支持多选）
- 搜索和筛选（状态、优先级、标签）
- 批量操作（删除、移动、执行）
- 单个操作（查看、编辑、复制、删除、执行）

**关键特性：**
- 左右分栏布局，参考ApiList.vue的设计
- 支持拖拽调整左右面板宽度
- 响应式设计，小屏幕隐藏左侧面板
- 表格支持排序、筛选、多选

### 4.2 测试用例详情页（TestCaseDetail.vue）

**页面布局：**
- 页面标题栏：返回按钮、保存按钮、执行按钮
- 标签页：基本信息、测试步骤、数据源、执行记录

**核心功能：**
- 标签页切换（基本信息、测试步骤、数据源、执行记录）
- 基本信息编辑表单
- 测试步骤管理（拖拽排序、添加、删除、启用/禁用）
- 数据源配置（CSV/JSON/数据库）
- 执行记录查看

**关键特性：**
- 使用el-tabs组件实现标签页切换
- 表单验证和错误提示
- 自动保存草稿功能
- 步骤编辑器支持拖拽排序

### 4.3 步骤编辑器组件（StepEditor.vue）

**核心功能：**
- 步骤列表展示（可拖拽排序）
- 添加新步骤（关联已有API）
- 编辑步骤（覆盖API配置）
- 删除步骤
- 启用/禁用步骤

**关键特性：**
- 使用vuedraggable实现拖拽排序
- 步骤卡片式展示，清晰直观
- 支持快速启用/禁用步骤
- 步骤配置覆盖API默认配置

### 4.4 执行对话框组件（ExecutionDialog.vue）

**核心功能：**
- 选择执行环境
- 配置执行参数（失败策略、超时时间、步骤间隔）
- 选择数据源（数据驱动）
- 显示执行进度
- 执行完成后跳转到执行记录

**关键特性：**
- 模态对话框，支持单个或批量执行
- 实时显示执行进度
- 支持取消执行
- 执行完成后自动跳转到详情页

## 5. 状态管理和路由配置

### 5.1 状态管理设计

**文件：`frontend/src/stores/testcase.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { testCaseApi } from '@/api/testcase'
import type { TestCase, TestCaseCreate, TestCaseUpdate, TestCaseStep } from '@/types/testcase'

export const useTestCaseStore = defineStore('testcase', () => {
  // 状态
  const testCases = ref<TestCase[]>([])
  const currentTestCase = ref<TestCase | null>(null)
  const total = ref(0)
  const loading = ref(false)
  const modules = ref<TestCaseModule[]>([])

  // 计算属性
  const enabledTestCases = computed(() =>
    testCases.value.filter(tc => tc.status === 'enabled')
  )

  // 方法
  async function fetchTestCases(params?) { ... }
  async function fetchTestCase(id: number) { ... }
  async function createTestCase(data: TestCaseCreate) { ... }
  async function updateTestCase(id: number, data: TestCaseUpdate) { ... }
  async function deleteTestCase(id: number) { ... }
  async function copyTestCase(id: number) { ... }
  async function batchDeleteTestCases(ids: number[]) { ... }
  async function fetchModules() { ... }

  return {
    testCases,
    currentTestCase,
    total,
    loading,
    modules,
    enabledTestCases,
    fetchTestCases,
    fetchTestCase,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    copyTestCase,
    batchDeleteTestCases,
    fetchModules
  }
})
```

**状态管理策略：**
- **测试用例列表**：使用`testCases`数组存储列表数据
- **当前测试用例**：使用`currentTestCase`存储当前编辑的测试用例
- **模块树**：使用`modules`存储模块数据
- **加载状态**：使用`loading`控制加载状态
- **分页信息**：使用`total`存储总数

### 5.2 路由配置

**文件：`frontend/src/router/index.ts`（更新）**

新增路由：
- `/test-cases` - 测试用例列表
- `/test-cases/new` - 新建测试用例
- `/test-cases/:id` - 测试用例详情
- `/test-cases/:id/edit` - 编辑测试用例
- `/executions` - 执行记录列表
- `/executions/:id` - 执行记录详情

**路由设计说明：**
- 使用动态路由参数传递测试用例ID
- 路由元信息包含页面标题
- 路由守卫设置页面标题

### 5.3 导航菜单配置

**文件：`frontend/src/App.vue`（更新导航）**

新增菜单项：
- 测试用例
- 执行记录

**导航设计：**
- 水平导航菜单
- 根据当前路由高亮对应菜单项
- 支持子菜单展开

### 5.4 数据流设计

**数据流图：**
```
用户操作 → 组件 → Store → API → Mock/Backend
   ↓         ↓       ↓       ↓         ↓
 UI更新 ← 组件 ← Store ← API ← Mock/Backend
```

**典型数据流示例（创建测试用例）：**
1. 用户在`TestCaseDetail.vue`点击"保存"按钮
2. 组件调用`testCaseStore.createTestCase(formData)`
3. Store调用`testCaseApi.create(data)`
4. API根据`USE_MOCK`开关决定使用Mock或真实API
5. Mock/Backend返回新创建的测试用例数据
6. Store更新`testCases`数组和`total`
7. 组件自动更新UI（响应式）

## 6. 错误处理和测试策略

### 6.1 错误处理设计

**全局错误处理：**
- 响应拦截器处理常见HTTP错误（400、401、403、404、500）
- 统一错误提示（使用Element Plus的ElMessage）
- 错误日志记录

**组件级错误处理：**
- try-catch捕获异步错误
- finally块确保清理加载状态
- 表单验证错误提示

**表单验证错误处理：**
- 使用Element Plus的表单验证
- 自定义验证规则
- 实时验证和提交验证

### 6.2 加载状态管理

**全局加载状态：**
- 使用v-loading指令显示加载状态
- 加载文本提示

**按钮加载状态：**
- 使用:loading属性显示按钮加载状态
- 防止重复提交

### 6.3 测试策略

**单元测试：**
- 使用Vitest作为测试框架
- 测试API封装函数
- 测试Store的actions和getters
- 测试工具函数

**组件测试：**
- 使用@vue/test-utils测试组件
- 测试组件渲染和交互
- 测试组件状态变化

**E2E测试：**
- 使用Playwright进行端到端测试
- 测试用户完整操作流程
- 测试关键业务场景

### 6.4 性能优化策略

**列表优化：**
- 使用虚拟滚动处理大量数据
- 分页加载，避免一次性加载所有数据
- 使用`v-show`代替`v-if`频繁切换的元素

**组件优化：**
- 使用`computed`缓存计算结果
- 使用`watch`的`deep`选项谨慎
- 合理使用`v-memo`缓存渲染结果

**网络优化：**
- 使用防抖处理搜索输入
- 使用节流处理滚动事件
- 合理使用缓存策略

### 6.5 可访问性设计

**键盘导航：**
- 所有交互元素支持Tab键导航
- 使用`tabindex`属性控制焦点顺序
- 支持Enter键触发按钮点击

**ARIA属性：**
- 为图标按钮添加`aria-label`
- 为表单添加`aria-describedby`
- 为模态框添加`aria-modal`

## 7. 后端API协调事项

### 7.1 缺失的API

以下API需要后端实现：

**测试用例CRUD：**
- `GET /teams/{team_id}/test-cases` - 获取测试用例列表
- `POST /teams/{team_id}/test-cases` - 创建测试用例
- `PUT /test-cases/{test_case_id}` - 更新测试用例
- `DELETE /test-cases/{test_case_id}` - 删除测试用例
- `POST /test-cases/{test_case_id}/copy` - 复制测试用例

**测试用例执行：**
- `POST /test-cases/{test_case_id}/execute` - 执行测试用例
- `POST /test-cases/batch-execute` - 批量执行测试用例

**数据源管理：**
- `GET /test-cases/{test_case_id}/data-sources` - 获取数据源列表
- `POST /test-cases/{test_case_id}/data-sources` - 创建数据源
- `PUT /data-sources/{data_source_id}` - 更新数据源
- `DELETE /data-sources/{data_source_id}` - 删除数据源
- `GET /data-sources/{data_source_id}/preview` - 预览数据源

**模块管理：**
- `GET /teams/{team_id}/test-case-modules` - 获取测试用例模块列表
- `POST /teams/{team_id}/test-case-modules` - 创建测试用例模块
- `PUT /test-case-modules/{module_id}` - 更新测试用例模块
- `DELETE /test-case-modules/{module_id}` - 删除测试用例模块

### 7.2 API响应格式要求

所有API响应应遵循以下格式：

**列表响应：**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

**单个资源响应：**
```json
{
  "id": 1,
  "name": "测试用例名称",
  ...
}
```

**错误响应：**
```json
{
  "detail": "错误信息"
}
```

### 7.3 API接口文档

建议后端提供完整的API接口文档，包括：
- 请求方法和路径
- 请求参数和请求体
- 响应格式和状态码
- 错误码说明

## 8. 待完成功能清单

### 8.1 第一阶段：基础架构

- [ ] 创建API封装模块
  - [ ] testcase.ts
  - [ ] datasource.ts
  - [ ] execution.ts
- [ ] 创建Mock数据模块
  - [ ] testcase.ts
  - [ ] datasource.ts
  - [ ] execution.ts
- [ ] 补充类型定义
- [ ] 更新路由配置

### 8.2 第二阶段：核心功能

- [ ] 测试用例列表页
  - [ ] 页面布局
  - [ ] 模块树组件
  - [ ] 列表展示
  - [ ] 搜索和筛选
  - [ ] 批量操作
- [ ] 测试用例详情页
  - [ ] 页面布局
  - [ ] 基本信息编辑
  - [ ] 步骤编辑器
- [ ] 基本CRUD操作
  - [ ] 创建测试用例
  - [ ] 更新测试用例
  - [ ] 删除测试用例
  - [ ] 复制测试用例

### 8.3 第三阶段：执行功能

- [ ] 执行对话框组件
  - [ ] 环境选择
  - [ ] 参数配置
  - [ ] 执行进度显示
- [ ] 详情页执行功能
- [ ] 列表页批量执行
- [ ] 执行记录查看

### 8.4 第四阶段：高级功能

- [ ] 数据源配置
  - [ ] CSV数据源
  - [ ] JSON数据源
  - [ ] 数据库数据源
- [ ] 数据驱动执行
- [ ] 定时执行配置
- [ ] 执行报告导出

## 9. 风险和注意事项

### 9.1 技术风险

- **Mock数据维护**：需要确保Mock数据与后端API格式一致
- **状态管理复杂度**：测试用例包含步骤、数据源等嵌套数据，状态管理较复杂
- **性能问题**：大量测试用例和执行记录可能导致性能问题

### 9.2 协作风险

- **后端API延迟**：后端API实现可能延迟，影响前端开发进度
- **需求变更**：需求可能在开发过程中变更，需要灵活调整
- **接口不匹配**：前端Mock数据与后端实际API可能存在差异

### 9.3 缓解措施

- **Mock数据管理**：建立Mock数据管理规范，定期与后端对齐
- **模块化设计**：采用模块化设计，降低耦合度，便于调整
- **性能优化**：提前规划性能优化策略，使用虚拟滚动等技术
- **沟通机制**：建立前后端沟通机制，定期同步进度和问题

## 10. 总结

本设计方案采用渐进式开发策略，分四个阶段交付测试用例管理系统的前端功能。通过Mock数据实现前端独立开发，降低对后端API的依赖。设计方案遵循现有代码风格和组件模式，确保代码质量和可维护性。

关键设计决策：
1. 使用Mock数据实现前端独立开发
2. 采用左右分栏布局的列表页设计
3. 使用标签页形式的详情页设计
4. 步骤编辑器关联已有API
5. 支持多种执行场景（详情页执行、批量执行、定时执行、数据驱动执行）

下一步工作：
1. 审查本设计文档
2. 创建详细的实施计划
3. 开始第一阶段的开发工作
