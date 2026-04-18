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
      console.log('userStore.login 被调用, loginData:', loginData)
      const res = await login(loginData)
      console.log('login API 返回:', res)
      this.token = res.access_token
      this.refreshToken = res.refresh_token
      setToken(res.access_token)
      setRefreshToken(res.refresh_token)
      console.log('Token 已保存, 准备获取用户信息...')
      await this.fetchUserInfo()
      console.log('用户信息获取完成')
      return res
    },

    async register(registerData) {
      const res = await register(registerData)
      return res
    },

    async fetchUserInfo() {
      console.log('fetchUserInfo 被调用...')
      const res = await getCurrentUser()
      console.log('getCurrentUser 返回:', res)
      this.userInfo = res
      setUserInfo(res)
      console.log('用户信息已保存:', this.userInfo)
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
