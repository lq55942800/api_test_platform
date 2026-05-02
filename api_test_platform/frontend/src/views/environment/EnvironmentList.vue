<template>
  <div class="environment-list">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">环境管理</h1>
        <p class="page-subtitle">管理测试环境的配置信息，包括服务器、数据库和变量</p>
      </div>
    </div>

    <!-- 工具栏区域 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建环境
      </el-button>
      <el-input
        v-model="searchText"
        placeholder="搜索环境名称/描述"
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 环境列表表格 -->
    <div class="table-container">
      <el-table
        :data="environments"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="70" align="center" :index="indexMethod" />
        <el-table-column prop="name" label="环境名称" sortable min-width="200">
          <template #default="{ row }">
            <div class="env-name">
              <el-tag v-if="row.is_default" type="success" size="small" class="default-tag">默认</el-tag>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300">
          <template #default="{ row }">
            <span class="description-text">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="服务数" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.services?.length || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            <span>{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleCopy(row)">复制</el-button>
            <el-button
              v-if="!row.is_default"
              type="primary"
              link
              @click="handleSetDefault(row)"
            >
              设为默认
            </el-button>
            <el-button
              type="danger"
              link
              @click="handleDelete(row)"
              :disabled="environments.length <= 1"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
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

    <!-- 新建环境对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建环境"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="createForm"
        :rules="formRules"
        ref="createFormRef"
        label-width="80px"
      >
        <el-form-item label="环境名称" prop="name">
          <el-input
            v-model="createForm.name"
            placeholder="请输入环境名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入描述"
            maxlength="500"
            show-word-limit
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑环境对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑环境"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="editForm"
        :rules="formRules"
        ref="editFormRef"
        label-width="80px"
      >
        <el-form-item label="环境名称" prop="name">
          <el-input
            v-model="editForm.name"
            placeholder="请输入环境名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入描述"
            maxlength="500"
            show-word-limit
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useEnvironmentStore } from '@/stores/environment'
import type { Environment } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const store = useEnvironmentStore()

// 状态
const searchText = ref('')
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)

// 表单引用
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单数据
const createForm = ref({ name: '', description: '' })
const editForm = ref({ id: 0, name: '', description: '' })

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入环境名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 环境列表
const environments = computed(() => store.environments)
const total = computed(() => store.total)

// 序号方法
function indexMethod(index: number) {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 初始化
onMounted(async () => {
  await fetchEnvironments()
})

// 监听分页变化
watch([currentPage, pageSize], () => {
  fetchEnvironments()
})

// 监听搜索变化（防抖）
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchText, (newVal) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchEnvironments()
  }, 300)
})

// 获取环境列表
async function fetchEnvironments() {
  loading.value = true
  try {
    await store.fetchEnvironments({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value || undefined
    })
  } finally {
    loading.value = false
  }
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

// 查看环境详情
function handleView(row: Environment) {
  router.push(`/environments/${row.id}`)
}

// 编辑环境
function handleEdit(row: Environment) {
  editForm.value = {
    id: row.id,
    name: row.name,
    description: row.description || ''
  }
  showEditDialog.value = true
}

// 创建环境
async function handleCreate() {
  const valid = await createFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await store.createEnvironment(createForm.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = { name: '', description: '' }
    await fetchEnvironments()
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}

// 更新环境
async function handleUpdate() {
  const valid = await editFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await store.updateEnvironment(editForm.value.id, {
      name: editForm.value.name,
      description: editForm.value.description
    })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    await fetchEnvironments()
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}

// 复制环境
async function handleCopy(row: Environment) {
  try {
    await ElMessageBox.confirm(`确定要复制环境"${row.name}"吗？`, '提示', {
      type: 'warning'
    })
    await store.copyEnvironment(row.id)
    ElMessage.success('复制成功')
    await fetchEnvironments()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 设置默认环境
async function handleSetDefault(row: Environment) {
  try {
    await ElMessageBox.confirm(`确定要将"${row.name}"设为默认环境吗？`, '提示', {
      type: 'warning'
    })
    await store.setDefaultEnvironment(row.id)
    ElMessage.success('设置成功')
    await fetchEnvironments()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 删除环境
async function handleDelete(row: Environment) {
  try {
    await ElMessageBox.confirm(
      `确定要删除环境"${row.name}"吗？删除后所有服务配置将被清除。`,
      '警告',
      { type: 'warning' }
    )
    await store.deleteEnvironment(row.id)
    ElMessage.success('删除成功')
    await fetchEnvironments()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}
</script>

<style scoped>
.environment-list {
  padding: 24px;
  background-color: #ffffff;
  min-height: 100vh;
}

/* 页面标题区域 */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  padding: 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #6b6375;
  margin: 0;
}

/* 工具栏区域 */
.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-input {
  width: 400px;
}

/* 表格容器 */
.table-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 分页容器 */
.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  background-color: #ffffff;
  border-top: 1px solid #e5e4e7;
}

/* 环境名称样式 */
.env-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.default-tag {
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: #08060d;
}

/* 描述文本样式 */
.description-text {
  color: #6b6375;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }
}
</style>
