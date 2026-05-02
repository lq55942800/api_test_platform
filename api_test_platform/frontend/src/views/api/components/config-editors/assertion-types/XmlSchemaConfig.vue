<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="Schema来源">
      <el-select v-model="config.schema_source" @change="emitUpdate">
        <el-option label="文件" value="file" />
        <el-option label="URL" value="url" />
      </el-select>
    </el-form-item>
    <template v-if="config.schema_source === 'file'">
      <el-form-item label="XSD文件路径">
        <el-input v-model="config.schema_file" placeholder="XSD文件路径" @input="emitUpdate" />
      </el-form-item>
    </template>
    <template v-if="config.schema_source === 'url'">
      <el-form-item label="XSD URL">
        <el-input v-model="config.schema_url" placeholder="XSD Schema URL地址" @input="emitUpdate" />
      </el-form-item>
    </template>
    <el-form-item label="自定义消息">
      <el-input v-model="config.message" placeholder="断言失败时的自定义消息" @input="emitUpdate" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  schema_source: 'file',
  schema_file: '',
  schema_url: '',
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { schema_source: 'file', schema_file: '', schema_url: '', message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
