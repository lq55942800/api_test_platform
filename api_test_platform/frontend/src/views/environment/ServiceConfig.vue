<template>
  <div class="service-config">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/environments' }">环境管理</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: `/environments/${environmentId}` }">
          {{ environmentName }}
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ isEdit ? '编辑服务' : '新建服务' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <h2>{{ isEdit ? `编辑服务：${service?.name}` : '新建服务' }}</h2>
    </div>

    <div class="config-form" v-loading="loading">
      <!-- 基本信息 -->
      <div class="form-section">
        <div class="section-title">基本信息</div>
        <el-form
          :model="formData"
          :rules="rules"
          ref="formRef"
          label-width="100px"
        >
          <el-form-item label="服务名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入服务名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="服务类型" prop="service_type">
            <el-select v-model="formData.service_type" placeholder="请选择服务类型">
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
              v-model="formData.description"
              type="textarea"
              placeholder="请输入服务描述"
              maxlength="500"
              show-word-limit
              :rows="3"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 服务器配置 -->
      <div class="form-section">
        <div class="section-title">服务器配置</div>
        <el-form
          :model="serverForm"
          :rules="serverRules"
          ref="serverFormRef"
          label-width="100px"
        >
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="协议" prop="protocol">
                <el-select v-model="serverForm.protocol" placeholder="请选择协议">
                  <el-option label="HTTP" value="http" />
                  <el-option label="HTTPS" value="https" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="主机地址" prop="host">
                <el-input
                  v-model="serverForm.host"
                  placeholder="请输入主机地址"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="端口" prop="port">
                <el-input
                  v-model.number="serverForm.port"
                  type="number"
                  :min="1"
                  :max="65535"
                  placeholder="请输入端口号"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="基础路径" prop="base_path">
                <el-input
                  v-model="serverForm.base_path"
                  placeholder="如 /api/v1"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="超时时间" prop="timeout">
                <el-input
                  v-model.number="serverForm.timeout"
                  type="number"
                  :min="0"
                  placeholder="请输入超时时间(毫秒)"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- baseUrl预览 -->
          <div class="base-url-preview">
            <span class="preview-label">预览：</span>
            <code class="preview-url">{{ baseUrlPreview }}</code>
          </div>
        </el-form>
      </div>

      <!-- 数据库配置 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-title">数据库配置</div>
          <el-button type="primary" link @click="showDatabaseDialog = true">
            <el-icon><Plus /></el-icon>
            添加数据库
          </el-button>
        </div>

        <div class="database-list" v-if="databases.length > 0">
          <div
            v-for="db in databases"
            :key="db.id || db.name"
            class="database-card"
          >
            <div class="db-header">
              <div class="db-title">
                <span class="db-name">{{ db.name }}</span>
                <el-tag size="small" :type="getDbTagType(db.db_type)">
                  {{ getDbTypeLabel(db.db_type) }}
                </el-tag>
              </div>
              <div class="db-actions">
                <el-button type="primary" link @click="handleEditDatabase(db)">编辑</el-button>
                <el-button type="danger" link @click="handleDeleteDatabase(db)">删除</el-button>
              </div>
            </div>
            <div class="db-info">
              <code>{{ db.host }}:{{ db.port || getDefaultPort(db.db_type) }}/{{ db.database || '' }}</code>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无数据库配置" :image-size="80" />
      </div>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="submitting">保存</el-button>
      </div>
    </div>

    <!-- 数据库配置对话框 -->
    <DatabaseConfig
      v-model="showDatabaseDialog"
      :database="editingDatabase"
      @save="handleSaveDatabase"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { environmentApi, serverApi, databaseApi } from '@/api/environment'
import { useEnvironmentStore } from '@/stores/environment'
import DatabaseConfig from './DatabaseConfig.vue'
import type {
  Service,
  Server as ServerType,
  Database,
  ServiceCreate,
  ServerCreate,
  DatabaseCreate
} from '@/types/environment'
import { SERVICE_TYPES, DATABASE_TYPES } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useEnvironmentStore()

const envId = computed(() => Number(route.params.envId))
const serviceId = computed(() => route.params.serviceId ? Number(route.params.serviceId) : undefined)
const isEdit = computed(() => !!serviceId.value)

const environmentName = computed(() => store.currentEnvironment?.name || '环境')

// 状态
const loading = ref(false)
const submitting = ref(false)
const service = ref<Service | null>(null)
const showDatabaseDialog = ref(false)
const editingDatabase = ref<Database | null>(null)

// 表单引用
const formRef = ref<FormInstance>()
const serverFormRef = ref<FormInstance>()

// 表单数据
const formData = ref<ServiceCreate>({
  name: '',
  service_type: 'microservice',
  description: ''
})

const serverForm = ref<ServerCreate>({
  name: 'default',
  host: '',
  port: undefined,
  protocol: 'http',
  base_path: '',
  timeout: 30000
})

const databases = ref<(Database | DatabaseCreate)[]>([])

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const serverRules: FormRules = {
  protocol: [
    { required: true, message: '请选择协议', trigger: 'change' }
  ],
  host: [
    { required: true, message: '请输入主机地址', trigger: 'blur' }
  ]
}

// 初始化
onMounted(async () => {
  if (envId.value) {
    await store.fetchEnvironment(envId.value)
  }
  if (isEdit.value && serviceId.value) {
    await loadService()
  }
})

// baseUrl预览
const baseUrlPreview = computed(() => {
  const { protocol, host, port, base_path } = serverForm.value
  let url = `${protocol}://${host}`
  
  if (port && !isStandardPort(protocol, port)) {
    url += `:${port}`
  }
  
  if (base_path) {
    url += base_path.startsWith('/') ? base_path : `/${base_path}`
  }
  
  return url
})

// 监听serviceId变化
watch(serviceId, async (newId) => {
  if (newId) {
    await loadService()
  }
})

// 加载服务数据
async function loadService() {
  if (!serviceId.value) return
  
  loading.value = true
  try {
    service.value = await environmentApi.getService(serviceId.value)
    
    // 填充表单数据
    formData.value = {
      name: service.value.name,
      service_type: service.value.service_type || 'microservice',
      description: service.value.description || ''
    }
    
    // 填充服务器配置
    if (service.value.servers && service.value.servers.length > 0) {
      const server = service.value.servers[0]
      serverForm.value = {
        name: server.name,
        host: server.host,
        port: server.port,
        protocol: server.protocol,
        base_path: server.base_path,
        timeout: server.timeout
      }
    }
    
    // 填充数据库配置
    databases.value = service.value.databases || []
  } finally {
    loading.value = false
  }
}

// 判断是否为标准端口
function isStandardPort(protocol: string, port: number): boolean {
  return (protocol === 'http' && port === 80) || (protocol === 'https' && port === 443)
}

// 获取数据库类型标签
function getDbTypeLabel(type: string) {
  const item = DATABASE_TYPES.find(t => t.value === type)
  return item?.label || type
}

// 获取数据库标签类型
function getDbTagType(type: string) {
  const typeMap: Record<string, string> = {
    mysql: '',
    postgresql: 'success',
    mongodb: 'warning',
    redis: 'danger',
    sqlserver: 'info',
    oracle: 'warning'
  }
  return typeMap[type] || ''
}

// 获取默认端口
function getDefaultPort(type: string) {
  const item = DATABASE_TYPES.find(t => t.value === type)
  return item?.defaultPort || 3306
}

// 编辑数据库
function handleEditDatabase(db: Database | DatabaseCreate) {
  editingDatabase.value = db as Database
  showDatabaseDialog.value = true
}

// 删除数据库
async function handleDeleteDatabase(db: Database | DatabaseCreate) {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据库"${db.name}"吗？`,
      '警告',
      { type: 'warning' }
    )
    databases.value = databases.value.filter(d => d !== db)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

// 保存数据库
function handleSaveDatabase(db: Database | DatabaseCreate) {
  const index = databases.value.findIndex(d => 
    (d as Database).id === (db as Database).id || d.name === db.name
  )
  
  if (index > -1) {
    databases.value[index] = db
  } else {
    databases.value.push(db)
  }
  
  editingDatabase.value = null
}

// 取消
function handleCancel() {
  router.back()
}

// 保存
async function handleSave() {
  const valid = await formRef.value?.validate()
  const serverValid = await serverFormRef.value?.validate()
  
  if (!valid || !serverValid) return

  submitting.value = true
  try {
    if (isEdit.value && serviceId.value) {
      // 编辑模式：分别更新各个部分
      await environmentApi.updateService(serviceId.value, formData.value)
      
      // 更新或创建服务器配置
      if (service.value?.servers && service.value.servers.length > 0) {
        await serverApi.update(service.value.servers[0].id, serverForm.value)
      } else {
        await serverApi.create(serviceId.value, serverForm.value)
      }
      
      // 保存数据库配置
      for (const db of databases.value) {
        if ((db as Database).id) {
          await databaseApi.update((db as Database).id, db as DatabaseCreate)
        } else {
          await databaseApi.create(serviceId.value, db as DatabaseCreate)
        }
      }
      
      ElMessage.success('更新成功')
    } else {
      // 创建模式
      await environmentApi.createService(envId.value, formData.value)
      const newService = await environmentApi.listServices(envId.value, { page: 1, page_size: 1 })
      if (newService.items.length > 0) {
        const newServiceId = newService.items[0].id
        await serverApi.create(newServiceId, serverForm.value)
        for (const db of databases.value) {
          await databaseApi.create(newServiceId, db as DatabaseCreate)
        }
      }
      ElMessage.success('创建成功')
    }
    
    router.back()
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.service-config {
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

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
}

/* 表单区域 */
.config-form {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e5e4e7;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 16px;
}

.section-header .section-title {
  margin-bottom: 0;
}

.input-suffix {
  margin-left: 8px;
  color: #6b6375;
  font-size: 14px;
}

/* baseUrl预览 */
.base-url-preview {
  background-color: #f4f3ec;
  border: 1px solid #e5e4e7;
  border-radius: 6px;
  padding: 12px;
  margin-top: 16px;
}

.preview-label {
  font-size: 12px;
  color: #6b6375;
  margin-right: 8px;
}

.preview-url {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 14px;
  color: #08060d;
}

/* 数据库列表 */
.database-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.database-card {
  background-color: #f9fafb;
  border: 1px solid #e5e4e7;
  border-radius: 8px;
  padding: 16px;
}

.db-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.db-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.db-name {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
}

.db-info code {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 14px;
  color: #6b6375;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e4e7;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-col {
    margin-bottom: 16px;
  }
}
</style>
