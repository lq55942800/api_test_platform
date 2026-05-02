export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH',
  HEAD = 'HEAD',
  OPTIONS = 'OPTIONS'
}

export enum ApiStatus {
  DRAFT = 'draft',
  ENABLED = 'enabled',
  DISABLED = 'disabled',
  DEPRECATED = 'deprecated'
}

export enum BodyType {
  NONE = 'none',
  JSON = 'json',
  FORM_DATA = 'form-data',
  X_WWW_FORM_URLENCODED = 'x-www-form-urlencoded',
  RAW = 'raw',
  XML = 'xml',
  BINARY = 'binary'
}

export enum ParamType {
  STRING = 'String',
  INTEGER = 'Integer',
  FLOAT = 'Float',
  BOOLEAN = 'Boolean',
  ARRAY = 'Array',
  OBJECT = 'Object',
  FILE = 'File'
}

export interface ApiParam {
  name: string
  type: ParamType | string
  required: boolean
  default_value?: string
  description?: string
  example?: string
  validation?: Record<string, any>
  children?: ApiParam[]
}

export interface ApiResponse {
  status_code: number
  description: string
  body_definition?: string
  body_example?: string
  headers?: Record<string, string>
}

export type PreRequestActionType =
  | 'set_variable'
  | 'wait'
  | 'script'
  | 'database'

export type PostRequestActionType =
  | 'extract'
  | 'script'
  | 'database'

export type AssertionType =
  | 'status_code'
  | 'response_time'
  | 'header'
  | 'body'
  | 'json_schema'
  | 'script'

export type ExtractType = 'jsonpath' | 'regex' | 'header' | 'cookie' | 'direct'

export type VariableScope = 'temp' | 'module' | 'env' | 'global'

export type ExtractSource = 'response_json' | 'response_text' | 'response_header' | 'response_cookie' | 'elapsed_time'

export type AssertionOperator =
  | 'eq'
  | 'neq'
  | 'gt'
  | 'lt'
  | 'gte'
  | 'lte'
  | 'contains'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'
  | 'matches'
  | 'is_empty'
  | 'not_empty'
  | 'length_eq'
  | 'length_gt'
  | 'length_lt'
  | 'in'
  | 'between'
  | 'type_eq'
  | 'has_key'

export interface ExtractorConfig {
  source: ExtractSource
  type: ExtractType
  expression: string
  default_value: string
  target_variable: string
  target_scope: VariableScope
}

export interface VariableItem {
  name: string
  value: string
  scope: VariableScope
  overwrite: boolean
}

export interface AssertionItem {
  type: AssertionType
  path?: string
  operator: AssertionOperator
  expected: any
  message?: string
}

export interface PreRequestAction {
  id: string
  enabled: boolean
  name: string
  type: PreRequestActionType | string
  phase: string
  order: number
  config: Record<string, any>
  description?: string
}

export interface PostRequestAction {
  id: string
  enabled: boolean
  name: string
  type: PostRequestActionType | string
  phase: string
  order: number
  config: Record<string, any>
  description?: string
}

export interface Assertion {
  id: string
  enabled: boolean
  name: string
  type: AssertionType | string
  phase: string
  order: number
  config: Record<string, any>
  description?: string
}

export interface TimeoutConfig {
  connect_timeout: number
  read_timeout: number
  write_timeout: number
  pool_timeout: number
  sample_timeout: number
  sql_timeout: number
  script_timeout: number
  timeout_enabled: boolean
}

export interface ActionExecutionResult {
  id: string
  name: string
  type: string
  success: boolean
  error?: string
  duration_ms: number
  output?: Record<string, any>
}

export interface AssertionExecutionResult {
  id: string
  name: string
  type: string
  passed: boolean
  actual: any
  expected: any
  operator?: string
  message: string
  severity: string
  duration_ms: number
}

export interface AssertionSummary {
  total: number
  passed: number
  failed: number
  critical_failed: number
  warning_failed: number
  info_failed: number
  all_passed: boolean
  critical_passed: boolean
}

export interface ApiDefinition {
  id: number
  team_id: number
  module_id?: number
  service_id?: number
  name: string
  method: HttpMethod | string
  path: string
  description?: string
  status: ApiStatus | string
  protocol?: string
  tags?: ApiTag[]
  owner_id?: number
  path_params?: ApiParam[]
  query_params?: ApiParam[]
  header_params?: ApiParam[]
  cookie_params?: ApiParam[]
  body_type?: BodyType | string
  body_definition?: string
  responses?: ApiResponse[]
  pre_request_actions?: PreRequestAction[]
  post_request_actions?: PostRequestAction[]
  assertions?: Assertion[]
  connect_timeout?: number
  read_timeout?: number
  write_timeout?: number
  pool_timeout?: number
  sample_timeout?: number
  sql_timeout?: number
  script_timeout?: number
  timeout_enabled?: boolean
  lock_user_id?: number
  lock_time?: string
  last_debug_at?: string
  last_debug_status?: string
  reference_count?: number
  is_deleted?: boolean
  created_by: number
  updated_by?: number
  created_at: string
  updated_at?: string
  module_name?: string
}

export interface ApiDefinitionCreate {
  module_id?: number
  service_id?: number
  name: string
  method: string
  path: string
  description?: string
  status?: string
  tags?: string
  tag_ids?: number[]
  owner_id?: number
  path_params?: ApiParam[]
  query_params?: ApiParam[]
  header_params?: ApiParam[]
  cookie_params?: ApiParam[]
  body_type?: string
  body_definition?: string
  responses?: ApiResponse[]
  pre_request_actions?: PreRequestAction[]
  post_request_actions?: PostRequestAction[]
  assertions?: Assertion[]
  connect_timeout?: number
  read_timeout?: number
  write_timeout?: number
  pool_timeout?: number
  sample_timeout?: number
  sql_timeout?: number
  script_timeout?: number
  timeout_enabled?: boolean
}

export interface ApiDefinitionUpdate {
  module_id?: number
  service_id?: number
  name?: string
  method?: string
  path?: string
  description?: string
  status?: string
  tags?: string
  tag_ids?: number[]
  owner_id?: number
  path_params?: ApiParam[]
  query_params?: ApiParam[]
  header_params?: ApiParam[]
  cookie_params?: ApiParam[]
  body_type?: string
  body_definition?: string
  responses?: ApiResponse[]
  pre_request_actions?: PreRequestAction[]
  post_request_actions?: PostRequestAction[]
  assertions?: Assertion[]
  connect_timeout?: number
  read_timeout?: number
  write_timeout?: number
  pool_timeout?: number
  sample_timeout?: number
  sql_timeout?: number
  script_timeout?: number
  timeout_enabled?: boolean
}

export interface ApiModule {
  id: number
  team_id: number
  parent_id?: number
  name: string
  description?: string
  sort_order: number
  created_by: number
  created_at: string
  updated_at?: string
  children?: ApiModule[]
  api_count?: number
}

export interface ApiModuleCreate {
  parent_id?: number
  name: string
  description?: string
  sort_order?: number
}

export interface ApiModuleUpdate {
  name?: string
  description?: string
  sort_order?: number
  parent_id?: number
}

export interface ApiTag {
  id: number
  team_id: number
  name: string
  color?: string
  tag_group?: string
  created_by: number
  created_at: string
}

export interface ApiTagCreate {
  name: string
  color?: string
  tag_group?: string
}

export interface ApiVersion {
  id: number
  api_id: number
  version_number: number
  snapshot: string
  change_type?: string
  change_summary?: string
  affected_fields?: string
  changed_by: number
  created_at: string
  changed_by_name?: string
}

export interface VersionDiff {
  changes: VersionChange[]
  impact_level: string
  summary: string
}

export interface VersionChange {
  type: string
  field: string
  old_value?: any
  new_value?: any
  impact: string
}

export interface DebugHistory {
  id: number
  api_id: number
  environment_id?: number
  user_id: number
  request_method: string
  request_url: string
  request_headers?: string
  request_body?: string
  response_status?: number
  response_headers?: string
  response_body?: string
  elapsed_ms?: number
  error_message?: string
  created_at: string
}

export interface DebugRequest {
  environment_id?: number
  service_id?: number
  param_overrides?: Record<string, any>
  header_overrides?: Record<string, any>
  body_overrides?: string
  body_type?: string
  cookie_overrides?: any[]
  pre_request_actions_overrides?: any[]
  post_request_actions_overrides?: any[]
  assertions_overrides?: any[]
  timeout_config_overrides?: any
  timeout?: number
}

export interface DebugResult {
  status_code?: number
  headers?: Record<string, string>
  body?: string
  elapsed_ms?: number
  history_id?: number
  error_message?: string
  request_url?: string
  request_headers?: Record<string, string>
  pre_request_results?: ActionExecutionResult[]
  post_request_results?: ActionExecutionResult[]
  assertion_results?: AssertionExecutionResult[]
  assertion_summary?: AssertionSummary
  variables_snapshot?: Record<string, any>
  timeout_config?: Record<string, number | boolean>
}

export interface AuditLog {
  id: number
  team_id: number
  api_id?: number
  user_id: number
  action: string
  resource_type?: string
  resource_name?: string
  old_value?: string
  new_value?: string
  change_summary?: string
  ip_address?: string
  created_at: string
  user_name?: string
}

export interface ImportRequest {
  import_type: 'file' | 'url'
  content?: string
  url?: string
  module_id?: number
  conflict_strategy: 'skip' | 'overwrite' | 'copy' | 'manual'
  selected_apis?: number[]
}

export interface ImportPreview {
  total: number
  new_count: number
  duplicate_count: number
  failed_count: number
  apis: ImportPreviewItem[]
}

export interface ImportPreviewItem {
  method: string
  path: string
  name: string
  status: 'new' | 'duplicate' | 'failed'
  error?: string
  module_name?: string
  selected: boolean
}

export interface ImportResult {
  total: number
  created: number
  skipped: number
  failed: number
  errors?: string[]
}

export interface ExportRequest {
  format: 'swagger2' | 'openapi3' | 'postman' | 'markdown'
  module_id?: number
  api_ids?: number[]
  include_draft?: boolean
  include_deprecated?: boolean
  title?: string
  description?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export const HTTP_METHODS = [
  { value: HttpMethod.GET, label: 'GET' },
  { value: HttpMethod.POST, label: 'POST' },
  { value: HttpMethod.PUT, label: 'PUT' },
  { value: HttpMethod.DELETE, label: 'DELETE' },
  { value: HttpMethod.PATCH, label: 'PATCH' },
  { value: HttpMethod.HEAD, label: 'HEAD' },
  { value: HttpMethod.OPTIONS, label: 'OPTIONS' }
] as const

export const API_STATUSES = [
  { value: ApiStatus.DRAFT, label: '草稿' },
  { value: ApiStatus.ENABLED, label: '启用' },
  { value: ApiStatus.DISABLED, label: '禁用' },
  { value: ApiStatus.DEPRECATED, label: '废弃' }
] as const

export const BODY_TYPES = [
  { value: BodyType.NONE, label: 'none' },
  { value: BodyType.JSON, label: 'JSON' },
  { value: BodyType.FORM_DATA, label: 'form-data' },
  { value: BodyType.X_WWW_FORM_URLENCODED, label: 'x-www-form-urlencoded' },
  { value: BodyType.RAW, label: 'raw' },
  { value: BodyType.XML, label: 'XML' },
  { value: BodyType.BINARY, label: 'Binary' }
] as const

export const PARAM_TYPES = [
  { value: ParamType.STRING, label: 'String' },
  { value: ParamType.INTEGER, label: 'Integer' },
  { value: ParamType.FLOAT, label: 'Float' },
  { value: ParamType.BOOLEAN, label: 'Boolean' },
  { value: ParamType.ARRAY, label: 'Array' },
  { value: ParamType.OBJECT, label: 'Object' },
  { value: ParamType.FILE, label: 'File' }
] as const

export const METHOD_COLORS: Record<string, { bg: string; text: string }> = {
  GET: { bg: '#E8F5E9', text: '#2E7D32' },
  POST: { bg: '#E3F2FD', text: '#1565C0' },
  PUT: { bg: '#FFF3E0', text: '#E65100' },
  DELETE: { bg: '#FFEBEE', text: '#C62828' },
  PATCH: { bg: '#FFF8E1', text: '#F57F17' },
  HEAD: { bg: '#F3E5F5', text: '#6A1B9A' },
  OPTIONS: { bg: '#ECEFF1', text: '#37474F' }
}

export const STATUS_COLORS: Record<string, { type: string }> = {
  draft: { type: 'warning' },
  enabled: { type: 'success' },
  disabled: { type: 'info' },
  deprecated: { type: 'danger' }
}

export const CONFLICT_STRATEGIES = [
  { value: 'skip', label: '跳过重复' },
  { value: 'overwrite', label: '覆盖更新' },
  { value: 'copy', label: '创建副本' },
  { value: 'manual', label: '手动选择' }
] as const

export const PRE_ACTION_TYPES = [
  { value: 'set_variable', label: '变量设置', icon: 'Coin' },
  { value: 'wait', label: '等待时间', icon: 'Timer' },
  { value: 'script', label: '前置脚本', icon: 'Document' },
  { value: 'database', label: '数据库操作', icon: 'Coin' }
] as const

export const POST_ACTION_TYPES = [
  { value: 'extract', label: '参数提取', icon: 'Download' },
  { value: 'script', label: '后置脚本', icon: 'Document' },
  { value: 'database', label: '数据库操作', icon: 'Coin' }
] as const

export const ASSERTION_TYPES = [
  { value: 'status_code', label: '状态码' },
  { value: 'response_time', label: '响应时间' },
  { value: 'header', label: '响应头' },
  { value: 'body', label: '响应体' },
  { value: 'json_schema', label: 'JSON Schema' },
  { value: 'script', label: 'Python脚本' }
] as const

export const EXTRACT_TYPES = [
  { value: 'jsonpath', label: 'JSONPath' },
  { value: 'regex', label: '正则表达式' },
  { value: 'header', label: '按名称提取' },
  { value: 'cookie', label: '按名称提取' },
  { value: 'direct', label: '直接提取' }
] as const

export const SOURCE_TYPE_MAP: Record<string, string> = {
  response_json: 'jsonpath',
  response_text: 'regex',
  response_header: 'header',
  response_cookie: 'cookie',
  elapsed_time: 'direct',
}

export const EXTRACT_SOURCES = [
  { value: 'response_json', label: '响应JSON' },
  { value: 'response_text', label: '响应文本' },
  { value: 'response_header', label: '响应头' },
  { value: 'response_cookie', label: '响应Cookie' },
  { value: 'elapsed_time', label: '耗时' }
] as const

export const VARIABLE_SCOPES = [
  { value: 'temp', label: '临时变量' },
  { value: 'module', label: '模块变量' },
  { value: 'env', label: '环境变量' },
  { value: 'global', label: '全局变量' }
] as const

export const ASSERTION_OPERATORS = [
  { value: 'eq', label: '等于' },
  { value: 'neq', label: '不等于' },
  { value: 'gt', label: '大于' },
  { value: 'lt', label: '小于' },
  { value: 'gte', label: '大于等于' },
  { value: 'lte', label: '小于等于' },
  { value: 'contains', label: '包含' },
  { value: 'not_contains', label: '不包含' },
  { value: 'starts_with', label: '开头为' },
  { value: 'ends_with', label: '结尾为' },
  { value: 'matches', label: '匹配正则' },
  { value: 'not_matches', label: '不匹配正则' },
  { value: 'is_empty', label: '为空' },
  { value: 'not_empty', label: '不为空' },
  { value: 'length_eq', label: '长度等于' },
  { value: 'length_gt', label: '长度大于' },
  { value: 'length_lt', label: '长度小于' },
  { value: 'length_gte', label: '长度大于等于' },
  { value: 'length_lte', label: '长度小于等于' },
  { value: 'in', label: '在列表中' },
  { value: 'not_in', label: '不在列表中' },
  { value: 'between', label: '在范围内' },
  { value: 'type_eq', label: '类型为' },
  { value: 'has_key', label: '包含字段' },
  { value: 'not_has_key', label: '不包含字段' }
] as const

export const COMPARISON_OPERATORS = ASSERTION_OPERATORS

export const SEVERITY_LEVELS = [
  { value: 'critical', label: '严重', type: 'danger' },
  { value: 'warning', label: '警告', type: 'warning' },
  { value: 'info', label: '信息', type: 'info' }
] as const

export const TIMEOUT_PRESETS = [
  {
    label: '快速接口',
    connect_timeout: 3000,
    read_timeout: 10000,
    write_timeout: 5000,
    pool_timeout: 3000,
    sample_timeout: 15000,
    sql_timeout: 10000,
    script_timeout: 5000
  },
  {
    label: '标准接口',
    connect_timeout: 5000,
    read_timeout: 30000,
    write_timeout: 10000,
    pool_timeout: 5000,
    sample_timeout: 60000,
    sql_timeout: 30000,
    script_timeout: 10000
  },
  {
    label: '慢接口',
    connect_timeout: 10000,
    read_timeout: 120000,
    write_timeout: 30000,
    pool_timeout: 5000,
    sample_timeout: 180000,
    sql_timeout: 60000,
    script_timeout: 30000
  },
  {
    label: '文件上传',
    connect_timeout: 10000,
    read_timeout: 300000,
    write_timeout: 60000,
    pool_timeout: 5000,
    sample_timeout: 420000,
    sql_timeout: 30000,
    script_timeout: 10000
  },
  {
    label: '数据库查询',
    connect_timeout: 5000,
    read_timeout: 30000,
    write_timeout: 10000,
    pool_timeout: 5000,
    sample_timeout: 300000,
    sql_timeout: 120000,
    script_timeout: 30000
  }
] as const

export const EXPORT_FORMATS = [
  { value: 'swagger2', label: 'Swagger 2.0' },
  { value: 'openapi3', label: 'OpenAPI 3.0' },
  { value: 'postman', label: 'Postman Collection' },
  { value: 'markdown', label: 'Markdown' }
] as const
