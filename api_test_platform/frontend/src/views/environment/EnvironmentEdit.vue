<template>
  <div class="environment-edit">
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/environments' }">环境管理</el-breadcrumb-item>
        <el-breadcrumb-item>{{ isEdit ? '编辑环境' : '新建环境' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-header">
      <h2>{{ isEdit ? '编辑环境' : '新建环境' }}</h2>
    </div>

    <div class="edit-form" v-loading="loading">
      <el-form
        :model="formData"
        :rules="rules"
        ref="formRef"
        label-width="100px"
      >
        <el-form-item label="环境名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入环境名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="环境描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入环境描述"
            maxlength="500"
            show-word-limit
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
        </el-form-item>
      </el-form>

      <div class="form-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="submitting">保存</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import type { EnvironmentUpdate } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useEnvironmentStore()

const loading = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const formData = ref<EnvironmentUpdate>({
  name: '',
  description: '',
  is_default: false
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入环境名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const isEdit = computed(() => !!route.params.id)

onMounted(async () => {
  if (isEdit.value) {
    const envId = Number(route.params.id)
    loading.value = true
    try {
      const env = await store.fetchEnvironment(envId)
      if (env) {
        formData.value = {
          name: env.name,
          description: env.description || '',
          is_default: env.is_default
        }
      }
    } finally {
      loading.value = false
    }
  }
})

function handleCancel() {
  router.back()
}

async function handleSave() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await store.updateEnvironment(Number(route.params.id), formData.value)
      ElMessage.success('更新成功')
    } else {
      const env = await store.createEnvironment({
        name: formData.value.name || '',
        description: formData.value.description,
        is_default: formData.value.is_default
      })
      ElMessage.success('创建成功')
      router.push(`/environments/${env.id}`)
      return
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
.environment-edit {
  padding: 24px;
  background-color: #f9fafb;
  min-height: 100vh;
}

.breadcrumb {
  margin-bottom: 24px;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
}

.edit-form {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e4e7;
}
</style>
