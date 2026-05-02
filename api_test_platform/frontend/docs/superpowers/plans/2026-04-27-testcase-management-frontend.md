# 测试用例管理系统前端实施计划

> **注意：数据驱动功能已从系统中移除。** 文档中涉及数据驱动（DataSource、数据源配置、数据驱动执行）的内容已不再适用，功能由步骤级条件控制(if/for/while)替代。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的测试用例管理系统前端，包括测试用例的创建、编辑、执行和结果查看功能。

**Architecture:** 采用Vue 3 Composition API + TypeScript + Element Plus + Pinia架构，使用Mock数据实现前端独立开发，分四个阶段渐进式交付。

**Tech Stack:** Vue 3, TypeScript, Element Plus, Pinia, Vue Router, Axios, Vuedraggable

---

## 阶段一：基础架构（预计1-2天）

### Task 1: 补充TypeScript类型定义

**Files:**
- Modify: `frontend/src/types/testcase.ts`

- [ ] **Step 1: 添加缺失的类型定义**

在 `frontend/src/types/testcase.ts` 文件末尾添加以下类型定义：

```typescript
// 测试用例模块
export interface TestCaseModule {
  id: number
  team_id: number
  name: string
  parent_id: number | null
  description: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

// 测试用例创建请求
export interface TestCaseCreate {
  name: string
  module_id?: number | null
  description?: string | null
  status?: 'enabled' | 'disabled'
  priority?: 'P0' | 'P1' | 'P2' | 'P3'
  tags?: string[] | null
  variables?: any[] | null
  execution_condition?: Record<string, any> | null
  steps?: TestCaseStepCreate[] | null
}

// 测试用例更新请求
export interface TestCaseUpdate {
  name?: string
  module_id?: number | null
  description?: string | null
  status?: 'enabled' | 'disabled'
  priority?: 'P0' | 'P1' | 'P2' | 'P3'
  tags?: string[] | null
  variables?: any[] | null
  execution_condition?: Record<string, any> | null
  steps?: TestCaseStepCreate[] | null
}

// 测试步骤创建请求
export interface TestCaseStepCreate {
  api_id: number
  step_name?: string | null
  sort_order?: number
  enabled?: boolean
  override_headers?: Record<string, any> | null
  override_params?: Record<string, any> | null
  override_body?: string | null
  override_body_type?: string | null
  override_cookies?: any[] | null
  assertions?: any[] | null
  extractors?: any[] | null
  pre_script?: string | null
  post_script?: string | null
  timeout_config?: Record<string, any> | null
  execution_condition?: Record<string, any> | null
}

// 数据源创建请求
export interface DataSourceCreate {
  name: string
  source_type: 'csv' | 'json' | 'database'
  source_config: Record<string, any>
  enabled?: boolean
  iteration_mode?: 'sequential' | 'random'
}

// 数据源更新请求
export interface DataSourceUpdate {
  name?: string
  source_type?: 'csv' | 'json' | 'database'
  source_config?: Record<string, any>
  enabled?: boolean
  iteration_mode?: 'sequential' | 'random'
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
```

- [ ] **Step 2: 验证类型定义**

运行TypeScript编译器检查类型定义是否正确：

```bash
cd f:\AutoTest\api_test_platform\frontend
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: 提交类型定义**

```bash
git add src/types/testcase.ts
git commit -m "feat: 补充测试用例类型定义"
```

### Task 2: 创建测试用例Mock数据

**Files:**
- Create: `frontend/src/mock/testcase.ts`

- [ ] **Step 1: 创建Mock数据文件**

创建文件 `frontend/src/mock/testcase.ts`：

```typescript
import type { TestCase, TestCaseCreate, TestCaseUpdate, TestCaseStep, PaginatedResponse, ExecuteRequest, ExecutionRecord, CrossTeamCopyCheck } from '@/types/testcase'

// 模拟测试用例数据
const mockTestCasesData: TestCase[] = [
  {
    id: 1,
    team_id: 1,
    name: '用户登录测试',
    module_id: 1,
    description: '测试用户登录功能，验证登录成功和失败场景',
    status: 'enabled',
    priority: 'P0',
    tags: ['登录', '认证', 'P0'],
    variables: [
      { name: 'username', value: 'admin' },
      { name: 'password', value: '123456' }
    ],
    execution_condition: null,
    created_by: 1,
    created_at: '2024-01-15T10:00:00',
    updated_at: '2024-01-15T10:00:00',
    steps: [
      {
        id: 1,
        test_case_id: 1,
        api_id: 1,
        step_name: '发送登录请求',
        sort_order: 1,
        enabled: true,
        override_headers: { 'Content-Type': 'application/json' },
        override_params: null,
        override_body: '{"username":"{{username}}","password":"{{password}}"}',
        override_body_type: 'json',
        override_cookies: null,
        assertions: [
          { type: 'status_code', expected: 200, description: '验证状态码为200' },
          { type: 'response_time', expected: 1000, description: '验证响应时间小于1秒' }
        ],
        extractors: [
          { name: 'token', type: 'jsonpath', expression: '$.data.token', description: '提取token' }
        ],
        pre_script: null,
        post_script: null,
        timeout_config: { connect: 5000, read: 10000 },
        execution_condition: null,
        created_at: '2024-01-15T10:00:00',
        updated_at: '2024-01-15T10:00:00'
      }
    ]
  },
  {
    id: 2,
    team_id: 1,
    name: '用户注册测试',
    module_id: 1,
    description: '测试用户注册功能',
    status: 'enabled',
    priority: 'P1',
    tags: ['注册', '认证'],
    variables: [],
    execution_condition: null,
    created_by: 1,
    created_at: '2024-01-16T14:30:00',
    updated_at: '2024-01-16T14:30:00',
    steps: []
  },
  {
    id: 3,
    team_id: 1,
    name: '获取用户列表测试',
    module_id: 2,
    description: '测试获取用户列表接口',
    status: 'disabled',
    priority: 'P2',
    tags: ['用户管理'],
    variables: [],
    execution_condition: null,
    created_by: 1,
    created_at: '2024-01-17T09:15:00',
    updated_at: '2024-01-17T09:15:00',
    steps: []
  }
]

// 模拟模块数据
const mockModulesData = [
  { id: 1, team_id: 1, name: '认证模块', parent_id: null, description: '用户认证相关测试', sort_order: 1, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 2, team_id: 1, name: '用户管理模块', parent_id: null, description: '用户管理相关测试', sort_order: 2, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 3, team_id: 1, name: '订单模块', parent_id: null, description: '订单相关测试', sort_order: 3, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' }
]

let nextId = 4

export const mockTestCases = {
  list(params?: {
    page?: number
    page_size?: number
    keyword?: string
    status?: string
    priority?: string
    module_id?: number
  }): PaginatedResponse<TestCase> {
    let filtered = [...mockTestCasesData]

    if (params?.keyword) {
      filtered = filtered.filter(tc =>
        tc.name.includes(params.keyword!) ||
        tc.description?.includes(params.keyword!)
      )
    }

    if (params?.status) {
      filtered = filtered.filter(tc => tc.status === params.status)
    }

    if (params?.priority) {
      filtered = filtered.filter(tc => tc.priority === params.priority)
    }

    if (params?.module_id) {
      filtered = filtered.filter(tc => tc.module_id === params.module_id)
    }

    const page = params?.page || 1
    const pageSize = params?.page_size || 20
    const start = (page - 1) * pageSize
    const end = start + pageSize

    return {
      items: filtered.slice(start, end),
      total: filtered.length,
      page,
      page_size: pageSize
    }
  }
}

export const mockTestCase = {
  get(id: number): TestCase {
    const testCase = mockTestCasesData.find(tc => tc.id === id)
    if (!testCase) {
      throw new Error('Test case not found')
    }
    return testCase
  },

  create(data: TestCaseCreate): TestCase {
    const newTestCase: TestCase = {
      id: nextId++,
      team_id: 1,
      name: data.name,
      module_id: data.module_id || null,
      description: data.description || null,
      status: data.status || 'enabled',
      priority: data.priority || 'P2',
      tags: data.tags || null,
      variables: data.variables || null,
      execution_condition: data.execution_condition || null,
      created_by: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      steps: data.steps?.map((step, index) => ({
        id: index + 1,
        test_case_id: nextId - 1,
        api_id: step.api_id,
        step_name: step.step_name || null,
        sort_order: step.sort_order || index + 1,
        enabled: step.enabled !== undefined ? step.enabled : true,
        override_headers: step.override_headers || null,
        override_params: step.override_params || null,
        override_body: step.override_body || null,
        override_body_type: step.override_body_type || null,
        override_cookies: step.override_cookies || null,
        assertions: step.assertions || null,
        extractors: step.extractors || null,
        pre_script: step.pre_script || null,
        post_script: step.post_script || null,
        timeout_config: step.timeout_config || null,
        execution_condition: step.execution_condition || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })) || null
    }
    mockTestCasesData.push(newTestCase)
    return newTestCase
  },

  update(id: number, data: TestCaseUpdate): TestCase {
    const index = mockTestCasesData.findIndex(tc => tc.id === id)
    if (index === -1) {
      throw new Error('Test case not found')
    }

    mockTestCasesData[index] = {
      ...mockTestCasesData[index],
      ...data,
      updated_at: new Date().toISOString()
    }

    return mockTestCasesData[index]
  },

  delete(id: number): void {
    const index = mockTestCasesData.findIndex(tc => tc.id === id)
    if (index !== -1) {
      mockTestCasesData.splice(index, 1)
    }
  },

  copy(id: number): TestCase {
    const original = this.get(id)
    const copy: TestCase = {
      ...original,
      id: nextId++,
      name: `${original.name} (副本)`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    mockTestCasesData.push(copy)
    return copy
  },

  execute(id: number, data: ExecuteRequest): ExecutionRecord {
    const testCase = this.get(id)
    return {
      id: Math.floor(Math.random() * 1000) + 100,
      team_id: 1,
      test_case_id: id,
      test_case_name: testCase.name,
      environment_id: data.environment_id,
      environment_name: '测试环境',
      execution_type: 'manual',
      status: 'passed',
      total_steps: testCase.steps?.length || 0,
      passed_steps: testCase.steps?.length || 0,
      failed_steps: 0,
      skipped_steps: 0,
      data_iteration_count: 1,
      data_iteration_passed: 1,
      data_iteration_failed: 0,
      start_time: new Date().toISOString(),
      end_time: new Date().toISOString(),
      duration: Math.floor(Math.random() * 5000) + 500,
      executor_id: 1,
      executor_name: '测试用户',
      error_message: null,
      created_at: new Date().toISOString()
    }
  },

  batchExecute(ids: number[], data: ExecuteRequest): ExecutionRecord[] {
    return ids.map(id => this.execute(id, data))
  },

  checkCrossTeamCopy(id: number, targetTeamId: number): CrossTeamCopyCheck {
    return {
      can_copy: true,
      warnings: [],
      services_to_check: [],
      variables_to_check: []
    }
  },

  copyToTeam(id: number, targetTeamId: number, options?: any): { success: boolean; message: string } {
    return {
      success: true,
      message: '复制成功'
    }
  }
}

export const mockModules = {
  list(): any[] {
    return mockModulesData
  }
}
```

- [ ] **Step 2: 提交Mock数据**

```bash
git add src/mock/testcase.ts
git commit -m "feat: 添加测试用例Mock数据"
```

### Task 3: 创建测试用例API封装

**Files:**
- Create: `frontend/src/api/testcase.ts`

- [ ] **Step 1: 创建API封装文件**

创建文件 `frontend/src/api/testcase.ts`：

```typescript
import { http } from '@/utils/request'
import type {
  TestCase,
  TestCaseCreate,
  TestCaseUpdate,
  TestCaseModule,
  PaginatedResponse,
  ExecuteRequest,
  ExecutionRecord,
  CrossTeamCopyCheck
} from '@/types/testcase'

const TEAM_ID = 1
const USE_MOCK = true // Mock开关，生产环境设为false

// Mock数据导入
import { mockTestCases, mockTestCase, mockModules } from '@/mock/testcase'

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

export const testCaseModuleApi = {
  // 获取模块列表
  list(): Promise<TestCaseModule[]> {
    if (USE_MOCK) {
      return Promise.resolve(mockModules.list())
    }
    return http.get(`/teams/${TEAM_ID}/test-case-modules`)
  },

  // 创建模块
  create(data: { name: string; parent_id?: number; description?: string }): Promise<TestCaseModule> {
    if (USE_MOCK) {
      const newModule = {
        id: Math.floor(Math.random() * 1000) + 10,
        team_id: 1,
        name: data.name,
        parent_id: data.parent_id || null,
        description: data.description || null,
        sort_order: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      return Promise.resolve(newModule)
    }
    return http.post(`/teams/${TEAM_ID}/test-case-modules`, data)
  },

  // 更新模块
  update(id: number, data: { name?: string; description?: string }): Promise<TestCaseModule> {
    if (USE_MOCK) {
      return Promise.resolve({
        id,
        team_id: 1,
        name: data.name || '未命名模块',
        parent_id: null,
        description: data.description || null,
        sort_order: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
    }
    return http.put(`/test-case-modules/${id}`, data)
  },

  // 删除模块
  delete(id: number): Promise<void> {
    if (USE_MOCK) {
      return Promise.resolve()
    }
    return http.delete(`/test-case-modules/${id}`)
  }
}
```

- [ ] **Step 2: 提交API封装**

```bash
git add src/api/testcase.ts
git commit -m "feat: 添加测试用例API封装"
```

### Task 4: 创建数据源Mock数据和API封装

**Files:**
- Create: `frontend/src/mock/datasource.ts`
- Create: `frontend/src/api/datasource.ts`

- [ ] **Step 1: 创建数据源Mock数据**

创建文件 `frontend/src/mock/datasource.ts`：

```typescript
import type { DataSource, DataSourceCreate } from '@/types/testcase'

// 模拟数据源数据
const mockDataSourcesData: DataSource[] = [
  {
    id: 1,
    test_case_id: 1,
    name: '用户数据CSV',
    source_type: 'csv',
    source_config: {
      file_path: '/data/users.csv',
      delimiter: ',',
      has_header: true
    },
    enabled: true,
    iteration_mode: 'sequential',
    created_at: '2024-01-15T10:00:00',
    updated_at: '2024-01-15T10:00:00'
  },
  {
    id: 2,
    test_case_id: 1,
    name: '测试数据JSON',
    source_type: 'json',
    source_config: {
      content: '[{"username":"user1","password":"pass1"},{"username":"user2","password":"pass2"}]'
    },
    enabled: true,
    iteration_mode: 'random',
    created_at: '2024-01-16T14:30:00',
    updated_at: '2024-01-16T14:30:00'
  }
]

let nextId = 3

export const mockDataSource = {
  list(testCaseId: number): Promise<DataSource[]> {
    const filtered = mockDataSourcesData.filter(ds => ds.test_case_id === testCaseId)
    return Promise.resolve(filtered)
  },

  create(testCaseId: number, data: DataSourceCreate): Promise<DataSource> {
    const newDataSource: DataSource = {
      id: nextId++,
      test_case_id: testCaseId,
      name: data.name,
      source_type: data.source_type,
      source_config: data.source_config,
      enabled: data.enabled !== undefined ? data.enabled : true,
      iteration_mode: data.iteration_mode || 'sequential',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    mockDataSourcesData.push(newDataSource)
    return Promise.resolve(newDataSource)
  },

  update(id: number, data: any): Promise<DataSource> {
    const index = mockDataSourcesData.findIndex(ds => ds.id === id)
    if (index === -1) {
      return Promise.reject(new Error('Data source not found'))
    }

    mockDataSourcesData[index] = {
      ...mockDataSourcesData[index],
      ...data,
      updated_at: new Date().toISOString()
    }

    return Promise.resolve(mockDataSourcesData[index])
  },

  delete(id: number): Promise<void> {
    const index = mockDataSourcesData.findIndex(ds => ds.id === id)
    if (index !== -1) {
      mockDataSourcesData.splice(index, 1)
    }
    return Promise.resolve()
  },

  preview(id: number): Promise<{ total_rows: number; columns: string[]; preview_data: any[] }> {
    return Promise.resolve({
      total_rows: 10,
      columns: ['username', 'password', 'email'],
      preview_data: [
        { username: 'user1', password: 'pass1', email: 'user1@example.com' },
        { username: 'user2', password: 'pass2', email: 'user2@example.com' },
        { username: 'user3', password: 'pass3', email: 'user3@example.com' }
      ]
    })
  }
}
```

- [ ] **Step 2: 创建数据源API封装**

创建文件 `frontend/src/api/datasource.ts`：

```typescript
import { http } from '@/utils/request'
import type { DataSource, DataSourceCreate, DataSourceUpdate } from '@/types/testcase'

const USE_MOCK = true

// Mock数据导入
import { mockDataSource } from '@/mock/datasource'

export const dataSourceApi = {
  // 获取数据源列表
  list(testCaseId: number): Promise<DataSource[]> {
    if (USE_MOCK) {
      return mockDataSource.list(testCaseId)
    }
    return http.get(`/test-cases/${testCaseId}/data-sources`)
  },

  // 创建数据源
  create(testCaseId: number, data: DataSourceCreate): Promise<DataSource> {
    if (USE_MOCK) {
      return mockDataSource.create(testCaseId, data)
    }
    return http.post(`/test-cases/${testCaseId}/data-sources`, data)
  },

  // 更新数据源
  update(id: number, data: DataSourceUpdate): Promise<DataSource> {
    if (USE_MOCK) {
      return mockDataSource.update(id, data)
    }
    return http.put(`/data-sources/${id}`, data)
  },

  // 删除数据源
  delete(id: number): Promise<void> {
    if (USE_MOCK) {
      return mockDataSource.delete(id)
    }
    return http.delete(`/data-sources/${id}`)
  },

  // 预览数据源
  preview(id: number): Promise<{ total_rows: number; columns: string[]; preview_data: any[] }> {
    if (USE_MOCK) {
      return mockDataSource.preview(id)
    }
    return http.get(`/data-sources/${id}/preview`)
  }
}
```

- [ ] **Step 3: 提交数据源相关文件**

```bash
git add src/mock/datasource.ts src/api/datasource.ts
git commit -m "feat: 添加数据源Mock数据和API封装"
```

### Task 5: 创建执行记录Mock数据和API封装

**Files:**
- Create: `frontend/src/mock/execution.ts`
- Create: `frontend/src/api/execution.ts`

- [ ] **Step 1: 创建执行记录Mock数据**

创建文件 `frontend/src/mock/execution.ts`：

```typescript
import type { ExecutionRecord, StepExecutionRecord, PaginatedResponse } from '@/types/testcase'

// 模拟执行记录数据
const mockExecutionsData: ExecutionRecord[] = [
  {
    id: 101,
    team_id: 1,
    test_case_id: 1,
    test_case_name: '用户登录测试',
    environment_id: 1,
    environment_name: '测试环境',
    execution_type: 'manual',
    status: 'passed',
    total_steps: 1,
    passed_steps: 1,
    failed_steps: 0,
    skipped_steps: 0,
    data_iteration_count: 1,
    data_iteration_passed: 1,
    data_iteration_failed: 0,
    start_time: '2024-01-20T10:00:00',
    end_time: '2024-01-20T10:00:05',
    duration: 5000,
    executor_id: 1,
    executor_name: '测试用户',
    error_message: null,
    created_at: '2024-01-20T10:00:00'
  },
  {
    id: 102,
    team_id: 1,
    test_case_id: 1,
    test_case_name: '用户登录测试',
    environment_id: 1,
    environment_name: '测试环境',
    execution_type: 'manual',
    status: 'failed',
    total_steps: 1,
    passed_steps: 0,
    failed_steps: 1,
    skipped_steps: 0,
    data_iteration_count: 1,
    data_iteration_passed: 0,
    data_iteration_failed: 1,
    start_time: '2024-01-20T11:00:00',
    end_time: '2024-01-20T11:00:03',
    duration: 3000,
    executor_id: 1,
    executor_name: '测试用户',
    error_message: '断言失败: 状态码期望200，实际401',
    created_at: '2024-01-20T11:00:00'
  }
]

// 模拟步骤执行记录数据
const mockStepExecutionsData: StepExecutionRecord[] = [
  {
    id: 1001,
    case_execution_id: 101,
    step_id: 1,
    step_name: '发送登录请求',
    step_order: 1,
    api_id: 1,
    api_name: '登录接口',
    status: 'passed',
    skip_reason: null,
    request_url: 'http://api.example.com/login',
    request_method: 'POST',
    request_headers: '{"Content-Type":"application/json"}',
    request_body: '{"username":"admin","password":"123456"}',
    response_status: 200,
    response_headers: '{"Content-Type":"application/json"}',
    response_body: '{"code":0,"message":"success","data":{"token":"abc123"}}',
    response_time: 245,
    assertions: '[{"type":"status_code","expected":200,"actual":200,"passed":true}]',
    extractors: '[{"name":"token","type":"jsonpath","expression":"$.data.token","value":"abc123"}]',
    start_time: '2024-01-20T10:00:00',
    end_time: '2024-01-20T10:00:05',
    duration: 5000,
    error_message: null
  }
]

export const mockExecution = {
  list(testCaseId: number, params?: {
    page?: number
    page_size?: number
    status?: string
    executor_id?: number
    start_date?: string
    end_date?: string
  }): PaginatedResponse<ExecutionRecord> {
    let filtered = mockExecutionsData.filter(e => e.test_case_id === testCaseId)

    if (params?.status) {
      filtered = filtered.filter(e => e.status === params.status)
    }

    if (params?.executor_id) {
      filtered = filtered.filter(e => e.executor_id === params.executor_id)
    }

    const page = params?.page || 1
    const pageSize = params?.page_size || 20
    const start = (page - 1) * pageSize
    const end = start + pageSize

    return {
      items: filtered.slice(start, end),
      total: filtered.length,
      page,
      page_size: pageSize
    }
  },

  getDetail(executionId: number): Promise<ExecutionRecord & { steps: StepExecutionRecord[] }> {
    const execution = mockExecutionsData.find(e => e.id === executionId)
    if (!execution) {
      return Promise.reject(new Error('Execution not found'))
    }

    const steps = mockStepExecutionsData.filter(s => s.case_execution_id === executionId)

    return Promise.resolve({
      ...execution,
      steps
    })
  },

  exportReport(executionId: number, format: 'html' | 'excel'): Promise<Blob> {
    // 模拟导出报告
    const content = format === 'html'
      ? '<html><body><h1>执行报告</h1></body></html>'
      : 'Excel content'

    return Promise.resolve(new Blob([content], {
      type: format === 'html' ? 'text/html' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }))
  },

  listTeamExecutions(teamId: number, params?: {
    page?: number
    page_size?: number
    test_case_id?: number
    status?: string
    executor_id?: number
    start_date?: string
    end_date?: string
  }): PaginatedResponse<ExecutionRecord> {
    let filtered = mockExecutionsData.filter(e => e.team_id === teamId)

    if (params?.test_case_id) {
      filtered = filtered.filter(e => e.test_case_id === params.test_case_id)
    }

    if (params?.status) {
      filtered = filtered.filter(e => e.status === params.status)
    }

    if (params?.executor_id) {
      filtered = filtered.filter(e => e.executor_id === params.executor_id)
    }

    const page = params?.page || 1
    const pageSize = params?.page_size || 20
    const start = (page - 1) * pageSize
    const end = start + pageSize

    return {
      items: filtered.slice(start, end),
      total: filtered.length,
      page,
      page_size: pageSize
    }
  }
}
```

- [ ] **Step 2: 创建执行记录API封装**

创建文件 `frontend/src/api/execution.ts`：

```typescript
import { http } from '@/utils/request'
import type { ExecutionRecord, StepExecutionRecord, PaginatedResponse } from '@/types/testcase'

const USE_MOCK = true

// Mock数据导入
import { mockExecution } from '@/mock/execution'

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
      return mockExecution.getDetail(executionId)
    }
    return http.get(`/executions/${executionId}`)
  },

  // 导出执行报告
  exportReport(executionId: number, format: 'html' | 'excel' = 'html'): Promise<Blob> {
    if (USE_MOCK) {
      return mockExecution.exportReport(executionId, format)
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

- [ ] **Step 3: 提交执行记录相关文件**

```bash
git add src/mock/execution.ts src/api/execution.ts
git commit -m "feat: 添加执行记录Mock数据和API封装"
```

### Task 6: 创建测试用例状态管理

**Files:**
- Create: `frontend/src/stores/testcase.ts`

- [ ] **Step 1: 创建Pinia Store**

创建文件 `frontend/src/stores/testcase.ts`：

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { testCaseApi, testCaseModuleApi } from '@/api/testcase'
import type { TestCase, TestCaseCreate, TestCaseUpdate, TestCaseModule } from '@/types/testcase'

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

  // 获取测试用例列表
  async function fetchTestCases(params?: {
    page?: number
    page_size?: number
    keyword?: string
    status?: string
    priority?: string
    module_id?: number
  }) {
    loading.value = true
    try {
      const response = await testCaseApi.list(params)
      testCases.value = response.items
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  // 获取测试用例详情
  async function fetchTestCase(id: number) {
    loading.value = true
    try {
      currentTestCase.value = await testCaseApi.get(id)
      return currentTestCase.value
    } finally {
      loading.value = false
    }
  }

  // 创建测试用例
  async function createTestCase(data: TestCaseCreate) {
    const testCase = await testCaseApi.create(data)
    testCases.value.unshift(testCase)
    total.value++
    return testCase
  }

  // 更新测试用例
  async function updateTestCase(id: number, data: TestCaseUpdate) {
    const testCase = await testCaseApi.update(id, data)
    const index = testCases.value.findIndex(tc => tc.id === id)
    if (index !== -1) {
      testCases.value[index] = testCase
    }
    if (currentTestCase.value?.id === id) {
      currentTestCase.value = testCase
    }
    return testCase
  }

  // 删除测试用例
  async function deleteTestCase(id: number) {
    await testCaseApi.delete(id)
    const index = testCases.value.findIndex(tc => tc.id === id)
    if (index !== -1) {
      testCases.value.splice(index, 1)
      total.value--
    }
    if (currentTestCase.value?.id === id) {
      currentTestCase.value = null
    }
  }

  // 复制测试用例
  async function copyTestCase(id: number) {
    const testCase = await testCaseApi.copy(id)
    testCases.value.unshift(testCase)
    total.value++
    return testCase
  }

  // 批量删除测试用例
  async function batchDeleteTestCases(ids: number[]) {
    for (const id of ids) {
      await testCaseApi.delete(id)
    }
    testCases.value = testCases.value.filter(tc => !ids.includes(tc.id))
    total.value -= ids.length
  }

  // 获取模块列表
  async function fetchModules() {
    modules.value = await testCaseModuleApi.list()
  }

  // 创建模块
  async function createModule(data: { name: string; parent_id?: number; description?: string }) {
    const module = await testCaseModuleApi.create(data)
    modules.value.push(module)
    return module
  }

  // 更新模块
  async function updateModule(id: number, data: { name?: string; description?: string }) {
    const module = await testCaseModuleApi.update(id, data)
    const index = modules.value.findIndex(m => m.id === id)
    if (index !== -1) {
      modules.value[index] = module
    }
    return module
  }

  // 删除模块
  async function deleteModule(id: number) {
    await testCaseModuleApi.delete(id)
    const index = modules.value.findIndex(m => m.id === id)
    if (index !== -1) {
      modules.value.splice(index, 1)
    }
  }

  return {
    // 状态
    testCases,
    currentTestCase,
    total,
    loading,
    modules,

    // 计算属性
    enabledTestCases,

    // 方法
    fetchTestCases,
    fetchTestCase,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    copyTestCase,
    batchDeleteTestCases,
    fetchModules,
    createModule,
    updateModule,
    deleteModule
  }
})
```

- [ ] **Step 2: 提交状态管理**

```bash
git add src/stores/testcase.ts
git commit -m "feat: 添加测试用例状态管理"
```

### Task 7: 更新路由配置

**Files:**
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 添加测试用例相关路由**

在 `frontend/src/router/index.ts` 文件中，在现有路由数组末尾添加以下路由：

```typescript
  // 测试用例管理路由
  {
    path: '/test-cases',
    name: 'TestCaseList',
    component: () => import('@/views/testcase/TestCaseList.vue'),
    meta: {
      title: '测试用例管理'
    }
  },
  {
    path: '/test-cases/new',
    name: 'TestCaseCreate',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '新建测试用例'
    }
  },
  {
    path: '/test-cases/:id',
    name: 'TestCaseDetail',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '测试用例详情'
    }
  },
  {
    path: '/test-cases/:id/edit',
    name: 'TestCaseEdit',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '编辑测试用例'
    }
  },
  // 执行记录路由
  {
    path: '/executions',
    name: 'ExecutionList',
    component: () => import('@/views/execution/ExecutionList.vue'),
    meta: {
      title: '执行记录'
    }
  },
  {
    path: '/executions/:id',
    name: 'ExecutionDetail',
    component: () => import('@/views/execution/ExecutionDetail.vue'),
    meta: {
      title: '执行记录详情'
    }
  }
```

- [ ] **Step 2: 提交路由配置**

```bash
git add src/router/index.ts
git commit -m "feat: 添加测试用例和执行记录路由配置"
```

---

## 阶段一完成检查点

- [ ] **验证阶段一完成**

运行以下命令验证所有文件已创建：

```bash
ls src/api/testcase.ts src/api/datasource.ts src/api/execution.ts
ls src/mock/testcase.ts src/mock/datasource.ts src/mock/execution.ts
ls src/stores/testcase.ts
```

Expected: 所有文件存在

---

## 阶段二：核心功能（预计3-4天）

### Task 8: 创建测试用例列表页基础结构

**Files:**
- Create: `frontend/src/views/testcase/TestCaseList.vue`

- [ ] **Step 1: 创建列表页基础结构**

创建文件 `frontend/src/views/testcase/TestCaseList.vue`，包含基础HTML结构和样式：

```vue
<template>
  <div class="testcase-list-page">
    <div class="left-panel">
      <TestCaseTree @select="handleModuleSelect" />
      <div class="left-section">
        <div class="section-header">
          <span class="section-icon">🕐</span>
          <span class="section-title">最近</span>
        </div>
        <div class="section-content">
          <div
            v-for="item in recentVisits"
            :key="item.id"
            class="recent-item"
            @click="handleGoDetail(item)"
          >
            <span class="item-name">{{ item.name }}</span>
            <span class="item-time">{{ formatTimeAgo(item.updated_at) }}</span>
          </div>
          <div v-if="recentVisits.length === 0" class="empty-hint">暂无最近访问</div>
        </div>
      </div>
    </div>

    <div class="right-panel">
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">测试用例管理</h1>
          <p class="page-subtitle">管理测试用例，支持创建、编辑、执行和查看执行记录</p>
        </div>
      </div>

      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" class="primary-btn" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建用例
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-input
            v-model="searchText"
            placeholder="搜索用例名称/描述"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
          </el-select>
          <el-select v-model="filterPriority" placeholder="优先级" clearable class="filter-select">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </div>
      </div>

      <div class="batch-bar" v-if="selectedCases.length > 0">
        <span class="batch-info">已选择 {{ selectedCases.length }} 项</span>
        <el-button size="small" type="danger" plain @click="handleBatchDelete">批量删除</el-button>
        <el-button size="small" plain @click="selectedCases = []">取消选择</el-button>
      </div>

      <div class="table-container">
        <el-table
          :data="testCases"
          v-loading="loading"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          :header-cell-style="{ backgroundColor: '#fafafa', fontWeight: 600 }"
        >
          <el-table-column type="selection" width="40" align="center" />
          <el-table-column prop="name" label="用例名称" min-width="180">
            <template #default="{ row }">
              <span class="case-name" @click="handleGoDetail(row)">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'enabled' ? 'success' : 'info'" size="small">
                {{ row.status === 'enabled' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="优先级" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">
                {{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="模块" width="120" align="center">
            <template #default="{ row }">
              <span class="module-name">{{ getModuleName(row.module_id) || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="标签" width="150">
            <template #default="{ row }">
              <div class="tag-list">
                <el-tag
                  v-for="tag in parseTags(row.tags)"
                  :key="tag"
                  size="small"
                  class="case-tag"
                >{{ tag }}</el-tag>
                <span v-if="!parseTags(row.tags).length" class="no-tag">-</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="160" align="center">
            <template #default="{ row }">
              <span class="update-time">{{ formatDate(row.updated_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleExecute(row)">
                <el-icon><VideoPlay /></el-icon>执行
              </el-button>
              <el-button type="primary" link size="small" @click="handleGoDetail(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-dropdown trigger="click" @command="(cmd: string) => handleMoreCommand(cmd, row)">
                <el-button type="primary" link size="small">
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="copy">
                      <el-icon><CopyDocument /></el-icon>复制
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon color="#F56C6C"><Delete /></el-icon><span style="color:#F56C6C">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            background
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, VideoPlay, Edit, More, CopyDocument, Delete } from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/stores/testcase'
import type { TestCase } from '@/types/testcase'
import TestCaseTree from './components/TestCaseTree.vue'

const router = useRouter()
const store = useTestCaseStore()

const loading = ref(false)
const searchText = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const filterModuleId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedCases = ref<TestCase[]>([])
const recentVisits = ref<TestCase[]>([])

const testCases = computed(() => store.testCases)
const total = computed(() => store.total)

onMounted(async () => {
  await Promise.all([
    fetchTestCases(),
    store.fetchModules()
  ])
})

watch([currentPage, pageSize], () => {
  fetchTestCases()
})

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchText, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchTestCases()
  }, 300)
})

watch([filterStatus, filterPriority], () => {
  currentPage.value = 1
  fetchTestCases()
})

async function fetchTestCases() {
  loading.value = true
  try {
    await store.fetchTestCases({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchText.value || undefined,
      status: filterStatus.value || undefined,
      priority: filterPriority.value || undefined,
      module_id: filterModuleId.value || undefined
    })
  } finally {
    loading.value = false
  }
}

function handleModuleSelect(moduleId: number | null) {
  filterModuleId.value = moduleId
  currentPage.value = 1
  fetchTestCases()
}

function handleCreate() {
  router.push('/test-cases/new')
}

function handleGoDetail(row: TestCase) {
  router.push(`/test-cases/${row.id}`)
}

function handleExecute(row: TestCase) {
  ElMessage.info('执行功能将在第三阶段实现')
}

function handleSelectionChange(selection: TestCase[]) {
  selectedCases.value = selection
}

async function handleMoreCommand(cmd: string, row: TestCase) {
  if (cmd === 'copy') {
    try {
      await ElMessageBox.confirm(`确定要复制测试用例"${row.name}"吗？`, '提示', { type: 'info' })
      await store.copyTestCase(row.id)
      ElMessage.success('复制成功')
      await fetchTestCases()
    } catch (error: any) {
      if (error !== 'cancel') { }
    }
  } else if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定删除测试用例"${row.name}"吗？此操作不可恢复。`,
        '警告',
        { type: 'warning', confirmButtonText: '确定删除', confirmButtonClass: 'el-button--danger' }
      )
      await store.deleteTestCase(row.id)
      ElMessage.success('删除成功')
      await fetchTestCases()
    } catch (error: any) {
      if (error !== 'cancel') { }
    }
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedCases.value.length} 个测试用例？此操作不可恢复。`,
      '警告',
      { type: 'warning' }
    )
    const ids = selectedCases.value.map(c => c.id)
    await store.batchDeleteTestCases(ids)
    ElMessage.success(`成功删除 ${ids.length} 个`)
    selectedCases.value = []
    await fetchTestCases()
  } catch (error: any) {
    if (error !== 'cancel') { }
  }
}

function getModuleName(moduleId: number | null): string {
  if (!moduleId) return ''
  const module = store.modules.find(m => m.id === moduleId)
  return module?.name || ''
}

function getPriorityType(priority: string): string {
  const types: Record<string, string> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return types[priority] || ''
}

function parseTags(tags?: any): string[] {
  if (!tags) return []
  if (Array.isArray(tags)) {
    return tags.filter(tag => typeof tag === 'string')
  }
  return []
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function formatTimeAgo(date: string) {
  if (!date) return ''
  const now = new Date()
  const d = new Date(date)
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return `${d.getMonth() + 1}-${d.getDate()}`
}
</script>

<style scoped>
.testcase-list-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f5f7;
}

.left-panel {
  width: 220px;
  min-width: 220px;
  background-color: #ffffff;
  border-right: 1px solid #e5e4e7;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

.left-section {
  border-top: 1px solid #e5e4e7;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #6b6375;
}

.section-icon {
  font-size: 14px;
}

.section-title {
  flex: 1;
}

.section-content {
  padding: 0 8px 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
}

.recent-item:hover {
  background-color: #f4f3ec;
}

.item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #08060d;
}

.item-time {
  font-size: 11px;
  color: #C0C4CC;
  flex-shrink: 0;
}

.empty-hint {
  font-size: 12px;
  color: #C0C4CC;
  padding: 12px 8px;
  text-align: center;
}

.right-panel {
  flex: 1;
  min-width: 0;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.header-content {
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
  margin: 0 0 8px 0;
  line-height: 32px;
}

.page-subtitle {
  font-size: 14px;
  color: #6b6375;
  margin: 0;
  line-height: 22px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 12px 16px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-left .el-button {
  padding: 8px 16px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.primary-btn {
  background-color: #aa3bff !important;
  border-color: #aa3bff !important;
}

.primary-btn:hover {
  background-color: #9333ea !important;
  border-color: #9333ea !important;
}

.search-input {
  width: 280px;
  max-width: 100%;
}

.filter-select {
  width: 90px;
  min-width: 70px;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 6px;
  margin-bottom: 12px;
  flex-shrink: 0;
  flex-wrap: wrap;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
}

.batch-info {
  font-size: 13px;
  font-weight: 500;
  padding-right: 12px;
  margin-right: 4px;
  border-right: 1px solid rgba(255, 255, 255, 0.25);
}

.batch-bar :deep(.el-button) {
  border-color: transparent;
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 5px 12px;
  height: 28px;
  margin: 0;
}

.batch-bar :deep(.el-button--danger) {
  background-color: #ef4444;
  border-color: transparent;
  color: #ffffff;
  margin: 0;
}

.table-container {
  flex: 1;
  min-height: 0;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-container :deep(.el-table) {
  flex: 1;
}

.table-container :deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.case-name {
  color: #08060d;
  cursor: pointer;
  font-weight: 500;
}

.case-name:hover {
  color: #aa3bff;
}

.module-name {
  font-size: 13px;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.case-tag {
  font-size: 11px;
  background-color: #f4f3ec;
  color: #6b6375;
  border: none;
}

.no-tag {
  color: #C0C4CC;
}

.update-time {
  font-size: 13px;
  color: #909399;
}

.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e5e4e7;
  background-color: #fafafa;
}

@media (max-width: 1024px) {
  .left-panel {
    display: none;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .toolbar-left, .toolbar-right {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }

  .filter-select {
    flex: 1;
    min-width: 80px;
  }
}
</style>
```

- [ ] **Step 2: 提交列表页基础结构**

```bash
git add src/views/testcase/TestCaseList.vue
git commit -m "feat: 创建测试用例列表页基础结构"
```

由于实施计划内容过长，我将继续创建完整的计划文档...
