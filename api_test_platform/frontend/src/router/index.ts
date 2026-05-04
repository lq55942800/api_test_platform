import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册', public: true }
  },
  {
    path: '/',
    component: () => import('@/views/layout/AppLayout.vue'),
    redirect: '/environments',
    children: [
      {
        path: 'environments',
        name: 'EnvironmentList',
        component: () => import('@/views/environment/EnvironmentList.vue'),
        meta: { title: '环境管理' }
      },
      {
        path: 'environments/new',
        name: 'EnvironmentCreate',
        component: () => import('@/views/environment/EnvironmentEdit.vue'),
        meta: { title: '新建环境' }
      },
      {
        path: 'environments/:id/edit',
        name: 'EnvironmentEdit',
        component: () => import('@/views/environment/EnvironmentEdit.vue'),
        meta: { title: '编辑环境' }
      },
      {
        path: 'environments/:id',
        name: 'EnvironmentDetail',
        component: () => import('@/views/environment/EnvironmentDetail.vue'),
        meta: { title: '环境详情' }
      },
      {
        path: 'environments/:envId/services/new',
        name: 'ServiceCreate',
        component: () => import('@/views/environment/ServiceConfig.vue'),
        meta: { title: '新建服务' }
      },
      {
        path: 'environments/:envId/services/:serviceId/edit',
        name: 'ServiceEdit',
        component: () => import('@/views/environment/ServiceConfig.vue'),
        meta: { title: '编辑服务' }
      },
      {
        path: 'apis',
        name: 'ApiList',
        component: () => import('@/views/api/ApiList.vue'),
        meta: { title: '接口管理' }
      },
      {
        path: 'apis/:id',
        name: 'ApiDetail',
        component: () => import('@/views/api/ApiDetail.vue'),
        meta: { title: '接口详情' }
      },
      {
        path: 'testcase',
        name: 'TestCaseList',
        component: () => import('@/views/testcase/TestCaseList.vue'),
        meta: { title: '测试用例' }
      },
      {
        path: 'testcase/create',
        name: 'TestCaseCreate',
        component: () => import('@/views/testcase/TestCaseDetail.vue'),
        meta: { title: '新建测试用例' }
      },
      {
        path: 'testcase/:id',
        name: 'TestCaseDetail',
        component: () => import('@/views/testcase/TestCaseDetail.vue'),
        meta: { title: '测试用例详情' }
      },
      {
        path: 'testcase/:id/edit',
        name: 'TestCaseEdit',
        component: () => import('@/views/testcase/TestCaseDetail.vue'),
        meta: { title: '编辑测试用例' }
      },
      {
        path: 'execution/:id',
        name: 'ExecutionDetail',
        component: () => import('@/views/testcase/ExecutionDetail.vue'),
        meta: { title: '执行详情' }
      },
      {
        path: 'admin/teams',
        name: 'TeamManagement',
        component: () => import('@/views/admin/TeamManagement.vue'),
        meta: { title: '团队管理' }
      },
      {
        path: 'admin/users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { title: '用户管理' }
      },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { title: '页面不存在', public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let authInitialized = false

router.beforeEach(async (to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - AutoTest`
  }

  const authStore = useAuthStore()

  if (!authInitialized) {
    authInitialized = true
    const storedToken = localStorage.getItem('autotest_token')
    if (storedToken) {
      await authStore.initAuth()
    }
  }

  const isPublicRoute = to.meta.public === true

  if (isPublicRoute) {
    if (authStore.isAuthenticated) {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    if (!authStore.isAuthenticated) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  }
})

export default router
