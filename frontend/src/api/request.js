import axios from 'axios'
import { getToken, removeToken, clearAuth } from '@/utils/auth'
import { useUserStore } from '@/store/modules/user'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    if (error.response?.status === 401) {
      clearAuth()
      const userStore = useUserStore()
      userStore.clearUser()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default request
