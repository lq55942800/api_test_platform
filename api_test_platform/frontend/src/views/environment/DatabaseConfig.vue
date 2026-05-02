<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :title="isEdit ? '编辑数据库' : '添加数据库'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      :model="formData"
      :rules="rules"
      ref="formRef"
      label-width="100px"
    >
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="数据库别名" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入数据库别名"
              maxlength="50"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="数据库类型" prop="db_type">
            <el-select
              v-model="formData.db_type"
              placeholder="请选择数据库类型"
              @change="handleDbTypeChange"
            >
              <el-option
                v-for="item in DATABASE_TYPES"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="16">
          <el-form-item label="主机地址" prop="host">
            <el-input
              v-model="formData.host"
              placeholder="请输入主机地址"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="端口" prop="port">
            <el-input
              v-model.number="formData.port"
              type="number"
              :min="1"
              :max="65535"
              placeholder="请输入端口"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="数据库名" prop="database">
        <el-input
          v-model="formData.database"
          placeholder="请输入数据库名"
        />
      </el-form-item>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="formData.username"
              placeholder="请输入用户名"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="formData.password"
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="字符集" prop="charset">
            <el-input
              v-model="formData.charset"
              placeholder="如 utf8mb4"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="加密存储">
            <el-checkbox v-model="formData.is_encrypted">加密存储密码</el-checkbox>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 连接串预览 -->
      <div class="connection-preview">
        <span class="preview-label">连接串预览：</span>
        <code class="preview-url">{{ connectionPreview }}</code>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button @click="handleTestConnection" :loading="testing">测试连接</el-button>
      <el-button type="primary" @click="handleSave" :loading="submitting">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { databaseApi } from '@/api/environment'
import type { Database, DatabaseCreate } from '@/types/environment'
import { DATABASE_TYPES } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

// Props
interface Props {
  modelValue: boolean
  database?: Database | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  database: null
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [database: Database | DatabaseCreate]
}>()

// 状态
const submitting = ref(false)
const testing = ref(false)

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const formData = ref<DatabaseCreate>({
  name: '',
  db_type: 'mysql',
  host: '',
  port: 3306,
  database: '',
  username: '',
  password: '',
  charset: 'utf8mb4',
  is_encrypted: true
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入数据库别名', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  db_type: [
    { required: true, message: '请选择数据库类型', trigger: 'change' }
  ],
  host: [
    { required: true, message: '请输入主机地址', trigger: 'blur' }
  ],
  database: [
    { required: true, message: '请输入数据库名', trigger: 'blur' }
  ]
}

// 计算属性
const isEdit = computed(() => !!props.database?.id)

const connectionPreview = computed(() => {
  const { db_type, host, port, database, username } = formData.value
  const defaultPort = getDefaultPort(db_type)
  const actualPort = port || defaultPort
  
  const typeMap: Record<string, string> = {
    mysql: 'mysql',
    postgresql: 'postgresql',
    mongodb: 'mongodb',
    redis: 'redis',
    sqlserver: 'mssql',
    oracle: 'oracle'
  }
  
  const protocol = typeMap[db_type] || db_type
  
  if (db_type === 'redis') {
    return `${protocol}://${host}:${actualPort}`
  }
  
  return `${protocol}://${username || 'user'}:***@${host}:${actualPort}/${database || 'db'}`
})

// 监听database变化
watch(() => props.database, (newDb) => {
  if (newDb) {
    formData.value = {
      name: newDb.name,
      db_type: newDb.db_type,
      host: newDb.host,
      port: newDb.port || getDefaultPort(newDb.db_type),
      database: newDb.database || '',
      username: newDb.username || '',
      password: '', // 密码不回显
      charset: newDb.charset || 'utf8mb4',
      is_encrypted: true
    }
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

// 监听对话框打开状态
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.database) {
    // 对话框打开时，确保数据已加载
    formData.value = {
      name: props.database.name,
      db_type: props.database.db_type,
      host: props.database.host,
      port: props.database.port || getDefaultPort(props.database.db_type),
      database: props.database.database || '',
      username: props.database.username || '',
      password: '', // 密码不回显
      charset: props.database.charset || 'utf8mb4',
      is_encrypted: true
    }
  }
})

// 获取默认端口
function getDefaultPort(type: string) {
  const item = DATABASE_TYPES.find(t => t.value === type)
  return item?.defaultPort || 3306
}

// 数据库类型变化处理
function handleDbTypeChange(type: string) {
  formData.value.port = getDefaultPort(type)
}

// 重置表单
function resetForm() {
  formData.value = {
    name: '',
    db_type: 'mysql',
    host: '',
    port: 3306,
    database: '',
    username: '',
    password: '',
    charset: 'utf8mb4',
    is_encrypted: true
  }
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
  resetForm()
}

// 测试连接
async function handleTestConnection() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  testing.value = true
  try {
    // 如果是编辑模式，使用现有ID测试
    if (isEdit.value && props.database?.id) {
      const result = await databaseApi.testConnection(props.database.id)
      if (result.success) {
        ElMessage.success('连接成功')
      } else {
        ElMessage.error(`连接失败：${result.message}`)
      }
    } else {
      // 新建模式，提示需要先保存
      ElMessage.info('请先保存数据库配置后再测试连接')
    }
  } catch (error: any) {
    // 错误已在拦截器中处理
  } finally {
    testing.value = false
  }
}

// 保存
async function handleSave() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    // 如果是编辑模式，保留ID
    const saveData: Database | DatabaseCreate = isEdit.value
      ? { ...formData.value, id: props.database!.id, service_id: props.database!.service_id }
      : formData.value
    
    emit('save', saveData)
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* 连接串预览 */
.connection-preview {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .el-col {
    margin-bottom: 16px;
  }
}
</style>
