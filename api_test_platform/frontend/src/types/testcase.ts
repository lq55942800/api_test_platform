// 测试步骤
export interface TestCaseStep {
  id: number
  test_case_id: number
  api_id: number
  step_name: string | null
  sort_order: number
  enabled: boolean
  override_headers: Record<string, any> | null
  override_params: Record<string, any> | null
  override_body: string | null
  override_body_type: string | null
  override_cookies: any[] | null
  assertions: any[] | null
  extractors: any[] | null
  pre_script: string | null
  post_script: string | null
  timeout_config: Record<string, any> | null
  execution_condition: Record<string, any> | null
  created_at: string
  updated_at: string
}

// 测试用例
export interface TestCase {
  id: number
  team_id: number
  name: string
  module_id: number | null
  description: string | null
  status: 'enabled' | 'disabled'
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  tags: string[] | null
  variables: any[] | null
  execution_condition: Record<string, any> | null
  created_by: number
  created_at: string
  updated_at: string
  steps: TestCaseStep[] | null
}

// 数据源
export interface DataSource {
  id: number
  test_case_id: number
  name: string
  source_type: 'csv' | 'json' | 'database'
  source_config: Record<string, any>
  enabled: boolean
  iteration_mode: 'sequential' | 'random'
  created_at: string
  updated_at: string
}

// 执行记录
export interface ExecutionRecord {
  id: number
  team_id: number
  test_case_id: number
  test_case_name: string
  environment_id: number | null
  environment_name: string | null
  execution_type: string | null
  status: 'pending' | 'running' | 'passed' | 'failed' | 'error' | 'skipped'
  total_steps: number
  passed_steps: number
  failed_steps: number
  skipped_steps: number
  data_iteration_count: number
  data_iteration_passed: number
  data_iteration_failed: number
  start_time: string | null
  end_time: string | null
  duration: number | null
  executor_id: number | null
  executor_name: string | null
  error_message: string | null
  created_at: string
}

// 步骤执行记录
export interface StepExecutionRecord {
  id: number
  case_execution_id: number
  step_id: number | null
  step_name: string | null
  step_order: number | null
  api_id: number | null
  api_name: string | null
  status: string
  skip_reason: string | null
  request_url: string | null
  request_method: string | null
  request_headers: string | null
  request_body: string | null
  response_status: number | null
  response_headers: string | null
  response_body: string | null
  response_time: number | null
  assertions: string | null
  extractors: string | null
  start_time: string | null
  end_time: string | null
  duration: number | null
  error_message: string | null
}

// 跨团队复制检查
export interface CrossTeamCopyCheck {
  can_copy: boolean
  warnings: Array<{
    type: string
    message: string
    suggestion: string
  }>
  services_to_check: Array<{
    source_service: string
    target_exists: boolean
    source_servers: string[]
  }>
  variables_to_check: string[]
}

// 执行请求
export interface ExecuteRequest {
  environment_id: number
  fail_strategy?: 'stop' | 'continue'
  save_record?: boolean
  timeout?: number
  step_interval?: number
  data_source_id?: number
}

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
