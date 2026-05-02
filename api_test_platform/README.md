# AutoTest API 测试平台

一个功能强大的API测试平台，支持环境管理、API管理、测试用例执行、断言处理等核心功能。

## 项目结构

```
api_test_platform/
├── backend/                    # 后端服务
│   └── app/
│       ├── api/               # API路由
│       │   ├── api_management.py      # API管理接口
│       │   ├── environment.py         # 环境管理接口
│       │   ├── execution.py           # 执行接口
│       │   ├── test_case.py           # 测试用例接口
│       │   └── test_case_module.py    # 测试用例模块接口
│       ├── core/               # 核心配置
│       ├── db/                 # 数据库
│       ├── models/             # 数据模型
│       ├── schemas/            # Pydantic schemas
│       ├── services/           # 业务逻辑服务
│       │   ├── assertions/     # 断言类型
│       │   │   ├── body_assertion.py      # 响应体断言
│       │   │   ├── header_assertion.py     # 响应头断言
│       │   │   ├── jsonpath_assertion.py   # JSONPath断言
│       │   │   ├── json_schema_assertion.py # JSON Schema断言
│       │   │   ├── regex_assertion.py      # 正则断言
│       │   │   ├── status_code_assertion.py # 状态码断言
│       │   │   ├── xml_assertion.py        # XML断言
│       │   │   └── ...                     # 其他断言类型
│       │   ├── engines/        # 执行引擎
│       │   │   ├── assertion_engine.py     # 断言引擎
│       │   │   ├── post_processor_engine.py # 后置处理器
│       │   │   ├── pre_processor_engine.py  # 前置处理器
│       │   │   ├── timeout_manager.py       # 超时管理
│       │   │   └── variable_manager.py      # 变量管理
│       │   ├── extractors/      # 数据提取器
│       │   │   ├── jsonpath_extractor.py    # JSONPath提取
│       │   │   ├── regex_extractor.py      # 正则提取
│       │   │   └── ...
│       │   ├── processors/      # 处理器
│       │   │   ├── condition_processor.py   # 条件处理器
│       │   │   ├── script_processor.py      # 脚本处理器
│       │   │   ├── variable_processor.py   # 变量处理器
│       │   │   └── ...
│       │   └── ...
│       └── main.py             # FastAPI入口
│
└── frontend/                   # 前端服务
    └── src/
        ├── api/               # API调用
        ├── router/            # 路由配置
        ├── stores/            # Pinia状态管理
        ├── types/             # TypeScript类型定义
        ├── utils/             # 工具函数
        └── views/             # 页面组件
```

## 技术栈

### 后端
- **FastAPI** - 高性能Web框架
- **SQLAlchemy** - ORM数据库访问
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI服务器

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端

## 核心功能

### 1. 环境管理
- 多环境配置（开发、测试、生产）
- 服务配置管理
- 数据库连接配置
- 全局变量管理

### 2. API管理
- API的CRUD操作
- 模块化组织结构
- 支持多种HTTP方法（GET、POST、PUT、DELETE等）
- 请求参数处理（Query、Body、Header、Path）
- 标签管理
- 版本管理

### 3. 前置/后置处理
- **前置处理器**：
  - 参数处理
  - 变量提取
  - 请求头处理
  - Cookie处理
  - 条件判断
  - 数据库操作
  - 脚本执行

- **后置处理器**：
  - 变量提取
  - 结果状态处理
  - Cookie处理

### 4. 断言类型
- 状态码断言
- 响应体断言
- 响应头断言
- JSONPath断言
- JSON Schema断言
- XPath断言
- XML Schema断言
- 正则断言
- MD5断言
- 响应时间断言
- 大小断言
- 脚本自定义断言

### 5. 数据提取器
- JSONPath提取
- 正则提取
- Header提取
- Cookie提取
- CSS选择器提取

### 6. 测试用例执行
- 步骤化执行
- 变量作用域管理
- 断点调试
- 执行结果展示

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
cd api_test_platform/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
cd api_test_platform/frontend
npm install
npm run dev
```

### 访问地址
- 前端：http://localhost:8080
- 后端API文档：http://localhost:8000/docs
- 后端健康检查：http://localhost:8000/health

## API接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 环境管理 | `/api/v1/environments` | 环境配置管理 |
| API管理 | `/api/v1/apis` | API的增删改查 |
| 执行 | `/api/v1/execution` | 测试用例执行 |
| 测试用例 | `/api/v1/test-cases` | 测试用例管理 |
| 测试模块 | `/api/v1/test-case-modules` | 测试用例模块管理 |

## 配置说明

环境变量配置（`.env`）：
```env
DATABASE_URL=sqlite:///./autotest.db
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key
```

## License

MIT License
