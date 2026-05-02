<template>
  <div class="body-editor">
    <el-radio-group v-model="bodyType" size="small" @change="handleTypeChange">
      <el-radio-button v-for="bt in BODY_TYPES" :key="bt.value" :value="bt.value">
        {{ bt.label }}
      </el-radio-button>
    </el-radio-group>

    <div class="body-content" v-if="bodyType !== 'none'">
      <div v-if="bodyType === 'json'" class="json-editor">
        <el-input
          v-model="bodyContent"
          type="textarea"
          placeholder="请输入JSON内容"
          :rows="12"
          class="code-textarea"
          @input="handleContentChange"
        />
      </div>

      <div v-else-if="bodyType === 'form-data'" class="form-editor">
        <el-table :data="formDataItems" border size="small" style="width: 100%">
          <el-table-column label="参数名" min-width="150">
            <template #default="{ row }">
              <el-input v-model="row.name" placeholder="参数名" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small">
                <el-option label="文本" value="text" />
                <el-option label="文件" value="file" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="值" min-width="200">
            <template #default="{ row, $index }">
              <el-input v-if="row.type !== 'file'" v-model="row.value" placeholder="值" size="small" />
              <div v-else style="display: flex; align-items: center; gap: 8px">
                <el-button size="small" @click="selectFormDataFile($index)">选择文件</el-button>
                <span v-if="row.fileName" style="font-size: 12px; color: #606266">{{ row.fileName }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="描述" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.description" placeholder="描述" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removeFormDataItem($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <input
          ref="formDataFileInput"
          type="file"
          style="display: none"
          @change="handleFormDataFileSelect"
        />
        <el-button type="primary" link size="small" @click="addFormDataItem" style="margin-top: 8px">
          <el-icon><Plus /></el-icon>
          添加参数
        </el-button>
      </div>

      <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="form-editor">
        <el-table :data="urlEncodedItems" border size="small" style="width: 100%">
          <el-table-column label="参数名" min-width="150">
            <template #default="{ row }">
              <el-input v-model="row.name" placeholder="参数名" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="值" min-width="200">
            <template #default="{ row }">
              <el-input v-model="row.value" placeholder="值" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="描述" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.description" placeholder="描述" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removeUrlEncodedItem($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" link size="small" @click="addUrlEncodedItem" style="margin-top: 8px">
          <el-icon><Plus /></el-icon>
          添加参数
        </el-button>
      </div>

      <div v-else-if="bodyType === 'binary'" class="binary-editor">
        <div class="upload-config">
          <el-radio-group v-model="uploadMode" size="small">
            <el-radio-button value="single">单文件</el-radio-button>
            <el-radio-button value="multiple">多文件</el-radio-button>
          </el-radio-group>
          
          <el-select v-model="fileTypeFilter" placeholder="文件类型限制" size="small" style="width: 150px; margin-left: 12px">
            <el-option label="不限制" value="*/*" />
            <el-option label="图片" value="image/*" />
            <el-option label="文档" value=".pdf,.doc,.docx,.txt" />
            <el-option label="压缩包" value=".zip,.rar,.7z" />
          </el-select>
        </div>
        
        <el-table :data="uploadedFiles" border size="small" style="width: 100%; margin-top: 12px" v-if="uploadedFiles.length > 0">
          <el-table-column label="文件名" prop="name" min-width="200" />
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column label="类型" prop="type" width="120" />
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removeFile($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <input
          ref="fileInput"
          type="file"
          :accept="fileTypeFilter"
          :multiple="uploadMode === 'multiple'"
          @change="handleFileSelect"
          style="display: none"
        />
        <el-button type="primary" link size="small" @click="selectFiles" style="margin-top: 8px">
          <el-icon><Plus /></el-icon>
          选择文件
        </el-button>
      </div>

      <div v-else class="raw-editor">
        <el-input
          v-model="bodyContent"
          type="textarea"
          placeholder="请输入请求体内容"
          :rows="12"
          class="code-textarea"
          @input="handleContentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { BODY_TYPES, BodyType } from '@/types/api'

interface FileUploadItem {
  name: string
  file: File | null
  type: string
  size: number
}

const props = withDefaults(defineProps<{
  modelType?: string
  modelValue?: string
}>(), {
  modelType: 'none',
  modelValue: ''
})

const emit = defineEmits<{
  'update:modelType': [value: string]
  'update:modelValue': [value: string]
}>()

const bodyType = ref(props.modelType || 'none')
const bodyContent = ref(props.modelValue || '')
const formDataItems = ref<Array<{ name: string; type: string; value: string; fileName?: string; file?: File | null; description: string }>>([])
const urlEncodedItems = ref<Array<{ name: string; value: string; description: string }>>([])
const uploadMode = ref<'single' | 'multiple'>('single')
const fileTypeFilter = ref('*/*')
const uploadedFiles = ref<FileUploadItem[]>([])
const fileInput = ref<HTMLInputElement | null>(null)
const formDataFileInput = ref<HTMLInputElement | null>(null)
const currentFormDataIndex = ref<number>(-1)

watch(() => props.modelType, (val) => {
  bodyType.value = val || 'none'
})

watch(() => props.modelValue, (val) => {
  bodyContent.value = val || ''
})

function handleTypeChange(val: string) {
  emit('update:modelType', val)
  if (val === 'none') {
    emit('update:modelValue', '')
  }
}

function handleContentChange() {
  emit('update:modelValue', bodyContent.value)
}

function addFormDataItem() {
  formDataItems.value.push({ name: '', type: 'text', value: '', fileName: '', file: null, description: '' })
}

function removeFormDataItem(index: number) {
  formDataItems.value.splice(index, 1)
}

function selectFormDataFile(index: number) {
  currentFormDataIndex.value = index
  formDataFileInput.value?.click()
}

function handleFormDataFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file && currentFormDataIndex.value >= 0) {
    formDataItems.value[currentFormDataIndex.value].file = file
    formDataItems.value[currentFormDataIndex.value].fileName = file.name
    formDataItems.value[currentFormDataIndex.value].value = file.name
  }
  target.value = ''
  currentFormDataIndex.value = -1
}

function addUrlEncodedItem() {
  urlEncodedItems.value.push({ name: '', value: '', description: '' })
}

function removeUrlEncodedItem(index: number) {
  urlEncodedItems.value.splice(index, 1)
}

function selectFiles() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    for (let i = 0; i < files.length; i++) {
      uploadedFiles.value.push({
        name: files[i].name,
        file: files[i],
        type: files[i].type || 'unknown',
        size: files[i].size
      })
    }
  }
  target.value = ''
}

function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.body-editor {
  width: 100%;
}

.body-content {
  margin-top: 12px;
}

.code-textarea :deep(.el-textarea__inner) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
