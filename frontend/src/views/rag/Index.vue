<template>
  <div class="rag-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="goHome">校园AI助手</h1>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>
    <main class="main">
      <div class="placeholder-page">
        <div class="icon">📚</div>
        <h2>RAG 知识检索</h2>
        <p>此功能正在开发中...</p>
        <button class="btn-primary" @click="goHome">返回首页</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

const goHome = () => {
  router.push('/home')
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.rag-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.logo {
  font-size: 18px;
  font-weight: 600;
  color: #2C68FF;
  cursor: pointer;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  font-size: 14px;
  color: #4E5969;
}

.logout-btn {
  padding: 8px 20px;
  background: rgba(44, 104, 255, 0.1);
  color: #2C68FF;
  border: 1px solid rgba(44, 104, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(44, 104, 255, 0.2);
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px;
}

.placeholder-page {
  text-align: center;
  background: white;
  padding: 80px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.placeholder-page .icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.placeholder-page h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 12px;
}

.placeholder-page p {
  color: #666;
  font-size: 16px;
  margin-bottom: 32px;
}

.btn-primary {
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}
</style>
