<template>
  <div class="home-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">校园AI助手</h1>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>
    <main class="main">
      <div class="welcome-card">
        <h2>欢迎使用校园AI助手</h2>
        <p class="subtitle">你的智能校园生活伙伴</p>
      </div>
      <div class="modules-grid">
        <div class="module-card" @click="goToRag">
          <div class="module-icon">📚</div>
          <h3>RAG知识检索</h3>
          <p>校园信息智能问答</p>
        </div>
        <div class="module-card" @click="goToContest">
          <div class="module-icon">🏆</div>
          <h3>赛事推荐与组队</h3>
          <p>智能匹配，高效协作</p>
        </div>
        <div class="module-card" @click="goToMap">
          <div class="module-icon">🗺️</div>
          <h3>智慧地图</h3>
          <p>AR导航，轻松找路</p>
        </div>
        <div class="module-card" @click="goToForum">
          <div class="module-icon">💬</div>
          <h3>校园论坛</h3>
          <p>畅所欲言，交流分享</p>
        </div>
      </div>
      <div class="user-profile">
        <h3>我的信息</h3>
        <div class="profile-item">
          <span class="label">学号/工号：</span>
          <span class="value">{{ userStore.userId }}</span>
        </div>
        <div class="profile-item">
          <span class="label">角色：</span>
          <span class="value">{{ userStore.role === 'student' ? '学生' : userStore.role === 'teacher' ? '教师' : '管理员' }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}

const goToContest = () => {
  router.push('/contest')
}

const goToRag = () => {
  router.push('/rag')
}

const goToMap = () => {
  router.push('/map')
}

const goToForum = () => {
  router.push('/forum')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  font-size: 16px;
}

.logout-btn {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.welcome-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  text-align: center;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.welcome-card h2 {
  color: #333;
  font-size: 28px;
  margin-bottom: 8px;
}

.welcome-card .subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.module-card {
  background: white;
  padding: 32px 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.module-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.module-card h3 {
  color: #333;
  font-size: 18px;
  margin-bottom: 8px;
}

.module-card p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.user-profile {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.user-profile h3 {
  color: #333;
  font-size: 18px;
  margin-bottom: 20px;
}

.profile-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.profile-item:last-child {
  border-bottom: none;
}

.profile-item .label {
  color: #666;
  width: 100px;
}

.profile-item .value {
  color: #333;
  font-weight: 500;
}
</style>
