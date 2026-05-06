<template>
  <div class="module-tree">
    <div class="tree-header">
      <span class="tree-title">模块导航</span>
      <el-button type="primary" link size="small" @click="handleAddRoot" class="add-btn">
        <el-icon><Plus /></el-icon>
        <span>新建</span>
      </el-button>
    </div>
    <div class="tree-body">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        node-key="id"
        highlight-current
        :expand-on-click-node="false"
        :default-expanded-keys="expandedKeys"
        :current-node-key="currentNodeKey"
        @node-click="handleNodeClick"
        @node-contextmenu="handleContextMenu"
      >
        <template #default="{ node, data }">
          <div class="tree-node" :class="{ 'is-all': data.id === 0 }">
            <div class="node-left">
              <el-icon v-if="data.id === 0" class="node-icon"><Grid /></el-icon>
              <el-icon v-else class="node-icon"><Folder /></el-icon>
              <span class="node-label">{{ data.name }}</span>
            </div>
            <span class="node-count" v-if="data.api_count !== undefined">{{ data.api_count }}</span>
          </div>
        </template>
      </el-tree>
    </div>

    <el-dialog
      v-model="showModuleDialog"
      :title="editingModule ? '编辑模块' : '新建模块'"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="moduleForm" :rules="moduleRules" ref="moduleFormRef" label-width="80px">
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="moduleForm.description" type="textarea" placeholder="请输入描述" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModuleDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveModule" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Grid, Folder } from '@element-plus/icons-vue'
import { useModuleStore } from '@/stores/api'
import type { ApiModule, ApiModuleCreate } from '@/types/api'
import type { FormInstance, FormRules } from 'element-plus'

const emit = defineEmits<{
  select: [moduleId: number | null]
}>()

const moduleStore = useModuleStore()
const treeRef = ref<any>()
const expandedKeys = ref<number[]>([])
const currentNodeKey = ref(0)
const showModuleDialog = ref(false)
const editingModule = ref<ApiModule | null>(null)
const submitting = ref(false)
const moduleFormRef = ref<FormInstance>()
const moduleForm = ref<ApiModuleCreate & { id?: number }>({
  name: '',
  description: '',
  parent_id: undefined
})

const moduleRules: FormRules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

const treeData = computed(() => {
  const totalApiCount = moduleStore.modules.length > 0
    ? (moduleStore.modules[0].total_api_count || 0)
    : 0
  const allNode = { id: 0, name: '全部接口', children: moduleStore.modules, api_count: totalApiCount }
  return [allNode]
})

onMounted(async () => {
  await moduleStore.fetchModules()
  if (moduleStore.modules.length > 0) {
    expandedKeys.value = moduleStore.modules.map(m => m.id)
  }
})

function handleNodeClick(data: ApiModule & { id?: number }) {
  emit('select', data.id === 0 ? null : data.id)
}

function handleAddRoot() {
  editingModule.value = null
  moduleForm.value = { name: '', description: '', parent_id: undefined }
  showModuleDialog.value = true
}

function handleContextMenu(event: MouseEvent, data: any, node: any) {
  event.preventDefault()
}

function handleAddChild(parentId: number) {
  editingModule.value = null
  moduleForm.value = { name: '', description: '', parent_id: parentId }
  showModuleDialog.value = true
}

function handleEdit(module: ApiModule) {
  editingModule.value = module
  moduleForm.value = {
    id: module.id,
    name: module.name,
    description: module.description || '',
    parent_id: module.parent_id
  }
  showModuleDialog.value = true
}

async function handleDelete(module: ApiModule) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模块"${module.name}"吗？该模块下的接口将移至未分类。`,
      '警告',
      { type: 'warning' }
    )
    await moduleStore.deleteModule(module.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      // error handled by interceptor
    }
  }
}

async function handleSaveModule() {
  const valid = await moduleFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (editingModule.value) {
      await moduleStore.updateModule(editingModule.value.id, {
        name: moduleForm.value.name,
        description: moduleForm.value.description
      })
      ElMessage.success('更新成功')
    } else {
      await moduleStore.createModule(moduleForm.value)
      ElMessage.success('创建成功')
    }
    showModuleDialog.value = false
  } catch (error: any) {
    // error handled by interceptor
  } finally {
    submitting.value = false
  }
}

defineExpose({ handleAddChild, handleEdit, handleDelete })
</script>

<style scoped>
.module-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface-50);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-neutral-200);
}

.tree-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-neutral-900);
  letter-spacing: -0.01em;
}

.add-btn {
  font-size: 13px;
  gap: 2px;
}

.tree-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding-right: 12px;
  height: 100%;
}

.node-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  flex: 1;
}

.node-icon {
  font-size: 14px;
  color: var(--color-neutral-400);
  flex-shrink: 0;
}

.tree-node.is-all .node-icon {
  color: var(--color-primary-500);
}

.node-label {
  font-size: 13px;
  color: var(--color-neutral-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.node-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-neutral-400);
  background-color: var(--color-neutral-100);
  padding: 1px 8px;
  border-radius: 10px;
  flex-shrink: 0;
  line-height: 1.6;
}

:deep(.el-tree) {
  background-color: transparent;
  --el-tree-node-content-height: 36px;
}

:deep(.el-tree-node__content) {
  padding-left: 12px !important;
  border-radius: 6px;
  margin: 1px 8px;
  transition: all var(--transition-fast);
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: var(--color-primary-50);
  color: var(--color-primary-600);
}

:deep(.el-tree-node.is-current > .el-tree-node__content .node-label) {
  color: var(--color-primary-600);
  font-weight: 600;
}

:deep(.el-tree-node.is-current > .el-tree-node__content .node-icon) {
  color: var(--color-primary-500);
}

:deep(.el-tree-node.is-current > .el-tree-node__content .node-count) {
  background-color: var(--color-primary-100);
  color: var(--color-primary-600);
}

:deep(.el-tree-node__content:hover) {
  background-color: var(--color-surface-200);
}

:deep(.el-tree-node__expand-icon) {
  font-size: 12px;
  color: var(--color-neutral-400);
}
</style>
