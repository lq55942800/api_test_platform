<template>
  <div class="environment-detail">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/environments' }">环境管理</el-breadcrumb-item>
        <el-breadcrumb-item>{{ currentEnvironment?.name || '环境详情' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 环境信息卡片 -->
    <div class="env-info-card" v-loading="loading">
      <div class="env-header">
        <div class="env-title">
          <h2>{{ currentEnvironment?.name }}</h2>
          <el-tag v-if="currentEnvironment?.is_default" type="success" size="small">默认</el-tag>
        </div>
        <div class="env-actions">
          <el-button @click="handleEdit">编辑</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </div>
      </div>
      <div class="env-meta">
        <div class="meta-item">
          <span class="meta-label">描述：</span>
          <span class="meta-value">{{ currentEnvironment?.description || '-' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">创建时间：</span>
          <span class="meta-value">{{ formatDate(currentEnvironment?.created_at || '') }}</span>
        </div>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="tab-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="服务列表" name="services">
          <div class="services-content">
            <div class="toolbar">
              <el-button type="primary" @click="showAddServiceDialog = true">
                <el-icon><Plus /></el-icon>
                添加服务
              </el-button>
              <el-input
                v-model="serviceSearchText"
                placeholder="搜索服务名称"
                clearable
                class="search-input"
                style="width: 250px"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <!-- 服务列表 -->
            <div class="service-list" v-if="services.length > 0">
              <div
                v-for="service in services"
                :key="service.id"
                class="service-card"
              >
                <div class="service-header">
                  <div class="service-title">
                    <el-icon class="expand-icon" @click="toggleService(service.id)">
                      <component :is="expandedServices.includes(service.id) ? 'ArrowDown' : 'ArrowRight'" />
                    </el-icon>
                    <span class="service-name">{{ service.name }}</span>
                    <el-tag v-if="service.service_type" size="small" type="info">
                      {{ getServiceTypeLabel(service.service_type) }}
                    </el-tag>
                  </div>
                  <div class="service-actions">
                    <el-button type="primary" link @click="handleEditService(service)">编辑</el-button>
                    <el-button type="primary" link @click="handleCopyService(service)">复制</el-button>
                    <el-button type="danger" link @click="handleDeleteService(service)">删除</el-button>
                  </div>
                </div>
                
                <div v-if="expandedServices.includes(service.id)" class="service-content">
                  <div class="info-row">
                    <span class="info-label">服务器：</span>
                    <span class="info-value">
                      {{ service.servers?.map(s => buildBaseUrl(s)).join(', ') || '-' }}
                    </span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">数据库：</span>
                    <span class="info-value">
                      {{ service.databases?.map(d => d.name).join(', ') || '-' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
              <el-empty description="暂无服务，点击添加服务开始配置" />
            </div>

            <!-- 分页 -->
            <div class="pagination-container" v-if="serviceTotal > 0">
              <el-pagination
                v-model:current-page="serviceCurrentPage"
                v-model:page-size="servicePageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="serviceTotal"
                layout="total, sizes, prev, pager, next, jumper"
                background
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="环境变量" name="variables">
          <div class="variables-content">
            <div class="toolbar">
              <el-button type="primary" @click="showAddVariableDialog = true">
                <el-icon><Plus /></el-icon>
                添加变量
              </el-button>
            </div>

            <!-- 变量列表 -->
            <div class="variable-list" v-if="variables.length > 0">
              <el-table :data="variables" stripe>
                <el-table-column prop="key" min-width="200">
                  <template #header>
                    <el-tooltip placement="top" :show-after="300">
                      <template #content>
                        <div class="syntax-tooltip">
                          <div>变量引用语法：</div>
                          <div><code v-pre>{{env.{变量名}}}</code> - 环境变量</div>
                          <div><code v-pre>{{{服务名}.{变量名}}}</code> - 服务变量</div>
                          <div><code v-pre>{{{服务名}.baseUrl}}</code> - 服务baseUrl</div>
                          <div><code v-pre>{{{服务名}.db.{数据库名}}}</code> - 数据库连接串</div>
                        </div>
                      </template>
                      <span class="header-with-tip">变量名 <el-icon><QuestionFilled /></el-icon></span>
                    </el-tooltip>
                  </template>
                  <template #default="{ row }">
                    <span>{{ row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="变量值" min-width="300">
                  <template #default="{ row }">
                    <span v-if="row.is_encrypted">********</span>
                    <span v-else>{{ row.value || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value_type" label="类型" width="100" align="center" />
                <el-table-column prop="is_encrypted" label="加密" width="80" align="center">
                  <template #default="{ row }">
                    <el-icon v-if="row.is_encrypted" color="#10b981"><Check /></el-icon>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button type="primary" link @click="handleEditVariable(row)">编辑</el-button>
                    <el-button type="danger" link @click="handleDeleteVariable(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
              <el-empty description="暂无变量，点击添加变量开始配置" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 添加服务对话框 -->
    <el-dialog
      v-model="showAddServiceDialog"
      title="添加服务"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="serviceForm"
        :rules="serviceRules"
        ref="serviceFormRef"
        label-width="80px"
      >
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="serviceForm.name" placeholder="请输入服务名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="服务类型" prop="service_type">
          <el-select v-model="serviceForm.service_type" placeholder="请选择服务类型">
            <el-option
              v-for="item in SERVICE_TYPES"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="服务描述" prop="description">
          <el-input
            v-model="serviceForm.description"
            type="textarea"
            placeholder="请输入服务描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddServiceDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddService" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑变量对话框 -->
    <el-dialog
      v-model="showAddVariableDialog"
      :title="editingVariable ? '编辑变量' : '添加变量'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="variableForm"
        :rules="variableRules"
        ref="variableFormRef"
        label-width="80px"
      >
        <el-form-item label="变量名" prop="key">
          <el-input v-model="variableForm.key" placeholder="请输入变量名" maxlength="100" />
        </el-form-item>
        <el-form-item label="变量值" prop="value">
          <el-input v-model="variableForm.value" placeholder="请输入变量值" />
        </el-form-item>
        <el-form-item label="变量类型" prop="value_type">
          <el-select v-model="variableForm.value_type" placeholder="请选择变量类型">
            <el-option
              v-for="item in VARIABLE_TYPES"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="加密存储">
          <el-checkbox v-model="variableForm.is_encrypted">加密存储</el-checkbox>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="variableForm.description" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddVariableDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddVariable" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Check, InfoFilled, QuestionFilled, ArrowDown, ArrowRight, Search } from '@element-plus/icons-vue'
import { useEnvironmentStore } from '@/stores/environment'
import type { Service, EnvVariable, ServiceCreate, EnvVariableCreate } from '@/types/environment'
import { SERVICE_TYPES, VARIABLE_TYPES } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useEnvironmentStore()

// 状态
const loading = ref(false)
const submitting = ref(false)
const activeTab = ref('services')
const expandedServices = ref<number[]>([])
const showAddServiceDialog = ref(false)
const showAddVariableDialog = ref(false)
const editingVariable = ref<EnvVariable | null>(null)

// 表单引用
const serviceFormRef = ref<FormInstance>()
const variableFormRef = ref<FormInstance>()

// 表单数据
const serviceForm = ref<ServiceCreate>({
  name: '',
  service_type: 'microservice',
  description: ''
})

const variableForm = ref<EnvVariableCreate>({
  key: '',
  value: '',
  value_type: 'string',
  is_encrypted: false,
  description: ''
})

// 表单验证规则
const serviceRules: FormRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const variableRules: FormRules = {
  key: [
    { required: true, message: '请输入变量名', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const currentEnvironment = computed(() => store.currentEnvironment)
const services = computed(() => store.services)
const variables = computed(() => store.variables)
const serviceTotal = computed(() => store.serviceTotal)

// 服务分页和搜索
const serviceSearchText = ref('')
const serviceCurrentPage = ref(1)
const servicePageSize = ref(10)

// 监听分页变化
watch([serviceCurrentPage, servicePageSize], () => {
  fetchServices()
})

// 监听搜索变化（防抖）
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(serviceSearchText, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    serviceCurrentPage.value = 1
    fetchServices()
  }, 300)
})

// 获取服务列表
async function fetchServices() {
  if (!currentEnvironment.value) return
  await store.fetchServices(currentEnvironment.value.id, {
    page: serviceCurrentPage.value,
    page_size: servicePageSize.value,
    search: serviceSearchText.value || undefined
  })
}

// 构建baseUrl
function buildBaseUrl(server: { protocol?: string; host?: string; port?: number; base_path?: string }) {
  if (!server.host) return '-'
  let url = `${server.protocol || 'https'}://${server.host}`
  if (server.port && ![80, 443].includes(server.port)) {
    url += `:${server.port}`
  }
  if (server.base_path) {
    url += server.base_path.startsWith('/') ? server.base_path : `/${server.base_path}`
  }
  return url
}

// 初始化
onMounted(async () => {
  const envId = Number(route.params.id)
  if (envId) {
    loading.value = true
    try {
      await store.fetchEnvironment(envId)
      await fetchServices()
    } finally {
      loading.value = false
    }
  }
})

// 格式化日期
function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 获取服务类型标签
function getServiceTypeLabel(type: string) {
  const item = SERVICE_TYPES.find(t => t.value === type)
  return item?.label || type
}

// 切换服务展开状态
function toggleService(serviceId: number) {
  const index = expandedServices.value.indexOf(serviceId)
  if (index > -1) {
    expandedServices.value.splice(index, 1)
  } else {
    expandedServices.value.push(serviceId)
  }
}

// 编辑环境
function handleEdit() {
  if (!currentEnvironment.value) return
  router.push(`/environments/${currentEnvironment.value.id}/edit`)
}

// 删除环境
async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除环境"${currentEnvironment.value?.name}"吗？删除后所有服务配置将被清除。`,
      '警告',
      { type: 'warning' }
    )
    await store.deleteEnvironment(currentEnvironment.value!.id)
    ElMessage.success('删除成功')
    router.push('/environments')
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 添加服务
async function handleAddService() {
  const valid = await serviceFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await store.createService(currentEnvironment.value!.id, serviceForm.value)
    ElMessage.success('添加成功')
    showAddServiceDialog.value = false
    serviceForm.value = {
      name: '',
      service_type: 'microservice',
      description: ''
    }
    await fetchServices()
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}

// 编辑服务
function handleEditService(service: Service) {
  router.push(`/environments/${currentEnvironment.value!.id}/services/${service.id}/edit`)
}

// 删除服务
async function handleDeleteService(service: Service) {
  try {
    await ElMessageBox.confirm(
      `确定要删除服务"${service.name}"吗？`,
      '警告',
      { type: 'warning' }
    )
    await store.deleteService(service.id)
    ElMessage.success('删除成功')
    await fetchServices()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 复制服务
async function handleCopyService(service: Service) {
  try {
    await ElMessageBox.confirm(
      `确定要复制服务"${service.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await store.copyService(service.id)
    ElMessage.success('复制成功')
    await fetchServices()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 添加/编辑变量
async function handleAddVariable() {
  const valid = await variableFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (editingVariable.value) {
      await store.updateVariable(editingVariable.value.id, variableForm.value)
      ElMessage.success('更新成功')
    } else {
      await store.createVariable(currentEnvironment.value!.id, variableForm.value)
      ElMessage.success('添加成功')
    }
    showAddVariableDialog.value = false
    editingVariable.value = null
    variableForm.value = {
      key: '',
      value: '',
      value_type: 'string',
      is_encrypted: false,
      description: ''
    }
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}

// 编辑变量
function handleEditVariable(variable: EnvVariable) {
  editingVariable.value = variable
  variableForm.value = {
    key: variable.key,
    value: variable.value || '',
    value_type: variable.value_type || 'string',
    is_encrypted: variable.is_encrypted || false,
    description: variable.description || ''
  }
  showAddVariableDialog.value = true
}

// 删除变量
async function handleDeleteVariable(variable: EnvVariable) {
  try {
    await ElMessageBox.confirm(
      `确定要删除变量"${variable.key}"吗？`,
      '警告',
      { type: 'warning' }
    )
    await store.deleteVariable(variable.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}
</script>

<style scoped>
.environment-detail {
  padding: 24px;
  background-color: #f9fafb;
  min-height: 100vh;
}

/* 面包屑导航 */
.breadcrumb {
  margin-bottom: 24px;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 环境信息卡片 */
.env-info-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
}

.env-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.env-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.env-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
}

.env-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  font-size: 14px;
  color: #6b6375;
  margin-right: 8px;
}

.meta-value {
  font-size: 14px;
  color: #08060d;
}

/* Tab容器 */
.tab-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

/* 工具栏 */
.toolbar {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 服务列表 */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.service-card {
  background-color: #f9fafb;
  border: 1px solid #e5e4e7;
  border-radius: 8px;
  padding: 16px 24px;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-icon {
  cursor: pointer;
  color: #6b6375;
}

.expand-icon:hover {
  color: #aa3bff;
}

.service-name {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
}

.service-content {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e4e7;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-label {
  font-size: 14px;
  color: #6b6375;
  margin-right: 8px;
  min-width: 80px;
}

.info-value {
  font-size: 14px;
  color: #08060d;
}

/* 变量列表 */
.variable-list {
  margin-bottom: 24px;
}

/* 变量名表头hover提示 */
.header-with-tip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: help;
}

.header-with-tip .el-icon {
  color: #6b6375;
  font-size: 14px;
}

.syntax-tooltip {
  font-size: 13px;
  line-height: 1.8;
}

.syntax-tooltip code {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: ui-monospace, Consolas, monospace;
}

/* 空状态 */
.empty-state {
  padding: 48px 0;
}

/* 分页容器 */
.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .env-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .env-actions {
    width: 100%;
    display: flex;
    gap: 8px;
  }
}
</style>
