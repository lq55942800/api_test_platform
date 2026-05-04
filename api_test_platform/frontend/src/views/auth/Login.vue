<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-brand">
        <div class="brand-content">
          <h1 class="brand-title">AutoTest API</h1>
          <p class="brand-subtitle">企业级API测试平台</p>
        </div>
      </div>
      <div class="login-form-section">
        <h2 class="form-title">登录</h2>
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
              size="large"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          还没有账号？<router-link to="/register" class="link">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login({ username: form.username, password: form.password })
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error: any) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 423) {
      ElMessage.error(detail || '账号已锁定，请稍后重试')
    } else if (status === 401) {
      ElMessage.error(detail || '用户名或密码错误')
    } else {
      ElMessage.error(detail || '登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  display: flex;
  width: 800px;
  min-height: 480px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.login-brand {
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

.login-form-section {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 32px 0;
}

.login-button {
  width: 100%;
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
  .login-card {
    flex-direction: column;
    width: 100%;
    max-width: 400px;
  }
  .login-brand {
    padding: 24px;
    min-height: auto;
  }
  .brand-title {
    font-size: 24px;
  }
  .login-form-section {
    padding: 32px 24px;
  }
}
</style>
