# 测试用例管理系统前端实施计划（续）

> **注意：数据驱动功能已从系统中移除。** 文档中涉及数据驱动（DataSource、数据源配置、数据驱动执行）的内容已不再适用，功能由步骤级条件控制(if/for/while)替代。

> 本文档是主实施计划的补充，包含阶段二、三、四的任务概要

---

## 阶段二：核心功能（续）

### Task 9: 创建模块树组件

**Files:**
- Create: `frontend/src/views/testcase/components/TestCaseTree.vue`

**功能：**
- 显示测试用例模块树
- 支持模块选择和筛选
- 支持模块的创建、编辑、删除

**关键实现：**
- 使用Element Plus的el-tree组件
- 支持拖拽排序
- 右键菜单操作

### Task 10: 创建测试用例详情页

**Files:**
- Create: `frontend/src/views/testcase/TestCaseDetail.vue`

**功能：**
- 标签页布局（基本信息、测试步骤、数据源、执行记录）
- 基本信息编辑表单
- 保存和执行按钮

**关键实现：**
- 使用el-tabs组件
- 表单验证
- 自动保存草稿

### Task 11: 创建步骤编辑器组件

**Files:**
- Create: `frontend/src/views/testcase/components/StepEditor.vue`

**功能：**
- 步骤列表展示（可拖拽排序）
- 添加新步骤（关联已有API）
- 编辑步骤（覆盖API配置）
- 删除步骤
- 启用/禁用步骤

**关键实现：**
- 使用vuedraggable实现拖拽
- 步骤卡片式展示
- API选择对话框

---

## 阶段三：执行功能（预计2-3天）

### Task 12: 创建执行对话框组件

**Files:**
- Create: `frontend/src/views/testcase/components/ExecutionDialog.vue`

**功能：**
- 选择执行环境
- 配置执行参数（失败策略、超时时间、步骤间隔）
- 选择数据源（数据驱动）
- 显示执行进度
- 执行完成后跳转到执行记录

**关键实现：**
- 模态对话框
- 环境选择下拉框
- 参数配置表单
- 执行进度条

### Task 13: 实现详情页执行功能

**Files:**
- Modify: `frontend/src/views/testcase/TestCaseDetail.vue`

**功能：**
- 在详情页添加执行按钮
- 调用执行对话框
- 处理执行结果

**关键实现：**
- 引入ExecutionDialog组件
- 执行成功后跳转到执行记录详情

### Task 14: 实现列表页批量执行功能

**Files:**
- Modify: `frontend/src/views/testcase/TestCaseList.vue`

**功能：**
- 在批量操作栏添加批量执行按钮
- 调用执行对话框
- 处理批量执行结果

**关键实现：**
- 传递选中的测试用例ID列表
- 批量执行API调用

### Task 15: 创建执行记录组件

**Files:**
- Create: `frontend/src/views/testcase/components/ExecutionReport.vue`

**功能：**
- 执行记录列表展示
- 执行记录详情查看
- 导出执行报告

**关键实现：**
- 使用el-table展示执行记录
- 执行状态标签
- 导出按钮（HTML/Excel格式）

---

## 阶段四：高级功能（预计2-3天）

### Task 16: 创建数据源配置组件

**Files:**
- Create: `frontend/src/views/testcase/components/DataSourceConfig.vue`

**功能：**
- 数据源列表展示
- 创建数据源（CSV/JSON/数据库）
- 编辑数据源
- 删除数据源
- 预览数据源

**关键实现：**
- 数据源类型选择
- 配置表单（根据类型动态显示）
- 数据预览表格

### Task 17: 实现数据驱动执行

**Files:**
- Modify: `frontend/src/views/testcase/components/ExecutionDialog.vue`

**功能：**
- 在执行对话框中添加数据源选择
- 数据驱动执行逻辑
- 显示数据迭代进度

**关键实现：**
- 数据源下拉选择
- 迭代次数显示
- 每次迭代的执行结果

### Task 18: 实现定时执行配置（可选）

**Files:**
- Create: `frontend/src/views/testcase/components/ScheduleConfig.vue`

**功能：**
- 定时任务配置表单
- Cron表达式生成器
- 定时任务列表

**关键实现：**
- Cron表达式编辑器
- 定时任务管理

### Task 19: 实现执行报告导出增强

**Files:**
- Modify: `frontend/src/views/testcase/components/ExecutionReport.vue`

**功能：**
- HTML报告模板
- Excel报告生成
- 报告内容配置（包含请求/响应详情）

**关键实现：**
- 报告模板设计
- 数据导出逻辑

---

## 总结

本实施计划采用渐进式开发策略，分为四个阶段：

1. **阶段一（基础架构）**：完成API封装、Mock数据、状态管理和路由配置
2. **阶段二（核心功能）**：完成列表页、详情页和步骤编辑器
3. **阶段三（执行功能）**：完成执行对话框、批量执行和执行记录
4. **阶段四（高级功能）**：完成数据驱动、定时执行和报告导出

每个阶段都能独立交付可用的功能，降低开发风险，便于测试和验证。

**预计总工时：** 8-12天

**关键里程碑：**
- 阶段一完成：前端可以独立运行，使用Mock数据
- 阶段二完成：可以创建和编辑测试用例
- 阶段三完成：可以执行测试用例并查看结果
- 阶段四完成：支持高级功能，完整交付
