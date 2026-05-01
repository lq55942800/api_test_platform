// HTTP Methods
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'

// Environment Types
export interface EnvServer {
  id?: number
  service_id?: number
  name: string
  host: string
  port?: number
  protocol: string
  base_path?: string
  headers?: string
  timeout?: number
  is_default: boolean
}

export interface EnvService {
  id?: number
  environment_id?: number
  name: string
  service_type: string
  description?: string
  servers?: EnvServer[]
  databases?: any[]
}

export interface EnvVariable {
  id?: number
  environment_id?: number
  key: string
  value?: string
  value_type: 'string' | 'number' | 'boolean'
  is_encrypted?: boolean
  description?: string
}

export interface Environment {
  id?: number
  team_id?: number
  name: string
  description?: string
  is_default?: boolean
  is_active?: boolean
  created_by?: number
  created_at?: string
  updated_at?: string
  services?: EnvService[]
  variables?: EnvVariable[]
}

// API Types
export type ApiStatus = 'draft' | 'enabled' | 'disabled' | 'deprecated'
export type BodyType = 'none' | 'json' | 'form-data' | 'x-www-form-urlencoded' | 'raw' | 'xml' | 'binary'

export interface ApiParam {
  name: string
  example?: string
  default_value?: string
  required?: boolean
  description?: string
  type?: string
}

export interface ApiModule {
  id: number
  team_id: number
  name: string
  parent_id?: number
  description?: string
  sort_order?: number
  children?: ApiModule[]
  api_count?: number
}

export interface ApiDefinition {
  id?: number
  team_id?: number
  module_id?: number
  service_id?: number
  name: string
  method: HttpMethod
  path: string
  description?: string
  status: ApiStatus
  protocol?: string
  path_params?: string
  query_params?: string
  header_params?: string
  cookie_params?: string
  body_type?: BodyType
  body_definition?: string
  responses?: string
  pre_request_actions?: string
  post_request_actions?: string
  assertions?: string
  connect_timeout?: number
  read_timeout?: number
  write_timeout?: number
  pool_timeout?: number
  sample_timeout?: number
  sql_timeout?: number
  script_timeout?: number
  timeout_enabled?: boolean
  owner_id?: number
  last_debug_at?: string
  last_debug_status?: string
  reference_count?: number
  is_deleted?: boolean
  created_by?: number
  updated_by?: number
  created_at?: string
  updated_at?: string
}

// Test Case Types
export type TestCaseStatus = 'enabled' | 'disabled'
export type TestCasePriority = 'P0' | 'P1' | 'P2' | 'P3'
export type StepType = 'api' | 'if' | 'for' | 'while'

export interface TestCaseVariable {
  key: string
  value: string
  default_value?: string
  description?: string
  enabled?: boolean
}

export interface StepExecutionCondition {
  type?: 'if' | 'for' | 'while'
  logic?: 'and' | 'or'
  conditions?: string[]
  expression?: string
  for_mode?: 'count' | 'items'
  loop_count?: number
  loop_variable?: string
  loop_items_source?: 'variable' | 'custom'
  loop_items_variable?: string
  loop_items?: string[]
  while_mode?: 'expression' | 'count'
  description?: string
}

export interface TestCaseStep {
  id?: number
  test_case_id?: number
  step_type: StepType
  api_id?: number | null
  parent_step_id?: number | null
  step_name?: string | null
  sort_order?: number
  enabled?: boolean
  override_headers?: Record<string, any> | null
  override_params?: Record<string, any> | null
  override_body?: any | null
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
  // For display
  api_name?: string
}

export interface TestCase {
  id?: number
  team_id?: number
  name: string
  module_id?: number | null
  description?: string | null
  status: TestCaseStatus
  priority: TestCasePriority
  tags?: string[] | null
  variables?: TestCaseVariable[] | null
  created_by?: number
  created_at?: string
  updated_at?: string
  steps?: TestCaseStep[] | null
  steps_tree?: TestCaseStep[]
}

export interface TestCaseModule {
  id: number
  team_id: number
  name: string
  parent_id?: number
  description?: string
  sort_order?: number
  created_at?: string
  updated_at?: string
  children?: TestCaseModule[]
  case_count?: number
}

// Execution Types
export interface StepExecutionRecord {
  id?: number
  case_execution_id?: number
  step_id?: number
  step_name?: string
  step_order?: number
  api_id?: number
  api_name?: string
  status: string
  skip_reason?: string
  request_url?: string
  request_method?: string
  request_headers?: string
  request_body?: string
  response_status?: number
  response_headers?: string
  response_body?: string
  response_time?: number
  assertions?: string
  extractors?: string
  error_message?: string
  start_time?: string
  end_time?: string
  duration?: number
}

export interface ExecutionRecord {
  id?: number
  team_id?: number
  test_case_id?: number
  test_case_name?: string
  test_case_snapshot?: string
  environment_id?: number
  environment_name?: string
  execution_type?: string
  status: string
  total_steps?: number
  passed_steps?: number
  failed_steps?: number
  skipped_steps?: number
  data_iteration_count?: number
  data_iteration_passed?: number
  data_iteration_failed?: number
  start_time?: string
  end_time?: string
  duration?: number
  executor_id?: number
  executor_name?: string
  error_message?: string
  created_at?: string
  steps?: StepExecutionRecord[]
}