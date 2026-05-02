import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/environments'
  },
  {
    path: '/environments',
    name: 'EnvironmentList',
    component: () => import('@/views/environment/EnvironmentList.vue'),
    meta: {
      title: '环境管理'
    }
  },
  {
    path: '/environments/new',
    name: 'EnvironmentCreate',
    component: () => import('@/views/environment/EnvironmentEdit.vue'),
    meta: {
      title: '新建环境'
    }
  },
  {
    path: '/environments/:id/edit',
    name: 'EnvironmentEdit',
    component: () => import('@/views/environment/EnvironmentEdit.vue'),
    meta: {
      title: '编辑环境'
    }
  },
  {
    path: '/environments/:id',
    name: 'EnvironmentDetail',
    component: () => import('@/views/environment/EnvironmentDetail.vue'),
    meta: {
      title: '环境详情'
    }
  },
  {
    path: '/environments/:envId/services/new',
    name: 'ServiceCreate',
    component: () => import('@/views/environment/ServiceConfig.vue'),
    meta: {
      title: '新建服务'
    }
  },
  {
    path: '/environments/:envId/services/:serviceId/edit',
    name: 'ServiceEdit',
    component: () => import('@/views/environment/ServiceConfig.vue'),
    meta: {
      title: '编辑服务'
    }
  },
  {
    path: '/apis',
    name: 'ApiList',
    component: () => import('@/views/api/ApiList.vue'),
    meta: {
      title: '接口管理'
    }
  },
  {
    path: '/apis/:id',
    name: 'ApiDetail',
    component: () => import('@/views/api/ApiDetail.vue'),
    meta: {
      title: '接口详情'
    }
  },
  {
    path: '/testcase',
    name: 'TestCaseList',
    component: () => import('@/views/testcase/TestCaseList.vue'),
    meta: {
      title: '测试用例管理'
    }
  },
  {
    path: '/testcase/create',
    name: 'TestCaseCreate',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '新建测试用例'
    }
  },
  {
    path: '/testcase/:id',
    name: 'TestCaseDetail',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '测试用例详情'
    }
  },
  {
    path: '/testcase/:id/edit',
    name: 'TestCaseEdit',
    component: () => import('@/views/testcase/TestCaseDetail.vue'),
    meta: {
      title: '编辑测试用例'
    }
  },
  {
    path: '/execution/:id',
    name: 'ExecutionDetail',
    component: () => import('@/views/testcase/ExecutionDetail.vue'),
    meta: {
      title: '执行详情'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - AutoTest`
  }
  next()
})

export default router
