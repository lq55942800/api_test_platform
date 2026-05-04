<template>
  <div class="team-management">
    <div class="page-header">
      <h2>团队管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>新建团队
      </el-button>
    </div>

    <el-table :data="teams" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="团队名称" min-width="150" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="member_count" label="成员数" width="90" align="center" />
      <el-table-column prop="api_count" label="接口数" width="90" align="center" />
      <el-table-column prop="test_case_count" label="用例数" width="90" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openMemberDialog(row)">成员</el-button>
          <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreateDialog" title="新建团队" width="480px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="teamRules" label-width="80px">
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑团队" width="480px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="teamRules" label-width="80px">
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMemberDialog" :title="`成员管理 - ${currentTeam?.name || ''}`" width="700px" destroy-on-close>
      <div class="member-header">
        <el-button type="primary" size="small" @click="showAddMemberDialog = true">
          <el-icon><Plus /></el-icon>添加成员
        </el-button>
      </div>
      <el-table :data="members" v-loading="memberLoading" stripe size="small">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column label="角色" width="130">
          <template #default="{ row }">
            <el-select v-model="row.role" size="small" @change="handleUpdateMemberRole(row)">
              <el-option v-for="r in MEMBER_ROLES" :key="r.value" :label="r.label" :value="r.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '活跃' : '已移除' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="joined_at" label="加入时间" width="170">
          <template #default="{ row }">
            {{ row.joined_at?.substring(0, 19).replace('T', ' ') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleRemoveMember(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="showAddMemberDialog" title="添加成员" width="400px" append-to-body destroy-on-close @open="onAddMemberDialogOpen">
        <el-form ref="addMemberFormRef" :model="addMemberForm" label-width="80px">
          <el-form-item label="用户" prop="user_id" :rules="[{ required: true, message: '请选择用户', trigger: 'change' }]">
            <el-select
              v-model="addMemberForm.user_id"
              filterable
              remote
              reserve-keyword
              placeholder="输入用户名搜索"
              :remote-method="searchUsers"
              :loading="userSearchLoading"
              style="width: 100%"
            >
              <el-option
                v-for="user in userSearchResults"
                :key="user.id"
                :label="`${user.username}（${user.full_name || '-'}）`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="addMemberForm.role" style="width: 100%">
              <el-option v-for="r in MEMBER_ROLES" :key="r.value" :label="r.label" :value="r.value" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddMemberDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleAddMember">确定</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { teamApi, userApi } from '@/api/admin'
import { MEMBER_ROLES } from '@/types/admin'
import type { TeamResponse, TeamMemberResponse, AdminUserResponse } from '@/types/admin'

const teams = ref<TeamResponse[]>([])
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showMemberDialog = ref(false)
const showAddMemberDialog = ref(false)
const currentTeam = ref<TeamResponse | null>(null)
const members = ref<TeamMemberResponse[]>([])
const memberLoading = ref(false)

const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

const createForm = reactive({ name: '', description: '' })
const editForm = reactive({ name: '', description: '', is_active: true })
const addMemberForm = reactive({ user_id: null as number | null, role: 'tester' })
const userSearchLoading = ref(false)
const userSearchResults = ref<AdminUserResponse[]>([])

const teamRules: FormRules = {
  name: [{ required: true, message: '请输入团队名称', trigger: 'blur' }],
}

let editingTeamId = 0

onMounted(() => { loadTeams() })

async function loadTeams() {
  loading.value = true
  try {
    teams.value = await teamApi.list()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载团队列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await teamApi.create(createForm)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.name = ''
    createForm.description = ''
    loadTeams()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

function openEditDialog(team: TeamResponse) {
  editingTeamId = team.id
  editForm.name = team.name
  editForm.description = team.description || ''
  editForm.is_active = team.is_active
  showEditDialog.value = true
}

async function handleEdit() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await teamApi.update(editingTeamId, { name: editForm.name, description: editForm.description, is_active: editForm.is_active })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadTeams()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(team: TeamResponse) {
  try {
    await ElMessageBox.confirm(`确定要删除团队"${team.name}"吗？此操作不可恢复。`, '确认删除', { type: 'warning' })
    await teamApi.delete(team.id)
    ElMessage.success('删除成功')
    loadTeams()
  } catch { /* cancelled */ }
}

async function openMemberDialog(team: TeamResponse) {
  currentTeam.value = team
  showMemberDialog.value = true
  await loadMembers(team.id)
}

async function loadMembers(teamId: number) {
  memberLoading.value = true
  try {
    members.value = await teamApi.listMembers(teamId)
  } catch (e: any) {
    ElMessage.error('加载成员列表失败')
  } finally {
    memberLoading.value = false
  }
}

async function handleAddMember() {
  if (!currentTeam.value || !addMemberForm.user_id) return
  submitting.value = true
  try {
    await teamApi.addMember(currentTeam.value.id, { user_id: addMemberForm.user_id, role: addMemberForm.role })
    ElMessage.success('添加成功')
    showAddMemberDialog.value = false
    addMemberForm.user_id = null
    addMemberForm.role = 'tester'
    userSearchResults.value = []
    loadMembers(currentTeam.value.id)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

function onAddMemberDialogOpen() {
  addMemberForm.user_id = null
  addMemberForm.role = 'tester'
  userSearchResults.value = []
}

async function searchUsers(query: string) {
  if (!query) {
    userSearchResults.value = []
    return
  }
  userSearchLoading.value = true
  try {
    const results = await userApi.list({ search: query })
    const memberIds = members.value.filter(m => m.status === 'active').map(m => m.user_id)
    userSearchResults.value = results.filter(u => !memberIds.includes(u.id))
  } catch {
    userSearchResults.value = []
  } finally {
    userSearchLoading.value = false
  }
}

async function handleUpdateMemberRole(member: TeamMemberResponse) {
  if (!currentTeam.value) return
  try {
    await teamApi.updateMember(currentTeam.value.id, member.id, { role: member.role })
    ElMessage.success('角色更新成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
    loadMembers(currentTeam.value.id)
  }
}

async function handleRemoveMember(member: TeamMemberResponse) {
  if (!currentTeam.value) return
  try {
    await ElMessageBox.confirm(`确定要移除成员"${member.username}"吗？`, '确认移除', { type: 'warning' })
    await teamApi.removeMember(currentTeam.value.id, member.id)
    ElMessage.success('移除成功')
    loadMembers(currentTeam.value.id)
  } catch { /* cancelled */ }
}
</script>

<style scoped>
.team-management {
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

.member-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
