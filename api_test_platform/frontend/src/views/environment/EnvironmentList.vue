<template>
  <div class="page-layout">
    <PageHeader
      title="环境管理"
      subtitle="管理测试环境的配置信息，包括服务器、数据库和变量"
    />

    <ToolBar>
      <template #left>
        <el-button type="primary" class="btn-primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建环境
        </el-button>
      </template>

      <template #right>
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
      </template>
    </ToolBar>

    <DataTable
      :loading="loading"
      :data="environments"
      :total="total"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
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
          <span class="time-text">{{ formatDate(row.created_at) }}</span>
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
    </DataTable>

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
import PageHeader from '@/components/common/PageHeader.vue'
import ToolBar from '@/components/common/ToolBar.vue'
import DataTable from '@/components/common/DataTable.vue'

const router = useRouter()
const store = useEnvironmentStore()

const searchText = ref('')
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)

const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

const createForm = ref({ name: '', description: '' })
const editForm = ref({ id: 0, name: '', description: '' })

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入环境名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

const currentPage = ref(1)
const pageSize = ref(20)

const environments = computed(() => store.environments)
const total = computed(() => store.total)

function indexMethod(index: number) {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

onMounted(async () => {
  await fetchEnvironments()
})

watch([currentPage, pageSize], () => {
  fetchEnvironments()
})

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchText, (newVal) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchEnvironments()
  }, 300)
})

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

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

function handleView(row: Environment) {
  router.push(`/environments/${row.id}`)
}

function handleEdit(row: Environment) {
  editForm.value = {
    id: row.id,
    name: row.name,
    description: row.description || ''
  }
  showEditDialog.value = true
}

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
  } finally {
    submitting.value = false
  }
}

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
  } finally {
    submitting.value = false
  }
}

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
      // error handled by interceptor
    }
  }
}

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
      // error handled by interceptor
    }
  }
}

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
      // error handled by interceptor
    }
  }
}
</script>

<style scoped>
.page-layout {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 100%;
  background-color: var(--color-surface-200);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  background-color: var(--color-primary-500);
  border: 1px solid var(--color-primary-500);
  border-radius: 0.375rem;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background-color: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.search-input {
  width: 300px;
}

.env-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.default-tag {
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: var(--color-neutral-900);
}

.description-text {
  color: var(--color-neutral-500);
}

.time-text {
  font-size: 13px;
  color: var(--color-neutral-500);
}

@media (max-width: 768px) {
  .page-layout {
    padding: 1rem;
  }

  .toolbar-container {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-right {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }
}
</style>