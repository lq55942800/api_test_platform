<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchText"
          placeholder="搜索用户名/邮箱/姓名"
          clearable
          style="width: 240px; margin-right: 12px"
          @clear="loadUsers"
          @keyup.enter="loadUsers"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>新建用户
        </el-button>
      </div>
    </div>

    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="full_name" label="姓名" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_superuser" type="danger" size="small">管理员</el-tag>
          <el-tag v-else type="" size="small">普通用户</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="所属团队" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="t in row.teams" :key="t.team_id" size="small" style="margin-right: 4px">
            {{ t.team_name }}({{ t.role === 'team_leader' ? '负责人' : t.role === 'developer' ? '开发' : '测试' }})
          </el-tag>
          <span v-if="!row.teams?.length" style="color: #909399">无</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button link type="warning" size="small" @click="openResetPasswordDialog(row)">重置密码</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)" :disabled="row.is_superuser">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreateDialog" title="新建用户" width="500px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="3-50位字母数字下划线" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" show-password placeholder="8-32位，含大小写字母和数字" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="createForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="createForm.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑用户" width="500px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-width="90px">
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.full_name" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showResetDialog" title="重置密码" width="400px" destroy-on-close>
      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" label-width="80px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetForm.new_password" type="password" show-password placeholder="8-32位，含大小写字母和数字" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleResetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { userApi } from '@/api/admin'
import type { AdminUserResponse } from '@/types/admin'

const users = ref<AdminUserResponse[]>([])
const loading = ref(false)
const submitting = ref(false)
const searchText = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showResetDialog = ref(false)

const createFormRef = ref<FormInstance>()
const resetFormRef = ref<FormInstance>()

const createForm = reactive({ username: '', email: '', password: '', full_name: '', is_superuser: false })
const editForm = reactive({ email: '', full_name: '', is_active: true, is_superuser: false })
const resetForm = reactive({ new_password: '' })

let editingUserId = 0
let resettingUserId = 0

const createRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '3-50个字符', trigger: 'blur' },
  ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '8-32个字符', trigger: 'blur' },
  ],
}

const resetRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 32, message: '8-32个字符', trigger: 'blur' },
  ],
}

onMounted(() => { loadUsers() })

async function loadUsers() {
  loading.value = true
  try {
    const params: any = {}
    if (searchText.value) params.search = searchText.value
    users.value = await userApi.list(params)
  } catch (e: any) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await userApi.create(createForm)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    Object.assign(createForm, { username: '', email: '', password: '', full_name: '', is_superuser: false })
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

function openEditDialog(user: AdminUserResponse) {
  editingUserId = user.id
  editForm.email = user.email
  editForm.full_name = user.full_name || ''
  editForm.is_active = user.is_active
  editForm.is_superuser = user.is_superuser
  showEditDialog.value = true
}

async function handleEdit() {
  submitting.value = true
  try {
    await userApi.update(editingUserId, editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

function openResetPasswordDialog(user: AdminUserResponse) {
  resettingUserId = user.id
  resetForm.new_password = ''
  showResetDialog.value = true
}

async function handleResetPassword() {
  const valid = await resetFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await userApi.resetPassword(resettingUserId, { new_password: resetForm.new_password })
    ElMessage.success('密码重置成功')
    showResetDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '重置失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(user: AdminUserResponse) {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${user.username}"吗？此操作不可恢复。`, '确认删除', { type: 'warning' })
    await userApi.delete(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch { /* cancelled */ }
}
</script>

<style scoped>
.user-management {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>
