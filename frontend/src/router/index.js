import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/home/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/contest',
    name: 'Contest',
    component: () => import('@/views/contest/TeamHall.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/contest/:id',
    name: 'ContestDetail',
    component: () => import('@/views/contest/ContestDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rag',
    name: 'Rag',
    component: () => import('@/views/rag/Index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('@/views/map/Index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/forum',
    name: 'Forum',
    component: () => import('@/views/forum/Index.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/home')
  } else {
    next()
  }
})

export default router
