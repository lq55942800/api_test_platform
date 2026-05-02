<template>
  <el-dialog
    v-model="visible"
    title="导入接口"
    width="700px"
    :close-on-click-modal="false"
  >
    <div v-if="step === 1" class="import-step">
      <el-form label-width="80px">
        <el-form-item label="导入方式">
          <el-radio-group v-model="importType">
            <el-radio value="file">上传文件</el-radio>
            <el-radio value="url">URL解析</el-radio>
          </el-radio-group>
        </el-form-item>

        <div v-if="importType === 'file'">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".json,.yaml,.yml"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            drag
          >
            <div class="upload-area">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div>拖拽文件到此处，或点击上传</div>
              <div class="upload-hint">支持 Swagger 2.0 / OpenAPI 3.0 / HAR 格式，文件大小不超过 10MB</div>
            </div>
          </el-upload>
        </div>

        <div v-if="importType === 'url'">
          <el-form-item label="URL">
            <el-input v-model="importUrl" placeholder="请输入Swagger/OpenAPI文档URL" />
          </el-form-item>
        </div>

        <el-form-item label="目标模块">
          <el-select v-model="targetModuleId" placeholder="选择模块" clearable style="width: 100%">
            <el-option
              v-for="m in moduleStore.modules"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="step === 2" class="import-step">
      <div class="preview-summary">
        <span>解析结果: 共 {{ previewData.total }} 个接口</span>
        <span class="summary-new">新增: {{ previewData.new_count }} 个</span>
        <span class="summary-dup">重复: {{ previewData.duplicate_count }} 个</span>
        <span class="summary-fail">失败: {{ previewData.failed_count }} 个</span>
      </div>

      <div class="conflict-strategy" v-if="previewData.duplicate_count > 0">
        <span class="strategy-label">重复接口处理策略：</span>
        <el-radio-group v-model="conflictStrategy" size="small">
          <el-radio v-for="cs in CONFLICT_STRATEGIES" :key="cs.value" :value="cs.value">
            {{ cs.label }}
          </el-radio>
        </el-radio-group>
      </div>

      <el-table :data="previewData.apis" border size="small" max-height="300">
        <el-table-column type="selection" width="40" />
        <el-table-column label="方法" width="80" align="center">
          <template #default="{ row }">
            <MethodTag :method="row.method" />
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="200" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'new' ? 'success' : row.status === 'duplicate' ? 'warning' : 'danger'"
              size="small"
            >
              {{ row.status === 'new' ? '新增' : row.status === 'duplicate' ? '重复' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="step === 3" class="import-step">
      <div class="import-result">
        <el-icon class="result-icon" color="#67C23A"><SuccessFilled /></el-icon>
        <div class="result-title">导入成功!</div>
        <div class="result-detail">
          <span>成功导入: {{ importResult.created }} 个</span>
          <span>跳过重复: {{ importResult.skipped }} 个</span>
          <span>导入失败: {{ importResult.failed }} 个</span>
        </div>
      </div>
    </div>

    <template #footer>
      <div v-if="step === 1">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handlePreview" :loading="previewing" :disabled="!canPreview">下一步</el-button>
      </div>
      <div v-if="step === 2">
        <el-button @click="step = 1">上一步</el-button>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">确认导入</el-button>
      </div>
      <div v-if="step === 3">
        <el-button @click="visible = false">关闭</el-button>
        <el-button type="primary" @click="handleContinue">继续导入</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, SuccessFilled } from '@element-plus/icons-vue'
import { importApi } from '@/api/api'
import { useModuleStore } from '@/stores/api'
import { CONFLICT_STRATEGIES } from '@/types/api'
import type { ImportPreview, ImportResult, ImportPreviewItem } from '@/types/api'
import MethodTag from './components/MethodTag.vue'
import type { UploadFile } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const moduleStore = useModuleStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const step = ref(1)
const importType = ref<'file' | 'url'>('file')
const importUrl = ref('')
const targetModuleId = ref<number | null>(null)
const conflictStrategy = ref('skip')
const previewing = ref(false)
const importing = ref(false)
const fileContent = ref('')
const previewData = ref<ImportPreview>({
  total: 0,
  new_count: 0,
  duplicate_count: 0,
  failed_count: 0,
  apis: []
})
const importResult = ref<ImportResult>({
  total: 0,
  created: 0,
  skipped: 0,
  failed: 0
})

const canPreview = computed(() => {
  if (importType.value === 'file') return !!fileContent.value
  return !!importUrl.value
})

function handleFileChange(file: UploadFile) {
  const reader = new FileReader()
  reader.onload = (e) => {
    fileContent.value = e.target?.result as string
  }
  if (file.raw) {
    reader.readAsText(file.raw)
  }
}

function handleFileRemove() {
  fileContent.value = ''
}

async function handlePreview() {
  previewing.value = true
  try {
    previewData.value = await importApi.preview({
      import_type: importType.value,
      content: importType.value === 'file' ? fileContent.value : undefined,
      url: importType.value === 'url' ? importUrl.value : undefined,
      module_id: targetModuleId.value || undefined,
      conflict_strategy: conflictStrategy.value
    })
    step.value = 2
  } catch (error: any) {
    // handled
  } finally {
    previewing.value = false
  }
}

async function handleImport() {
  importing.value = true
  try {
    importResult.value = await importApi.execute({
      import_type: importType.value,
      content: importType.value === 'file' ? fileContent.value : undefined,
      url: importType.value === 'url' ? importUrl.value : undefined,
      module_id: targetModuleId.value || undefined,
      conflict_strategy: conflictStrategy.value,
      selected_apis: previewData.value.apis
        .filter(a => a.selected && a.status !== 'failed')
        .map((_, i) => i)
    })
    step.value = 3
    emit('success')
  } catch (error: any) {
    // handled
  } finally {
    importing.value = false
  }
}

function handleContinue() {
  step.value = 1
  fileContent.value = ''
  importUrl.value = ''
  previewData.value = { total: 0, new_count: 0, duplicate_count: 0, failed_count: 0, apis: [] }
}
</script>

<style scoped>
.import-step {
  min-height: 200px;
}

.upload-area {
  text-align: center;
  padding: 20px;
}

.upload-icon {
  font-size: 48px;
  color: #aa3bff;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #6b6375;
  margin-top: 8px;
}

.preview-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 14px;
}

.summary-new { color: #67C23A; }
.summary-dup { color: #E6A23C; }
.summary-fail { color: #F56C6C; }

.conflict-strategy {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.strategy-label {
  font-size: 14px;
  color: #08060d;
  white-space: nowrap;
}

.import-result {
  text-align: center;
  padding: 24px;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 12px;
}

.result-detail {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 14px;
  color: #6b6375;
}
</style>
