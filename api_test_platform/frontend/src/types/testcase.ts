export interface StepExecutionCondition {
  type: 'if' | 'for' | 'while'
  logic?: 'and' | 'or'
  conditions?: string[]
  expression?: string
  for_mode?: 'count' | 'items'
  loop_count?: number
  loop_variable?: string
  loop_items_source?: 'variable' | 'custom'
  loop_items_variable?: string
  loop_items?: string
  while_mode?: 'expression' | 'count'
  description?: string
}

export interface TestCaseVariable {
  key: string
  value: string
  default_value: string
  description: string
  enabled: boolean
}

export interface TestCaseStep {
  id?: number
  test_case_id?: number
  step_type: 'api' | 'if' | 'for' | 'while'
  api_id?: number | null
  parent_step_id?: number | null
  step_name: string | null
  sort_order: number
  enabled: boolean
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
  execution_condition?: StepExecutionCondition | null
  created_at?: string
  updated_at?: string
  children?: TestCaseStep[]
}

export interface TestCase {
  id: number
  team_id: number
  name: string
  module_id: number | null
  description: string | null
  status: 'enabled' | 'disabled'
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  tags: string[] | null
  variables: TestCaseVariable[] | null
  created_by: number
  created_at: string
  updated_at: string
  steps: TestCaseStep[] | null
}

export interface TestCaseStepCreate {
  step_type?: 'api' | 'if' | 'for' | 'while'
  api_id?: number | null
  parent_step_id?: number | null
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
  execution_condition?: StepExecutionCondition | null
}

export interface TestCaseCreate {
  name: string
  module_id?: number | null
  description?: string | null
  status?: string
  priority?: string
  tags?: string[] | null
  variables?: TestCaseVariable[] | null
  steps?: TestCaseStepCreate[] | null
}

export interface TestCaseUpdate {
  name?: string | null
  module_id?: number | null
  description?: string | null
  status?: string | null
  priority?: string | null
  tags?: string[] | null
  variables?: TestCaseVariable[] | null
  steps?: TestCaseStepCreate[] | null
}

export interface ExecutionRecord {
  id: number
  test_case_id: number
  environment_id: number
  status: string
  total_steps: number
  passed_steps: number
  failed_steps: number
  skipped_steps: number
  start_time: string | null
  end_time: string | null
  duration: number
  error_message: string | null
  created_at: string
}

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
  pre_actions: string | null
  post_actions: string | null
  start_time: string | null
  end_time: string | null
  duration: number | null
  error_message: string | null
  request_data: any | null
  response_data: any | null
}

export interface CrossTeamCopyCheck {
  can_copy: boolean
  missing_environments: string[]
  missing_apis: string[]
  warnings: string[]
}

export interface ExecuteRequest {
  environment_id: number
  fail_strategy?: string
  save_record?: boolean
  timeout?: number
  step_interval?: number
}

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

export interface TestCaseModuleCreate {
  name: string
  parent_id?: number | null
  description?: string | null
  sort_order?: number
}

export interface TestCaseModuleUpdate {
  name?: string
  parent_id?: number | null
  description?: string | null
  sort_order?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
