import { defineStore } from 'pinia'
import { login, register, getCurrentUser, logout as logoutApi } from '@/api/auth'
import { setToken, setRefreshToken, setUserInfo, clearAuth, getToken, getRefreshToken, getUserInfo } from '@/utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    refreshToken: getRefreshToken() || '',
    userInfo: getUserInfo() || null
  }),

  getters: {
    isLoggedIn: state => !!state.token,
    username: state => state.userInfo?.username || '',
    userId: state => state.userInfo?.id || '',
    role: state => state.userInfo?.role || 'student'
  },

  actions: {
    async login(loginData) {
      const res = await login(loginData)
      this.token = res.access_token
      this.refreshToken = res.refresh_token
      setToken(res.access_token)
      setRefreshToken(res.refresh_token)
      await this.fetchUserInfo()
      return res
    },

    async register(registerData) {
      const res = await register(registerData)
      return res
    },

    async fetchUserInfo() {
      const res = await getCurrentUser()
      this.userInfo = res
      setUserInfo(res)
      return res
    },

    async logout() {
      try {
        await logoutApi()
      } catch (error) {
        console.error('Logout API error:', error)
      } finally {
        this.clearUser()
        clearAuth()
      }
    },

    clearUser() {
      this.token = ''
      this.refreshToken = ''
      this.userInfo = null
    },

    updateUserInfo(info) {
      this.userInfo = { ...this.userInfo, ...info }
      setUserInfo(this.userInfo)
    }
  }
})
