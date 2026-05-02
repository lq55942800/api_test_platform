/**
 * 环境管理模块类型定义
 */

// 环境接口
export interface Environment {
  id: number;
  team_id: number;
  name: string;
  description?: string;
  is_default: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
  service_count?: number;
  services?: Service[];
  variables?: EnvVariable[];
}

// 环境创建请求
export interface EnvironmentCreate {
  name: string;
  description?: string;
}

// 环境更新请求
export interface EnvironmentUpdate {
  name?: string;
  description?: string;
}

// 服务接口
export interface Service {
  id: number;
  environment_id: number;
  name: string;
  service_type?: 'microservice' | 'module' | 'third_party';
  description?: string;
  sort_order: number;
  created_at: string;
  updated_at?: string;
  servers?: Server[];
  databases?: Database[];
}

// 服务创建请求
export interface ServiceCreate {
  name: string;
  service_type?: 'microservice' | 'module' | 'third_party';
  description: string;
}

// 服务更新请求
export interface ServiceUpdate {
  name?: string;
  service_type?: 'microservice' | 'module' | 'third_party';
  description?: string;
}

// 服务器配置接口
export interface Server {
  id: number;
  service_id: number;
  name: string;
  host: string;
  port?: number;
  protocol: 'http' | 'https';
  base_path?: string;
  ssl_config?: Record<string, any>;
  headers?: Record<string, string>;
  timeout: number;
  base_url: string;
  created_at: string;
  updated_at?: string;
}

// 服务器创建请求
export interface ServerCreate {
  name?: string;
  host: string;
  port?: number;
  protocol?: 'http' | 'https';
  base_path?: string;
  ssl_config?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
}

// 服务器更新请求
export interface ServerUpdate {
  name?: string;
  host?: string;
  port?: number;
  protocol?: 'http' | 'https';
  base_path?: string;
  ssl_config?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
}

// 数据库配置接口
export interface Database {
  id: number;
  service_id: number;
  name: string;
  db_type: 'mysql' | 'postgresql' | 'mongodb' | 'redis' | 'sqlserver' | 'oracle';
  host: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  charset?: string;
  extra_config?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

// 数据库创建请求
export interface DatabaseCreate {
  name: string;
  db_type: 'mysql' | 'postgresql' | 'mongodb' | 'redis' | 'sqlserver' | 'oracle';
  host: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  charset?: string;
  extra_config?: Record<string, any>;
  is_encrypted?: boolean;
}

// 数据库更新请求
export interface DatabaseUpdate {
  name?: string;
  db_type?: 'mysql' | 'postgresql' | 'mongodb' | 'redis' | 'sqlserver' | 'oracle';
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  charset?: string;
  extra_config?: Record<string, any>;
}

// 环境变量接口
export interface EnvVariable {
  id: number;
  environment_id: number;
  key: string;
  value?: string;
  value_type: 'string' | 'number' | 'boolean';
  is_encrypted: boolean;
  description?: string;
  created_at: string;
  updated_at?: string;
}

// 环境变量创建请求
export interface EnvVariableCreate {
  key: string;
  value?: string;
  value_type?: 'string' | 'number' | 'boolean';
  is_encrypted?: boolean;
  description?: string;
}

// 环境变量更新请求
export interface EnvVariableUpdate {
  key?: string;
  value?: string;
  value_type?: 'string' | 'number' | 'boolean';
  is_encrypted?: boolean;
  description?: string;
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// 数据库类型选项
export const DATABASE_TYPES = [
  { value: 'mysql', label: 'MySQL', defaultPort: 3306 },
  { value: 'postgresql', label: 'PostgreSQL', defaultPort: 5432 },
  { value: 'mongodb', label: 'MongoDB', defaultPort: 27017 },
  { value: 'redis', label: 'Redis', defaultPort: 6379 },
  { value: 'sqlserver', label: 'SQL Server', defaultPort: 1433 },
  { value: 'oracle', label: 'Oracle', defaultPort: 1521 }
] as const;

// 服务类型选项
export const SERVICE_TYPES = [
  { value: 'microservice', label: '微服务' },
  { value: 'module', label: '应用模块' },
  { value: 'third_party', label: '第三方服务' }
] as const;

// 变量类型选项
export const VARIABLE_TYPES = [
  { value: 'string', label: 'String' },
  { value: 'number', label: 'Number' },
  { value: 'boolean', label: 'Boolean' }
] as const;
