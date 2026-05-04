<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-brand">
        <div class="brand-content">
          <h1 class="brand-title">AutoTest API</h1>
          <p class="brand-subtitle">企业级API测试平台</p>
        </div>
      </div>
      <div class="register-form-section">
        <h2 class="form-title">注册</h2>
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名（3-50位字母数字下划线）"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="邮箱"
              :prefix-icon="Message"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码（8-32位，含大小写字母和数字）"
              :prefix-icon="Lock"
              show-password
              size="large"
            />
            <div v-if="form.password" class="password-strength">
              <span class="strength-label">密码强度：</span>
              <span :class="['strength-text', strengthClass]">{{ strengthText }}</span>
            </div>
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              :prefix-icon="Lock"
              show-password
              size="large"
              @keyup.enter="handleRegister"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="register-button"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          已有账号？<router-link to="/login" class="link">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码长度为8-32个字符', trigger: 'blur' },
    { pattern: /[A-Z]/, message: '密码需包含大写字母', trigger: 'blur' },
    { pattern: /[a-z]/, message: '密码需包含小写字母', trigger: 'blur' },
    { pattern: /\d/, message: '密码需包含数字', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const strengthClass = computed(() => {
  const pw = form.password
  if (!pw) return ''
  let score = 0
  if (pw.length >= 8) score++
  if (pw.length >= 12) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[a-z]/.test(pw)) score++
  if (/\d/.test(pw)) score++
  if (/[^a-zA-Z0-9]/.test(pw)) score++
  if (score <= 2) return 'weak'
  if (score <= 4) return 'medium'
  return 'strong'
})

const strengthText = computed(() => {
  if (strengthClass.value === 'weak') return '弱'
  if (strengthClass.value === 'medium') return '中'
  if (strengthClass.value === 'strong') return '强'
  return ''
})

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password,
    })
    ElMessage.success('注册成功')
    router.push('/')
  } catch (error: any) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 409) {
      ElMessage.error(detail || '用户名或邮箱已存在')
    } else if (status === 422) {
      ElMessage.error(detail || '密码强度不足')
    } else {
      ElMessage.error(detail || '注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  display: flex;
  width: 800px;
  min-height: 560px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.register-brand {
  flex: 1;
  background: linear-gradient(135deg, #aa3bff 0%, #6c5ce7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.brand-content {
  text-align: center;
  color: #fff;
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin: 0;
}

.register-form-section {
  flex: 1;
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px 0;
}

.register-button {
  width: 100%;
}

.password-strength {
  margin-top: 4px;
  font-size: 12px;
}

.strength-label {
  color: #909399;
}

.strength-text.weak {
  color: #f56c6c;
}

.strength-text.medium {
  color: #e6a23c;
}

.strength-text.strong {
  color: #67c23a;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}

.link {
  color: #aa3bff;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-card {
    flex-direction: column;
    width: 100%;
    max-width: 400px;
  }
  .register-brand {
    padding: 24px;
    min-height: auto;
  }
  .brand-title {
    font-size: 24px;
  }
  .register-form-section {
    padding: 32px 24px;
  }
}
</style>
