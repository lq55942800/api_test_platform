import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/environments',
    },
    {
      path: '/environments',
      name: 'environments',
      component: () => import('@/views/environment/EnvironmentList.vue'),
    },
    {
      path: '/apis',
      name: 'apis',
      component: () => import('@/views/api/ApiList.vue'),
    },
    {
      path: '/testcases',
      name: 'testcases',
      component: () => import('@/views/testcase/TestCaseList.vue'),
    },
  ],
})

export default router