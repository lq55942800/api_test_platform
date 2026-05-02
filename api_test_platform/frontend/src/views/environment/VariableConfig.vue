<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :title="isEdit ? '编辑变量' : '添加变量'"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      :model="formData"
      :rules="rules"
      ref="formRef"
      label-width="80px"
    >
      <el-form-item label="变量名" prop="key">
        <el-input
          v-model="formData.key"
          placeholder="请输入变量名"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="变量值" prop="value">
        <el-input
          v-model="formData.value"
          type="textarea"
          placeholder="请输入变量值"
          maxlength="5000"
          show-word-limit
          :rows="3"
        />
      </el-form-item>

      <el-form-item label="变量类型" prop="value_type">
        <el-select v-model="formData.value_type" placeholder="请选择变量类型">
          <el-option
            v-for="item in VARIABLE_TYPES"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="加密存储">
        <el-checkbox v-model="formData.is_encrypted">加密存储变量值</el-checkbox>
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          placeholder="请输入描述"
          maxlength="200"
          show-word-limit
          :rows="2"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="submitting">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { EnvVariable, EnvVariableCreate } from '@/types/environment'
import { VARIABLE_TYPES } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  modelValue: boolean
  variable?: EnvVariable | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  variable: null
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [variable: EnvVariable | EnvVariableCreate]
}>()

const submitting = ref(false)

const formRef = ref<FormInstance>()

const formData = ref<EnvVariableCreate>({
  key: '',
  value: '',
  value_type: 'string',
  is_encrypted: false,
  description: ''
})

const rules: FormRules = {
  key: [
    { required: true, message: '请输入变量名', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '变量名只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ],
  value_type: [
    { required: true, message: '请选择变量类型', trigger: 'change' }
  ]
}

const isEdit = computed(() => !!props.variable?.id)

watch(() => props.variable, (newVar) => {
  if (newVar) {
    formData.value = {
      key: newVar.key,
      value: newVar.is_encrypted ? '' : (newVar.value || ''),
      value_type: newVar.value_type || 'string',
      is_encrypted: newVar.is_encrypted,
      description: newVar.description || ''
    }
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.variable) {
    formData.value = {
      key: props.variable.key,
      value: props.variable.is_encrypted ? '' : (props.variable.value || ''),
      value_type: props.variable.value_type || 'string',
      is_encrypted: props.variable.is_encrypted,
      description: props.variable.description || ''
    }
  }
})

function resetForm() {
  formData.value = {
    key: '',
    value: '',
    value_type: 'string',
    is_encrypted: false,
    description: ''
  }
}

function handleClose() {
  emit('update:modelValue', false)
  resetForm()
}

async function handleSave() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const saveData: EnvVariable | EnvVariableCreate = isEdit.value
      ? { 
          ...formData.value, 
          id: props.variable!.id,
          environment_id: props.variable!.environment_id
        }
      : formData.value
    
    emit('save', saveData)
    handleClose()
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
</style>
